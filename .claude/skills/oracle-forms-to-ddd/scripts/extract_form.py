#!/usr/bin/env python3
"""
extract_form.py — Parser of an exported Oracle Forms file (.fmb dumped to text).

Extracts the structural facts needed to build a DDD domain model:
  - Data blocks (bloques de datos) and whether each is a database block
  - Each block's query source / DML target (table or embedded SELECT)
  - Each block's items (columns): name, item type, max length, datatype,
    whether it is a database item, and the underlying column name
  - Program units and packages (names + types)
  - Triggers at form and block level

It deliberately does NOT decide aggregates/entities/value objects — that
classification is a modeling judgment made by Claude using SKILL.md. This
script only produces the raw, reliable inventory.

Usage:
    python3 extract_form.py <form_file> [--json]

The input file is often ISO-8859-1 (Latin-1). Encoding is auto-detected with a
Latin-1 fallback so accented Spanish labels parse correctly.

Output (default): a human-readable report.
Output (--json):  a machine-readable JSON inventory for further processing.
"""
import sys
import re
import json
import argparse


# Labels are emitted by the Forms export in Spanish. Map the ones we care about.
LBL_NAME = "Nombre"
LBL_ITEM_TYPE = "Tipo de Elemento"
LBL_MAXLEN = "Longitud Máxima"
LBL_DTYPE = "Tipo de Datos"
LBL_DB_ITEM = "Elemento de Base de Datos"
LBL_COLUMN = "Nombre de Columna"
LBL_REQUIRED = "Requerido"
LBL_DB_BLOCK = "Bloque de Datos de Base de Datos"
LBL_QUERY_SRC = "Nombre del Origen de Datos de Consulta"
LBL_DML_TGT = "Nombre Destino de Datos DML"
LBL_NAV_STYLE = "Estilo de Navegación"          # block-only property → anchors a block
LBL_PU_TYPE = "Tipo de Unidad de Programa"
LBL_TRIGGER_STYLE = "Estilo de Disparador"      # trigger-only property

# Item types that carry data (vs. buttons, rectangles, etc.)
DATA_ITEM_TYPES = {
    "Elemento de Texto",
    "Visualizar Elemento",
    "Elemento de Lista",
    "Casilla de Control",
    "Grupo de Botones de Radio",
}

LINE_RE = re.compile(r'^(\s*)([\*\-\^o])\s+(.+?)(?:\s{2,}(.*))?$')


def read_lines(path):
    """Read file trying UTF-8 then Latin-1 (Forms exports are usually Latin-1)."""
    for enc in ("utf-8", "iso-8859-1"):
        try:
            with open(path, encoding=enc) as f:
                return [l.rstrip("\n") for l in f]
        except UnicodeDecodeError:
            continue
    # last resort: replace bad bytes
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f]


def parse_line(line):
    """Return (indent, label, value) or None for a Forms property line."""
    m = LINE_RE.match(line)
    if not m:
        return None
    return len(m.group(1)), m.group(3).strip(), (m.group(4) or "").strip()


def find_name_lines(lines):
    out = []
    for i, l in enumerate(lines):
        p = parse_line(l)
        if p and p[1] == LBL_NAME:
            out.append((i, p[0], p[2]))
    return out


def find_blocks(lines, name_lines):
    """
    A data block is a '* Nombre <X>' at the block indent (3) whose following
    window contains the block-only property 'Estilo de Navegación'.
    Returns list of (start_line_index, block_name).
    """
    blocks = []
    for i, ind, nm in name_lines:
        if ind == 3:
            window = "\n".join(lines[i:i + 20])
            if LBL_NAV_STYLE in window:
                blocks.append((i, nm))
    return blocks


def block_property(seg, label):
    """First value of a property within a block segment (top-level props)."""
    for ln in seg:
        p = parse_line(ln)
        if p and p[1] == label and p[2]:
            return p[2]
    return ""


def extract_items(seg):
    """
    Extract data-bearing items from a block segment. Items are sub-records that
    have a 'Tipo de Elemento' property. We accumulate properties under the most
    recent 'Nombre' and keep only those whose item type is a data type.
    """
    items = []
    cur = None
    for ln in seg:
        p = parse_line(ln)
        if not p:
            continue
        ind, lab, v = p
        if lab == LBL_NAME and ind >= 5:
            if cur and cur.get("item_type"):
                items.append(cur)
            cur = {"name": v}
        elif cur is not None:
            if lab == LBL_ITEM_TYPE:
                cur["item_type"] = v
            elif lab == LBL_MAXLEN:
                cur["max_len"] = v
            elif lab == LBL_DTYPE:
                cur["datatype"] = v
            elif lab == LBL_DB_ITEM:
                cur["db_item"] = v
            elif lab == LBL_COLUMN:
                cur["column"] = v
            elif lab == LBL_REQUIRED:
                cur["required"] = v
    if cur and cur.get("item_type"):
        items.append(cur)
    # keep only data-bearing items
    return [it for it in items if it.get("item_type") in DATA_ITEM_TYPES]


def extract_program_units(lines):
    """
    Program units / packages: name + type.

    The export prints the unit NAME, then its (possibly long) PL/SQL body, then
    the 'Tipo de Unidad de Programa' line. So we scope to the 'Unidades de
    Programa' section and pair each unit '* Nombre' with the next type line.
    """
    units = []
    # locate section start
    sec_start = None
    for i, l in enumerate(lines):
        p = parse_line(l)
        if p and p[1] == "Unidades de Programa":
            sec_start = i
            break
    if sec_start is None:
        return units

    pending = None
    for l in lines[sec_start + 1:]:
        p = parse_line(l)
        if not p:
            continue
        ind, lab, v = p
        if lab == LBL_NAME and ind == 3:
            pending = v
        elif lab == LBL_PU_TYPE and pending is not None:
            units.append({"name": pending, "type": v})
            pending = None
    return units


def extract_tables_from_sql(sql):
    """Best-effort table extraction from an embedded SELECT (for relations)."""
    if not sql:
        return []
    tabs = re.findall(r'\bFROM\s+(.+?)(?:\bWHERE\b|$)', sql, flags=re.IGNORECASE | re.DOTALL)
    found = []
    for chunk in tabs:
        for part in chunk.split(","):
            tok = part.strip().split()
            if tok:
                t = tok[0].strip()
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', t):
                    found.append(t.upper())
    # dedupe preserving order
    seen, out = set(), []
    for t in found:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def extract(path):
    lines = read_lines(path)
    name_lines = find_name_lines(lines)
    blocks = find_blocks(lines, name_lines)

    result = {"form": path, "blocks": [], "program_units": []}

    for bi, (start, nm) in enumerate(blocks):
        end = blocks[bi + 1][0] if bi + 1 < len(blocks) else len(lines)
        seg = lines[start:end]
        is_db = block_property(seg, LBL_DB_BLOCK)
        qsrc = block_property(seg, LBL_QUERY_SRC)
        dml = block_property(seg, LBL_DML_TGT)
        items = extract_items(seg)
        block = {
            "name": nm,
            "is_db_block": is_db,                 # 'Sí' / 'No'
            "query_source": qsrc,                 # table name or SELECT ...
            "dml_target": dml,                    # table name
            "embedded_tables": extract_tables_from_sql(qsrc),
            "items": items,
        }
        result["blocks"].append(block)

    result["program_units"] = extract_program_units(lines)
    return result


def print_report(data):
    print(f"# Inventario del formulario: {data['form']}\n")
    db_blocks = [b for b in data["blocks"] if b["is_db_block"] == "Sí"]
    ctrl_blocks = [b for b in data["blocks"] if b["is_db_block"] != "Sí"]

    print(f"## Bloques de datos de BD (candidatos a Entidad/Agregado): {len(db_blocks)}\n")
    for b in db_blocks:
        src = b["query_source"][:70] + ("…" if len(b["query_source"]) > 70 else "")
        print(f"### {b['name']}")
        print(f"   origen consulta : {src or '(ninguno)'}")
        print(f"   destino DML     : {b['dml_target'] or '(ninguno)'}")
        if b["embedded_tables"]:
            print(f"   tablas en SELECT: {', '.join(b['embedded_tables'])}")
        print(f"   columnas ({len(b['items'])}):")
        for it in b["items"]:
            print("     {name:26} {item_type:24} dt={dt:8} len={ln:5} db={db:3} col={col}".format(
                name=it.get("name", ""),
                item_type=it.get("item_type", ""),
                dt=it.get("datatype", "") or "-",
                ln=it.get("max_len", "") or "-",
                db=it.get("db_item", "-"),
                col=it.get("column", "") or "-",
            ))
        print()

    print(f"## Bloques de control (NO BD → capa Controller/Vista): {len(ctrl_blocks)}")
    print("   " + ", ".join(b["name"] for b in ctrl_blocks) + "\n")

    print(f"## Unidades de Programa / Paquetes (→ Service): {len(data['program_units'])}")
    for u in data["program_units"]:
        print(f"   {u['name']:30} {u['type']}")


def main():
    ap = argparse.ArgumentParser(description="Extract structure from an exported Oracle Form.")
    ap.add_argument("form_file", help="Path to the exported .fmb text file")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a report")
    args = ap.parse_args()

    data = extract(args.form_file)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
