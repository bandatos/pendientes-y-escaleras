"""Vista en planta por nivel, en SVG puro, para revisar antes de JOSM."""
from __future__ import annotations

from .document import OsmDocument

SCALE = 3.0          # píxeles por metro
MARGIN = 40.0

COLORS = {
    "platform": "#c9d6e2",
    "platform_stroke": "#5b7a99",
    "footway": "#1f6feb",
    "steps": "#e07b00",
    "escalator": "#c0392b",
    "entrance": "#1e8e3e",
    "turnstile": "#111111",
}


def levels_in(doc: OsmDocument) -> list[int]:
    out = set()
    for way in doc.ways:
        if way.foreign:
            continue
        for part in way.tags.get("level", "").split(";"):
            if part.strip():
                out.add(int(part))
    return sorted(out)


def _esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _framed_nodes(doc: OsmDocument) -> list:
    """Nodos que encuadran la vista: los de las piezas con nivel.

    Fuera quedan el contexto de OSM y las superficies sin nivel (área de
    estación, edificio, explanada), que abarcan mucho más que la
    circulación y dejarían el dibujo minúsculo.
    """
    ids = set()
    for way in doc.ways:
        if not way.foreign and "level" in way.tags:
            ids |= set(way.nodes)
    out = [doc.nodes[i] for i in ids if i in doc.nodes]
    return out or [n for n in doc.nodes.values() if not n.foreign]


def render_level(doc: OsmDocument, level: int, title: str) -> str:
    framed = _framed_nodes(doc)
    us = [n.u for n in framed]
    vs = [n.v for n in framed]
    umin, umax = min(us) - 5, max(us) + 5
    vmin, vmax = min(vs) - 5, max(vs) + 5
    # Holgura a la derecha para las etiquetas de los accesos, que salen
    # del objeto hacia afuera.
    width = (vmax - vmin) * SCALE + 2 * MARGIN + 120
    height = (umax - umin) * SCALE + 2 * MARGIN

    def xy(u, v):
        # +u (rumbo del eje) hacia arriba, +v (derecha del eje) a la derecha
        return (MARGIN + (v - vmin) * SCALE,
                MARGIN + (umax - u) * SCALE)

    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width:.0f}' "
           f"height='{height:.0f}' viewBox='0 0 {width:.0f} "
           f"{height:.0f}'>",
           "<rect width='100%' height='100%' fill='#ffffff'/>",
           _defs(),
           f"<text x='{MARGIN}' y='24' font-family='sans-serif' "
           f"font-size='16' fill='#222'>{_esc(title)} — nivel {level}"
           f"</text>"]

    def in_level(way):
        parts = [int(p) for p in way.tags.get("level", "").split(";")
                 if p.strip()]
        return level in parts

    for way in doc.ways:
        if way.foreign:
            continue
        if not in_level(way) or way.tags.get("railway") != "platform":
            continue
        pts = " ".join(f"{xy(*_uv(doc, n))[0]:.1f},"
                       f"{xy(*_uv(doc, n))[1]:.1f}" for n in way.nodes)
        out.append(f"<polygon points='{pts}' fill='{COLORS['platform']}' "
                   f"stroke='{COLORS['platform_stroke']}' "
                   f"stroke-width='1.5'/>")
        # Etiqueta cerca del extremo superior: en el centro se encimaría
        # con la del andén de enfrente.
        top_u = max(doc.nodes[n].u for n in way.nodes)
        cv = sum(doc.nodes[n].v for n in way.nodes) / len(way.nodes)
        x, y = xy(top_u - 8, cv)
        label = way.tags.get("destination") or way.tags.get("name", "")
        out.append(_text(x, y, f"{way.label} {label}", "#33475b"))

    labelled = 0
    for way in doc.ways:
        if way.foreign:
            continue
        if not in_level(way) or way.tags.get("railway") == "platform":
            continue
        highway = way.tags.get("highway")
        if highway == "steps":
            color = (COLORS["escalator"] if way.tags.get("conveying")
                     else COLORS["steps"])
            dash = "6,3" if way.tags.get("conveying") else "none"
            marker = " marker-end='url(#arrow)'"
        else:
            color = COLORS["footway"]
            dash = "none"
            marker = ""
        pts = " ".join(f"{xy(*_uv(doc, n))[0]:.1f},"
                       f"{xy(*_uv(doc, n))[1]:.1f}" for n in way.nodes)
        out.append(f"<polyline points='{pts}' fill='none' stroke='{color}' "
                   f"stroke-width='2.5' stroke-dasharray='{dash}'"
                   f"{marker}/>")
        if way.tags.get("name"):
            mid = doc.nodes[way.nodes[len(way.nodes) // 2]]
            x, y = xy(mid.u, mid.v)
            out.append(_text(x, y - 6 - 11 * (labelled % 3),
                             way.tags["name"], color))
            labelled += 1

    for node in doc.nodes.values():
        if node.frozen:
            continue
        x, y = xy(node.u, node.v)
        if node.tags.get("railway") == "subway_entrance":
            if int(node.tags.get("level", "0")) != level:
                continue
            out.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' "
                       f"fill='{COLORS['entrance']}'/>")
            label = (node.tags.get("description")
                     or node.tags.get("name", ""))
            out.append(_text(x + 9, y + 4, label,
                             COLORS["entrance"], anchor="start"))
        elif node.tags.get("barrier") == "turnstile":
            if int(node.tags.get("level", "0")) != level:
                continue
            out.append(f"<rect x='{x - 4:.1f}' y='{y - 4:.1f}' width='8' "
                       f"height='8' fill='{COLORS['turnstile']}'/>")
            out.append(_text(x, y + 18, "torniquetes",
                             COLORS["turnstile"]))

    out.append(_legend(width, height))
    out.append(_scale_bar(MARGIN, height - 14))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _uv(doc, nid):
    node = doc.nodes[nid]
    return node.u, node.v


def _text(x, y, text, color, anchor="middle", size=10):
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-family='sans-serif' "
            f"font-size='{size}' fill='{color}' text-anchor='{anchor}'>"
            f"{_esc(text)}</text>")


def _defs():
    return ("<defs><marker id='arrow' viewBox='0 0 10 10' refX='9' "
            "refY='5' markerWidth='3.5' markerHeight='3.5' orient='auto'>"
            "<path d='M 0 0 L 10 5 L 0 10 z' fill='#444'/></marker></defs>")


def _legend(width, height):
    items = [("andén", COLORS["platform_stroke"]),
             ("pasillo", COLORS["footway"]),
             ("escaleras", COLORS["steps"]),
             ("escalera eléctrica", COLORS["escalator"]),
             ("acceso", COLORS["entrance"])]
    out = []
    y = 44
    for label, color in items:
        out.append(f"<rect x='{width - 150:.0f}' y='{y - 8}' width='14' "
                   f"height='4' fill='{color}'/>")
        out.append(_text(width - 130, y - 3, label, "#333", anchor="start"))
        y += 16
    return "\n".join(out)


def _scale_bar(x, y):
    length = 20 * SCALE
    return (f"<line x1='{x}' y1='{y}' x2='{x + length}' y2='{y}' "
            f"stroke='#333' stroke-width='2'/>"
            + _text(x + length / 2, y - 4, "20 m", "#333"))


def render_all(doc: OsmDocument, title: str) -> dict[int, str]:
    return {lvl: render_level(doc, lvl, title) for lvl in levels_in(doc)}
