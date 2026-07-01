#!/usr/bin/env python3
"""
oracle_wireframe.py - Reconstruye la UI de un Oracle Form exportado a texto
(.fmb volcado) como un WIREFRAME HTML interactivo autocontenido.

El export es un arbol de propiedades indentado, normalmente en Latin-1 y en
espanol. Este script:

  1) Parsea la GEOMETRIA de la interfaz: ventanas, lienzos (content / barra de
     herramientas / pestana), marcos (frames), paginas de pestana e items de
     pantalla con su posicion (X/Y), tamano (Ancho/Alto), tipo, prompt y lienzo.
  2) Genera un unico fichero .html interactivo: barra de herramientas comun,
     navegacion entre pantallas (una por lienzo), pestanas clicables, rejillas
     para bloques multi-registro y botonera con feedback.

No decide arquitectura ni capas Java: solo reconstruye la pantalla tal como el
Form la dibuja, para poder VERLA y valorar la viabilidad del traspaso.

Uso:
    python3 oracle_wireframe.py inspect <form.txt> [--json]
    python3 oracle_wireframe.py build   <form.txt> [-o <salida.html>]

Si se omite -o, escribe junto al form: <dir>/<NOMBRE>_wireframe.html
"""
import sys
import re
import json
import html
import argparse
import os

LINE_RE = re.compile(r'^(\s*)([\*\-\^o])\s+(.+?)(?:\s{2,}(.*))?$')

# --- etiquetas del export (espanol). Acentos incluidos tal cual aparecen. ---
NAME       = "Nombre"
ITEM_TYPE  = "Tipo de Elemento"
CANVAS     = "Lienzo"
PAGE       = "Página con Pestaña"
POS_X      = "Posición X"
POS_Y      = "Posición Y"
WIDTH      = "Ancho"
HEIGHT     = "Altura"
PROMPT     = "Prompt"
VISIBLE    = "Visible"
DISP_COUNT = "Número de Elementos Visualizados"
DB_ITEM    = "Elemento de Base de Datos"
CANVAS_KIND= "Tipo de Lienzo"
WINDOW     = "Ventana"
TITLE      = "Título"
GTYPE      = "Tipo de Gráficos"
FRAME_TTL  = "Título del Marco"
TAB_LABEL  = "Etiqueta"
TABS_HDR   = "Páginas con Pestaña"

# secciones de primer nivel (indent 1) que cierran la lista de bloques/items
SECTION_LABELS = {
    "Alertas", "Disparadores", "Unidades de Programa", "Lienzos",
    "Grupos de Registros", "Atributos Visuales", "Ventanas",
    "Listas de Valores", "Editores", "Parámetros",
}

# tipo de item -> familia de widget
def widget_family(item_type):
    t = (item_type or "").lower()
    if "botón" in t or "boton" in t:            return "button"
    if "casilla" in t:                                return "check"
    if "radio" in t:                                  return "radio"
    if "lista" in t:                                  return "list"
    if "visualizar" in t:                             return "display"
    if "imagen" in t:                                 return "image"
    if "texto" in t or "elemento de texto" in t:      return "text"
    return "text"


def read_lines(path):
    for enc in ("utf-8", "iso-8859-1"):
        try:
            with open(path, encoding=enc) as f:
                return [l.rstrip("\n") for l in f]
        except UnicodeDecodeError:
            continue
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\n") for l in f]


def parse_line(line):
    m = LINE_RE.match(line)
    if not m:
        return None
    return len(m.group(1)), m.group(3).strip(), (m.group(4) or "").strip()


def to_int(v, default=0):
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return default


# --------------------------------------------------------------------------
# parseo
# --------------------------------------------------------------------------
def section_bounds(lines, label):
    """(start, end) del bloque de una seccion de primer nivel, o None."""
    start = None
    for i, l in enumerate(lines):
        p = parse_line(l)
        if p and p[0] == 1 and p[1] == label:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        p = parse_line(lines[i])
        if p and p[0] == 1 and p[1] in SECTION_LABELS:
            end = i
            break
    return start, end


def form_title(lines):
    for l in lines[:60]:
        p = parse_line(l)
        if p and p[0] == 1 and p[1] == TITLE and p[2]:
            return p[2]
    return ""


def parse_items(lines, end):
    """Items de pantalla (los que tienen 'Tipo de Elemento')."""
    items = []
    cur = None

    def flush():
        if cur and cur.get("type"):
            items.append(cur)

    for l in lines[:end]:
        p = parse_line(l)
        if not p:
            continue
        ind, lab, v = p
        if lab == NAME and ind == 5:
            flush()
            cur = {"name": v, "x": 0, "y": 0, "w": 0, "h": 0,
                   "prompt": "", "canvas": "", "page": "",
                   "visible": "Sí", "disp": 1, "db": ""}
            cur["_seen"] = set()
        elif cur is not None:
            s = cur["_seen"]
            if lab == ITEM_TYPE and "type" not in s:
                cur["type"] = v; s.add("type")
            elif lab == CANVAS and "canvas" not in s:
                cur["canvas"] = v; s.add("canvas")
            elif lab == PAGE and "page" not in s:
                cur["page"] = v; s.add("page")
            elif lab == POS_X and "x" not in s:
                cur["x"] = to_int(v); s.add("x")
            elif lab == POS_Y and "y" not in s:
                cur["y"] = to_int(v); s.add("y")
            elif lab == WIDTH and "w" not in s:
                cur["w"] = to_int(v); s.add("w")
            elif lab == HEIGHT and "h" not in s:
                cur["h"] = to_int(v); s.add("h")
            elif lab == PROMPT and "prompt" not in s:
                cur["prompt"] = v; s.add("prompt")
            elif lab == VISIBLE and "visible" not in s:
                cur["visible"] = v; s.add("visible")
            elif lab == DISP_COUNT and "disp" not in s:
                cur["disp"] = to_int(v, 1); s.add("disp")
            elif lab == DB_ITEM and "db" not in s:
                cur["db"] = v; s.add("db")
    flush()
    for it in items:
        it.pop("_seen", None)
    return items


def parse_canvases(lines):
    """Lienzos con su tipo, ventana, paginas de pestana y marcos (frames)."""
    b = section_bounds(lines, "Lienzos")
    if not b:
        return []
    seg = lines[b[0] + 1:b[1]]

    canvases = []
    cur = None          # canvas
    rec = None          # sub-registro (pagina o grafico)
    cur_page = ""       # pagina de pestana en curso

    def flush_rec():
        nonlocal cur_page
        if not rec or not cur:
            return
        if rec.get("kind") == "page":
            cur["pages"].append({"name": rec["name"], "label": rec.get("label", rec["name"])})
            cur_page = rec["name"]
        elif rec.get("gtype", "").lower().startswith("marco"):
            cur["frames"].append({
                "title": rec.get("title", ""),
                "x": rec.get("x", 0), "y": rec.get("y", 0),
                "w": rec.get("w", 0), "h": rec.get("h", 0),
                "page": cur_page,
            })

    for l in seg:
        p = parse_line(l)
        if not p:
            continue
        ind, lab, v = p
        if lab == NAME and ind == 3:
            flush_rec(); rec = None
            if cur:
                canvases.append(cur)
            cur = {"name": v, "kind": "", "window": "", "w": 0, "h": 0,
                   "pages": [], "frames": []}
            cur_page = ""
            continue
        if not cur:
            continue
        if ind == 3:
            if lab == CANVAS_KIND:
                cur["kind"] = v
            elif lab == WINDOW:
                cur["window"] = v
            elif lab == WIDTH and not cur["w"]:
                cur["w"] = to_int(v)
            elif lab == HEIGHT and not cur["h"]:
                cur["h"] = to_int(v)
        # sub-registros (paginas de pestana / objetos graficos), indent >= 5
        if lab == NAME and ind >= 5:
            flush_rec()
            rec = {"name": v}
        elif rec is not None:
            if lab == TAB_LABEL:
                rec["kind"] = "page"; rec["label"] = v
            elif lab == GTYPE:
                rec["gtype"] = v
            elif lab == FRAME_TTL:
                rec["title"] = v
            elif lab == POS_X and "x" not in rec:
                rec["x"] = to_int(v)
            elif lab == POS_Y and "y" not in rec:
                rec["y"] = to_int(v)
            elif lab == WIDTH and "w" not in rec:
                rec["w"] = to_int(v)
            elif lab == HEIGHT and "h" not in rec:
                rec["h"] = to_int(v)
    flush_rec()
    if cur:
        canvases.append(cur)
    return canvases


def parse_windows(lines):
    b = section_bounds(lines, "Ventanas")
    if not b:
        return {}
    seg = lines[b[0] + 1:b[1]]
    wins = {}
    cur = None
    for l in seg:
        p = parse_line(l)
        if not p:
            continue
        ind, lab, v = p
        if lab == NAME and ind == 3:
            cur = v
            wins[cur] = {"title": ""}
        elif cur and lab == TITLE and not wins[cur]["title"]:
            wins[cur]["title"] = v
    return wins


def parse(path):
    lines = read_lines(path)
    lz = section_bounds(lines, "Lienzos")
    items_end = lz[0] if lz else len(lines)
    return {
        "form": os.path.splitext(os.path.basename(path))[0],
        "title": form_title(lines),
        "items": parse_items(lines, items_end),
        "canvases": parse_canvases(lines),
        "windows": parse_windows(lines),
    }


# --------------------------------------------------------------------------
# layout: agrupar items en marcos y filas
# --------------------------------------------------------------------------
ROW_TOL = 6


def frame_of(item, frames):
    """Marco mas pequeno que contiene el item; None si ninguno."""
    best, best_area = None, None
    for f in frames:
        if f["w"] <= 0 or f["h"] <= 0:
            continue
        if (f["x"] - 3 <= item["x"] <= f["x"] + f["w"] + 3 and
                f["y"] - 6 <= item["y"] <= f["y"] + f["h"] + 6):
            area = f["w"] * f["h"]
            if best_area is None or area < best_area:
                best, best_area = f, area
    return best


def rows_of(items):
    """Ordena por (y,x) y parte en filas por salto vertical."""
    items = sorted(items, key=lambda it: (it["y"], it["x"]))
    rows, cur, last_y = [], [], None
    for it in items:
        if last_y is None or abs(it["y"] - last_y) <= ROW_TOL:
            cur.append(it)
        else:
            rows.append(cur); cur = [it]
        last_y = it["y"]
    if cur:
        rows.append(cur)
    return rows


def group_items(items, frames):
    """Devuelve lista de grupos {title, singles_rows, grid_cols}."""
    buckets = {}   # frame index (o -1) -> list items
    frame_by_idx = {-1: {"title": ""}}
    for i, f in enumerate(frames):
        frame_by_idx[i] = f
    for it in items:
        f = frame_of(it, frames)
        idx = frames.index(f) if f is not None else -1
        buckets.setdefault(idx, []).append(it)

    # ordenar grupos por posicion del marco
    def gkey(idx):
        if idx == -1:
            return (99999, 99999)
        f = frames[idx]
        return (f["y"], f["x"])

    groups = []
    for idx in sorted(buckets, key=gkey):
        its = buckets[idx]
        singles = [it for it in its if it["disp"] <= 1]
        grids = [it for it in its if it["disp"] > 1]
        groups.append({
            "title": frame_by_idx[idx]["title"],
            "rows": rows_of(singles),
            "grid": sorted(grids, key=lambda it: it["x"]),
            "grid_rows": max((it["disp"] for it in grids), default=0),
        })
    return groups


# --------------------------------------------------------------------------
# render HTML
# --------------------------------------------------------------------------
def esc(s):
    return html.escape(s or "")


def label_of(it):
    return it["prompt"].strip() or it["name"]


def render_field(it):
    fam = widget_family(it["type"])
    lab = esc(label_of(it))
    if fam == "button":
        return '<button class="btn" data-t="%s">%s</button>' % (lab, lab or "Botón")
    if fam == "check":
        return '<label class="chk"><input type="checkbox"><span>%s</span></label>' % lab
    if fam == "radio":
        return ('<span class="fld"><label>%s</label>'
                '<span class="radio">○ ○</span></span>') % lab
    if fam == "image":
        return '<span class="fld"><label>%s</label><span class="img">IMG</span></span>' % lab
    inner = {
        "list":    '<select class="w"><option>— seleccionar —</option></select>',
        "display": '<span class="disp"></span>',
        "text":    '<input class="w" type="text">',
    }[fam]
    if fam == "text":
        low = (it["prompt"] + " " + it["name"]).lower()
        if "fecha" in low or low.strip().startswith("f.") or "f_" in it["name"].lower():
            inner = '<input class="w date" type="text" placeholder="dd/mm/aaaa">'
    return '<span class="fld"><label>%s</label>%s</span>' % (lab, inner)


def render_group(g):
    out = ['<fieldset>']
    if g["title"]:
        out.append('<legend>%s</legend>' % esc(g["title"]))
    for row in g["rows"]:
        out.append('<div class="row">')
        out += [render_field(it) for it in row]
        out.append('</div>')
    if g["grid"]:
        out.append('<table class="grid"><tr>')
        out += ['<th>%s</th>' % esc(label_of(it)) for it in g["grid"]]
        out.append('</tr>')
        for _ in range(min(max(g["grid_rows"], 2), 4)):
            out.append('<tr>' + ''.join('<td><div class="cell"></div></td>' for _ in g["grid"]) + '</tr>')
        out.append('</table>')
    out.append('</fieldset>')
    return "\n".join(out)


def render_screen(canvas, items, wins):
    """Una pantalla (lienzo de contenido o pestana)."""
    title = wins.get(canvas["window"], {}).get("title") or canvas["window"] or canvas["name"]
    parts = ['<section class="win" id="scr-%s">' % esc(canvas["name"]),
             '<div class="titlebar"><span>%s</span>'
             '<span class="dots"><i class="dot"></i><i class="dot"></i><i class="dot"></i></span></div>'
             % esc(title),
             '<div class="winbody">']

    is_tab = "pesta" in canvas["kind"].lower()
    if is_tab and canvas["pages"]:
        parts.append('<div class="tabbar">')
        for i, pg in enumerate(canvas["pages"]):
            cls = "tab active" if i == 0 else "tab"
            parts.append('<div class="%s" data-tab="%s">%s</div>'
                         % (cls, esc(pg["name"]), esc(pg["label"])))
        parts.append('</div>')
        for i, pg in enumerate(canvas["pages"]):
            cls = "tabpanel show" if i == 0 else "tabpanel"
            parts.append('<div class="%s" data-panel="%s">' % (cls, esc(pg["name"])))
            pg_items = [it for it in items if it["page"] == pg["name"]]
            pg_frames = [f for f in canvas["frames"] if f.get("page") == pg["name"]]
            for g in group_items(pg_items, pg_frames):
                parts.append(render_group(g))
            if not pg_items:
                parts.append('<p class="empty">(sin elementos)</p>')
            parts.append('</div>')
    else:
        for g in group_items(items, canvas["frames"]):
            parts.append(render_group(g))
        if not items:
            parts.append('<p class="empty">(sin elementos visibles)</p>')

    parts.append('</div></section>')
    return "\n".join(parts)


def render_toolbar(canvas, items):
    if not canvas:
        return ('<div class="toolbar"><div class="logo">FORM</div>'
                '<div class="tbtns"></div></div>')
    buttons = [it for it in items if widget_family(it["type"]) == "button"]
    fields = [it for it in items if widget_family(it["type"]) in ("display", "text")][:4]
    out = ['<div class="toolbar"><div class="logo">%s</div>' % esc(canvas.get("_form", "FORM"))]
    out.append('<div class="session">')
    for it in fields:
        out.append('<span><b>%s:</b><i class="fakefield"></i></span>' % esc(label_of(it)))
    out.append('</div>')
    out.append('<div class="tbtns" id="tbtns">')
    for it in sorted(buttons, key=lambda b: (b["y"], b["x"])):
        lab = esc(label_of(it))
        out.append('<button class="tbtn" data-t="%s">%s</button>' % (lab, esc(it["name"])))
    out.append('</div></div>')
    return "\n".join(out)


CSS = """
:root{--ink:#2b2b2b;--soft:#5a5a5a;--line:#3a3a3a;--paper:#f4f2ec;--card:#fffdf8;
--field:#fff;--ro:#ece9e1;--accent:#3b6ea5;--accent2:#dbe6f2;--head:#e7e2d6;
--sk:2px 2px 0 rgba(40,40,40,.18);}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font-family:"Kalam","Comic Sans MS","Segoe Print",cursive;font-size:15px;line-height:1.35}
.toolbar{position:sticky;top:0;z-index:20;background:#efece3;border-bottom:2px solid var(--line);
padding:6px 10px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;box-shadow:0 2px 0 rgba(40,40,40,.12)}
.logo{border:2px solid var(--line);border-radius:4px;padding:4px 10px;background:#fff;font-weight:700;box-shadow:var(--sk)}
.session{display:flex;gap:12px;flex-wrap:wrap;color:var(--soft);font-size:13px}
.session b{color:var(--ink)} .fakefield{display:inline-block;min-width:70px;height:16px;border-bottom:1.5px dashed #999;vertical-align:middle}
.tbtns{display:flex;gap:5px;margin-left:auto;flex-wrap:wrap}
.tbtn{border:1.6px solid var(--line);background:#f7f4ec;border-radius:5px;padding:3px 8px;cursor:pointer;
font-family:inherit;font-size:12px;color:var(--ink);box-shadow:var(--sk);transition:transform .05s}
.tbtn:hover{background:#fff} .tbtn:active{transform:translate(2px,2px);box-shadow:none}
.shell{display:grid;grid-template-columns:240px 1fr;min-height:calc(100vh - 46px)}
.nav{border-right:2px solid var(--line);padding:14px 10px;background:#efece3}
.nav h2{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--soft);margin:16px 6px 6px}
.nav h2:first-child{margin-top:0}
.nav a{display:block;padding:6px 10px;margin:3px 0;cursor:pointer;color:var(--ink);
border:1.5px solid transparent;border-radius:6px}
.nav a:hover{background:#fff;border-color:#cfc9ba}
.nav a.active{background:var(--accent2);border-color:var(--accent);font-weight:700}
.stage{padding:24px 28px}
.win{display:none;max-width:820px;margin:0 auto;background:var(--card);border:2px solid var(--line);
border-radius:8px;box-shadow:5px 5px 0 rgba(40,40,40,.15);overflow:hidden}
.win.show{display:block;animation:pop .18s ease}
@keyframes pop{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.titlebar{background:#e6e1d4;border-bottom:2px solid var(--line);padding:7px 12px;display:flex;
align-items:center;gap:8px;font-weight:700}
.titlebar .dots{margin-left:auto;display:flex;gap:6px}
.dot{width:13px;height:13px;border:1.5px solid var(--line);border-radius:3px;background:#fff;display:inline-block}
.winbody{padding:16px 18px 22px}
fieldset{border:1.6px dashed #8c8578;border-radius:7px;margin:0 0 16px;padding:12px 16px 16px}
legend{padding:0 8px;font-weight:700;color:var(--accent);font-size:14px}
.row{display:flex;flex-wrap:wrap;gap:9px 18px;align-items:center;margin:8px 0}
.fld{display:flex;align-items:center;gap:7px}
.fld>label{color:var(--soft)}
input.w,select.w,.disp{font-family:inherit;font-size:14px;color:var(--ink);border:1.5px solid #9a9384;
border-radius:4px;background:var(--field);padding:3px 7px;height:26px}
input.w{min-width:150px} select.w{min-width:160px}
.disp{background:var(--ro);color:#555;min-width:120px;display:inline-flex;align-items:center}
input.date{min-width:110px}
.chk{display:flex;align-items:center;gap:7px} .chk input{width:16px;height:16px}
.radio{letter-spacing:3px;color:#8a8378} .img{border:1.5px dashed #9a9384;padding:2px 10px;color:#8a8378;background:#fff}
.btn{font-family:inherit;border:1.6px solid var(--line);background:#eee;border-radius:5px;padding:4px 12px;cursor:pointer;box-shadow:var(--sk)}
.btn:active{transform:translate(2px,2px);box-shadow:none}
table.grid{border-collapse:collapse;width:100%;margin-top:4px}
table.grid th{background:var(--head);border:1.4px solid #9a9384;padding:4px 8px;font-size:13px;text-align:left}
table.grid td{border:1.4px solid #b8b1a2;padding:2px 6px}
table.grid .cell{height:20px;background:var(--field);border:1px solid #cfc7b6;border-radius:3px}
.tabbar{display:flex;gap:4px;border-bottom:2px solid var(--line);flex-wrap:wrap}
.tab{border:1.6px solid var(--line);border-bottom:none;border-radius:7px 7px 0 0;padding:5px 12px;cursor:pointer;
background:#e6e1d4;font-size:13px;color:var(--soft);position:relative;top:2px}
.tab.active{background:var(--card);color:var(--accent);font-weight:700;border-bottom:2px solid var(--card)}
.tabpanel{display:none;border:1.6px solid var(--line);border-top:none;padding:14px 16px;background:var(--card);border-radius:0 0 7px 7px}
.tabpanel.show{display:block}
.empty{color:#8a8378;font-style:italic}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--ink);
color:#fff;padding:8px 16px;border-radius:20px;font-size:13px;opacity:0;pointer-events:none;transition:all .2s;z-index:50}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.foot{max-width:820px;margin:16px auto 0;color:#8a8378;font-size:12px;text-align:center}
"""

JS = """
function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');
clearTimeout(window._tt);window._tt=setTimeout(function(){t.classList.remove('show')},1400);}
function show(id){document.querySelectorAll('.win').forEach(function(w){w.classList.remove('show')});
var s=document.getElementById('scr-'+id);if(s)s.classList.add('show');
document.querySelectorAll('.nav a').forEach(function(a){a.classList.toggle('active',a.dataset.s===id)});
window.scrollTo({top:0,behavior:'smooth'});}
document.getElementById('nav').addEventListener('click',function(e){
var a=e.target.closest('a');if(a)show(a.dataset.s);});
document.addEventListener('click',function(e){
var b=e.target.closest('.tbtn,.btn');if(b&&b.dataset.t){toast('▶ '+b.dataset.t);return;}
var t=e.target.closest('.tab');if(t){var bar=t.parentNode,body=bar.parentNode;
bar.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active')});
body.querySelectorAll('.tabpanel').forEach(function(p){p.classList.remove('show')});
t.classList.add('active');
body.querySelector('.tabpanel[data-panel="'+t.dataset.tab+'"]').classList.add('show');}});
"""


def build_html(layout):
    items = [it for it in layout["items"] if it.get("visible", "Sí") != "No"]
    canvases = layout["canvases"]
    wins = layout["windows"]

    by_canvas = {}
    for it in items:
        by_canvas.setdefault(it["canvas"], []).append(it)

    toolbar_cv = next((c for c in canvases if "barra de herramientas" in c["kind"].lower()), None)
    if toolbar_cv:
        toolbar_cv["_form"] = layout["form"]
    screens = [c for c in canvases if c is not toolbar_cv and c["kind"].lower() != ""]
    # solo lienzos con al menos un item
    screens = [c for c in screens if by_canvas.get(c["name"])]

    # navegacion agrupada por ventana
    nav_groups = {}
    for c in screens:
        wt = wins.get(c["window"], {}).get("title") or c["window"] or "(sin ventana)"
        nav_groups.setdefault(wt, []).append(c)

    nav = ['<nav class="nav" id="nav">']
    first_id = screens[0]["name"] if screens else ""
    for wt, cs in nav_groups.items():
        nav.append('<h2>%s</h2>' % esc(wt))
        for c in cs:
            label = (c["frames"][0]["title"] if c["frames"] and c["frames"][0]["title"] else c["name"])
            cls = ' class="active"' if c["name"] == first_id else ''
            nav.append('<a data-s="%s"%s>%s</a>' % (esc(c["name"]), cls, esc(label)))
    nav.append('</nav>')

    body = [render_toolbar(toolbar_cv, by_canvas.get(toolbar_cv["name"], []) if toolbar_cv else [])]
    body.append('<div class="shell">')
    body.append("\n".join(nav))
    body.append('<main class="stage">')
    for i, c in enumerate(screens):
        html_scr = render_screen(c, by_canvas.get(c["name"], []), wins)
        if i == 0:
            html_scr = html_scr.replace('class="win"', 'class="win show"', 1)
        body.append(html_scr)
    body.append('<div class="foot">Wireframe reconstruido de %s.txt &middot; datos de ejemplo</div>' % esc(layout["form"]))
    body.append('</main></div>')

    title = layout["title"] or layout["form"]
    return ("""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s - Wireframe</title>
<link href="https://fonts.googleapis.com/css2?family=Kalam:wght@300;400;700&display=swap" rel="stylesheet">
<style>%s</style></head><body>
%s
<div class="toast" id="toast"></div>
<script>%s</script></body></html>""" % (esc(title), CSS, "\n".join(body), JS))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def cmd_inspect(args):
    layout = parse(args.form_file)
    if args.json:
        print(json.dumps(layout, ensure_ascii=False, indent=2))
        return
    print("# Wireframe inventory: %s" % layout["form"])
    print("  Titulo: %s" % (layout["title"] or "(sin titulo)"))
    print("  Ventanas: %d   Lienzos: %d   Items: %d\n"
          % (len(layout["windows"]), len(layout["canvases"]), len(layout["items"])))
    by_c = {}
    for it in layout["items"]:
        by_c.setdefault(it["canvas"] or "(sin lienzo)", 0)
        by_c[it["canvas"] or "(sin lienzo)"] += 1
    for c in layout["canvases"]:
        n = by_c.get(c["name"], 0)
        tabs = (" | pestanas: " + ", ".join(p["label"] for p in c["pages"])) if c["pages"] else ""
        frames = (" | marcos: " + ", ".join(f["title"] for f in c["frames"] if f["title"])) if c["frames"] else ""
        print("  [%s] tipo=%s ventana=%s items=%d%s%s"
              % (c["name"], c["kind"] or "?", c["window"] or "?", n, tabs, frames))


def cmd_build(args):
    layout = parse(args.form_file)
    out = args.output
    if not out:
        d = os.path.dirname(os.path.abspath(args.form_file))
        out = os.path.join(d, layout["form"] + "_wireframe.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(layout))
    n_scr = sum(1 for c in layout["canvases"]
                if "barra" not in c["kind"].lower() and c["kind"]
                and any(it["canvas"] == c["name"] for it in layout["items"]))
    print("OK -> %s" % out)
    print("   %d pantallas, %d items" % (n_scr, len(layout["items"])))


def main():
    ap = argparse.ArgumentParser(description="Oracle Form export -> interactive HTML wireframe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("inspect", help="inventario de ventanas/lienzos/items")
    pi.add_argument("form_file"); pi.add_argument("--json", action="store_true")
    pi.set_defaults(func=cmd_inspect)
    pb = sub.add_parser("build", help="genera el wireframe .html")
    pb.add_argument("form_file"); pb.add_argument("-o", "--output")
    pb.set_defaults(func=cmd_build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
