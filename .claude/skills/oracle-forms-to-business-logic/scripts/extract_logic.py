#!/usr/bin/env python3
"""
extract_logic.py — Extract the BUSINESS LOGIC of an exported Oracle Form.

Where extract_form.py (skill oracle-forms-to-ddd) inventories the *structure*
(blocks, columns, program units), this script pulls out the *behaviour*: every
trigger's PL/SQL body, attributed to its owning block and item, plus the
database packages/procedures each block invokes and the :BLOCK.ITEM fields it
references. This is the raw material for one-markdown-per-form business-logic
extraction.

It deliberately does NOT decide which blocks are "user-input forms" nor write
the markdown — that judgment and prose belong to Claude via SKILL.md. This
script only produces the reliable, deterministic inventory of trigger code.

Usage:
    python3 extract_logic.py <form_file>                 # human-readable report
    python3 extract_logic.py <form_file> --list          # one line per block
    python3 extract_logic.py <form_file> --json          # full JSON (all blocks)
    python3 extract_logic.py <form_file> --block NAME     # only that block
    python3 extract_logic.py <form_file> --block NAME --json

The input file is usually ISO-8859-1 (Latin-1). Encoding is auto-detected with a
Latin-1 fallback so accented Spanish labels parse correctly. Trigger bodies are
emitted verbatim (accents preserved) — do not "fix" them, they are source code.
"""
import sys
import re
import json
import argparse


# --- Forms export labels (Spanish) -----------------------------------------
LBL_NAME = "Nombre"
LBL_ITEM_TYPE = "Tipo de Elemento"
LBL_NAV_STYLE = "Estilo de Navegación"          # block-only property → anchors a block
LBL_DB_BLOCK = "Bloque de Datos de Base de Datos"
LBL_TRIGGER_STYLE = "Estilo de Disparador"
LBL_TRIGGER_TEXT = "Texto del Disparador"

# The first property emitted AFTER a trigger body. Primary end-of-body sentinel.
LBL_TRIGGER_TAIL = "Activar en Modo Introducir Consulta"
# Any of these appearing (parsed as a property) also ends a body, as a fallback.
TRIGGER_TAIL_LABELS = {
    LBL_TRIGGER_TAIL,
    "Jerarquía de Ejecución",
    "Visualizar en 'Ayuda del Teclado'",
    "Texto de la Ayuda del Teclado'",
    "Pasos de Disparador",
}

LINE_RE = re.compile(r'^(\s*)([\*\-\^o])\s+(.+?)(?:\s{2,}(.*))?$')

# Package / procedure call detection inside PL/SQL bodies.
PKG_CALL_RE = re.compile(r'\b([A-Z][A-Z0-9_]*_PKG)\s*\.\s*([A-Z0-9_]+)', re.IGNORECASE)
PROC_CALL_RE = re.compile(r'\b([A-Z][A-Z0-9_]*)\s*\.\s*([A-Z0-9_]+)\s*\(', re.IGNORECASE)
FIELD_REF_RE = re.compile(r':([A-Z][A-Z0-9_]*)\.([A-Z0-9_]+)', re.IGNORECASE)


def read_lines(path):
    """Read file trying UTF-8 then Latin-1 (Forms exports are usually Latin-1)."""
    for enc in ("utf-8", "iso-8859-1"):
        try:
            with open(path, encoding=enc) as f:
                return [l.rstrip("\n") for l in f]
        except UnicodeDecodeError:
            continue
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f]


def parse_line(line):
    """Return (indent, label, value) or None for a Forms property line."""
    m = LINE_RE.match(line)
    if not m:
        return None
    return len(m.group(1)), m.group(3).strip(), (m.group(4) or "").strip()


def find_blocks(lines):
    """
    A data block is a '* Nombre <X>' at block indent (3) whose following window
    contains the block-only property 'Estilo de Navegación'.
    Returns list of (start_line_index, block_name).
    """
    blocks = []
    for i, l in enumerate(lines):
        p = parse_line(l)
        if p and p[1] == LBL_NAME and p[0] == 3:
            window = "\n".join(lines[i:i + 20])
            if LBL_NAV_STYLE in window:
                blocks.append((i, p[2]))
    return blocks


def block_property(seg, label, indent=None):
    """First value of a property within a block segment."""
    for ln in seg:
        p = parse_line(ln)
        if p and p[1] == label and p[2] and (indent is None or p[0] == indent):
            return p[2]
    return ""


def extract_triggers(seg, seg_start):
    """
    Extract every trigger in a block segment: name, owner (block/item), style
    and full PL/SQL body. `seg` is the list of lines for one block; `seg_start`
    is its absolute start index (so line numbers are absolute in the file).

    Attribution rule (validated on real exports):
      - item-level trigger  → its '* Nombre' sits at indent >= 7; owner is the
        nearest preceding indent-5 item name.
      - block-level trigger → its '* Nombre' sits at indent 5; owner is the block.
    The body is every line after 'Texto del Disparador' up to the first
    subsequent property line (the trigger tail metadata).
    """
    triggers = []
    current_item = None
    last_name = None          # (indent, value)
    n = len(seg)
    i = 0
    while i < n:
        p = parse_line(seg[i])
        if p:
            ind, lab, val = p
            if lab == LBL_NAME:
                last_name = (ind, val)
                # track the most recent item (indent-5 name with a Tipo de Elemento nearby)
                if ind == 5:
                    lookahead = "\n".join(seg[i:i + 6])
                    if LBL_ITEM_TYPE in lookahead:
                        current_item = val
            elif lab == LBL_TRIGGER_TEXT:
                trig_name = last_name[1] if last_name else "(desconocido)"
                trig_indent = last_name[0] if last_name else 0
                owner = current_item if trig_indent >= 7 else "(bloque)"
                # capture body: lines after this one until the tail property
                body_lines = []
                j = i + 1
                while j < n:
                    q = parse_line(seg[j])
                    if q and (q[1] in TRIGGER_TAIL_LABELS or q[1] == LBL_NAME
                              or q[1] == LBL_TRIGGER_STYLE):
                        break
                    body_lines.append(seg[j])
                    j += 1
                body = "\n".join(body_lines).strip("\n")
                # trim leading/trailing blank lines but preserve inner spacing
                body = re.sub(r'^\s*\n', '', body)
                body = body.rstrip()
                triggers.append({
                    "name": trig_name,
                    "owner": owner,
                    "level": "item" if trig_indent >= 7 else "block",
                    "line": seg_start + i + 1,   # 1-based absolute line of the text marker
                    "body": body,
                })
                i = j
                continue
        i += 1
    return triggers


def collect_calls(triggers):
    """Aggregate package calls, standalone proc calls and field refs across bodies."""
    pkg = {}
    procs = set()
    fields = set()
    for t in triggers:
        b = t["body"]
        for m in PKG_CALL_RE.finditer(b):
            key = f"{m.group(1).upper()}.{m.group(2).upper()}"
            pkg.setdefault(key, 0)
            pkg[key] += 1
        for m in PROC_CALL_RE.finditer(b):
            name = f"{m.group(1).upper()}.{m.group(2).upper()}"
            if "_PKG." not in name:              # already captured above
                procs.add(name)
        for m in FIELD_REF_RE.finditer(b):
            fields.add(f":{m.group(1).upper()}.{m.group(2).upper()}")
    return {
        "packages": sorted(pkg.keys()),
        "procedures": sorted(procs),
        "fields": sorted(fields),
    }


def extract(path, only_block=None):
    lines = read_lines(path)
    blocks = find_blocks(lines)
    form_name = block_property(lines[:60], LBL_NAME, indent=1) or path

    out = {"form": form_name, "file": path, "blocks": []}
    for bi, (start, nm) in enumerate(blocks):
        if only_block and nm.upper() != only_block.upper():
            continue
        end = blocks[bi + 1][0] if bi + 1 < len(blocks) else len(lines)
        seg = lines[start:end]
        is_db = block_property(seg, LBL_DB_BLOCK)
        triggers = extract_triggers(seg, start)
        calls = collect_calls(triggers)
        out["blocks"].append({
            "name": nm,
            "is_db_block": is_db,                # 'Sí' / 'No'
            "start_line": start + 1,
            "end_line": end,
            "trigger_count": len(triggers),
            "triggers": triggers,
            "packages": calls["packages"],
            "procedures": calls["procedures"],
            "fields": calls["fields"],
        })
    return out


# --- output ------------------------------------------------------------------
def print_list(data):
    print(f"# {data['form']}  ({len(data['blocks'])} bloques)\n")
    print(f"{'BLOQUE':28} {'BD':4} {'DISP':5} {'LÍNEAS':13} PAQUETES")
    for b in data["blocks"]:
        pk = ", ".join(p.split(".")[0] for p in b["packages"])
        pk = ", ".join(sorted(set(pk.split(", ")))) if pk else "-"
        print("{name:28} {db:4} {tc:<5} {rng:13} {pk}".format(
            name=b["name"], db=b["is_db_block"] or "-", tc=b["trigger_count"],
            rng=f"{b['start_line']}-{b['end_line']}", pk=pk))


def print_report(data):
    print(f"# Lógica de negocio: {data['form']}\n")
    for b in data["blocks"]:
        print(f"## Bloque {b['name']}  (BD={b['is_db_block'] or '-'}, "
              f"líneas {b['start_line']}-{b['end_line']}, {b['trigger_count']} disparadores)")
        if b["packages"]:
            print(f"   paquetes  : {', '.join(b['packages'])}")
        if b["procedures"]:
            print(f"   procs     : {', '.join(b['procedures'])}")
        print()
        for t in b["triggers"]:
            owner = t["owner"] if t["level"] == "item" else "(nivel bloque)"
            print(f"   -- {t['name']}  [{owner}]  (línea {t['line']})")
            for ln in t["body"].splitlines():
                print(f"      {ln}")
            print()


def main():
    # Windows consoles default to cp1252 and choke on accented/box characters.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Extract business logic (triggers) from an exported Oracle Form.")
    ap.add_argument("form_file", help="Path to the exported .fmb text file")
    ap.add_argument("--block", help="Only this block (by name)")
    ap.add_argument("--list", action="store_true", help="One-line summary per block")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    data = extract(args.form_file, only_block=args.block)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.list:
        print_list(data)
    else:
        print_report(data)


if __name__ == "__main__":
    main()
