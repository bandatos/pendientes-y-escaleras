"""Comparación entre el .osm generado y el que volvió editado de JOSM.

El archivo generado es una propuesta y JOSM es donde se corrige; para que
esa corrección pueda volver a la plantilla hay que poder leerla, y leerla
en el marco de la plantilla —metros sobre el eje de la estación— y no en
grados. JOSM renumera los ids negativos al guardar, así que el
emparejamiento se apoya primero en las etiquetas de traza y solo después
en la cercanía.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from xml.etree import ElementTree

from .geometry import LocalFrame

FRAME_RE = re.compile(
    r"frame anchor=(-?[\d.]+),(-?[\d.]+) bearing=(-?[\d.]+) "
    r"mirror=(true|false)")
MOVE_TOLERANCE_M = 0.25
MATCH_RADIUS_M = 3.0


class DiffError(Exception):
    pass


@dataclass
class Element:
    kind: str            # 'node' | 'way'
    osm_id: int
    tags: dict
    u: float = 0.0
    v: float = 0.0
    nds: list = field(default_factory=list)

    @property
    def foreign(self) -> bool:
        return self.osm_id > 0


def read_frame(path) -> LocalFrame:
    for line in open(path, encoding="utf-8"):
        m = FRAME_RE.search(line)
        if m:
            return LocalFrame(float(m.group(1)), float(m.group(2)),
                              float(m.group(3)), m.group(4) == "true")
        if "<node" in line:
            break
    raise DiffError(
        f"{path} no trae el comentario con el marco local; regenera la "
        f"estación con export_station_osm o pasa --anchor y --bearing")


def read_document(path, frame: LocalFrame) -> dict:
    root = ElementTree.parse(path).getroot()
    out = {}
    coords = {}
    for node in root.iter("node"):
        nid = int(node.get("id"))
        u, v = frame.to_local(float(node.get("lat")), float(node.get("lon")))
        coords[nid] = (u, v)
        out[("node", nid)] = Element(
            "node", nid, _tags(node), u, v)
    for way in root.iter("way"):
        wid = int(way.get("id"))
        nds = [int(nd.get("ref")) for nd in way.findall("nd")]
        pts = [coords[n] for n in nds if n in coords]
        cu = sum(p[0] for p in pts) / len(pts) if pts else 0.0
        cv = sum(p[1] for p in pts) / len(pts) if pts else 0.0
        out[("way", wid)] = Element("way", wid, _tags(way), cu, cv, nds)
    return out


def _tags(el) -> dict:
    return {t.get("k"): t.get("v") for t in el.findall("tag")}


def _key(el: Element):
    """Identidad estable del elemento entre las dos versiones.

    El `note:stop_id` de un andén lo llevan dos ways —el polígono y la
    línea de circulación—, así que la etiqueta sola no basta y el rol se
    saca de lo que el objeto es.
    """
    if el.foreign:
        return ("osm", el.kind, el.osm_id)
    trace = (el.tags.get("note:pathway_id") or el.tags.get("note:stop_id"))
    if not trace:
        return None
    role = "nodo"
    if el.kind == "way":
        role = ("anden" if el.tags.get("railway") == "platform"
                else "linea")
    return ("trace", el.kind, trace, role)


def compare(generated: dict, edited: dict) -> dict:
    gen_keys = {}
    for el in generated.values():
        key = _key(el)
        if key is not None:
            gen_keys.setdefault(key, el)
    edit_keys = {}
    for el in edited.values():
        key = _key(el)
        if key is not None:
            edit_keys.setdefault(key, el)

    moved, retagged, reshaped, deleted, added = [], [], [], [], []
    matched_edit = set()
    for key, el in gen_keys.items():
        other = edit_keys.get(key)
        if other is None:
            deleted.append(el)
            continue
        matched_edit.add(id(other))
        _compare_pair(el, other, moved, retagged, reshaped)

    # Lo que no lleva traza (vértices sueltos, puertas, superficies) se
    # empareja por cercanía: es lo único que sobrevive a la renumeración.
    rest_gen = [e for e in generated.values() if _key(e) is None]
    rest_edit = [e for e in edited.values()
                 if _key(e) is None and id(e) not in matched_edit]
    used = set()
    for el in rest_gen:
        best = None
        for i, other in enumerate(rest_edit):
            if i in used or other.kind != el.kind:
                continue
            d = math.hypot(other.u - el.u, other.v - el.v)
            if d <= MATCH_RADIUS_M and (best is None or d < best[0]):
                best = (d, i, other)
        if best is None:
            deleted.append(el)
            continue
        used.add(best[1])
        _compare_pair(el, best[2], moved, retagged, reshaped)
    added += [o for i, o in enumerate(rest_edit) if i not in used]
    added += [o for k, o in edit_keys.items() if k not in gen_keys]
    return {"moved": moved, "retagged": retagged, "reshaped": reshaped,
            "deleted": deleted, "added": added}


def _compare_pair(a: Element, b: Element, moved, retagged, reshaped) -> None:
    du, dv = b.u - a.u, b.v - a.v
    dist = math.hypot(du, dv)
    if dist > MOVE_TOLERANCE_M:
        moved.append((a, du, dv, dist))
    if a.kind == "way" and len(a.nds) != len(b.nds):
        reshaped.append((a, len(a.nds), len(b.nds)))
    changes = _tag_changes(a.tags, b.tags)
    if changes:
        retagged.append((a, changes))


def _tag_changes(before: dict, after: dict) -> list:
    out = []
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key), after.get(key)
        if old != new:
            out.append((key, old, new))
    return out


def label(el: Element) -> str:
    trace = (el.tags.get("note:pathway_id") or el.tags.get("note:stop_id"))
    if el.foreign:
        what = "nodo" if el.kind == "node" else "way"
        return f"{what} OSM {el.osm_id}"
    what = _what(el)
    return f"{what} {trace}" if trace else f"{what} (sin traza)"


def _what(el: Element) -> str:
    tags = el.tags
    if el.kind == "node":
        if tags.get("railway") == "subway_entrance":
            return "acceso"
        if tags.get("disused:railway") == "subway_entrance":
            return "acceso clausurado"
        if tags.get("barrier") == "turnstile":
            return "torniquete"
        return "nodo"
    if tags.get("railway") == "platform":
        return "andén"
    if tags.get("public_transport") == "station":
        return "área de estación"
    if tags.get("building"):
        return "edificio"
    if tags.get("highway") == "pedestrian":
        return "explanada"
    if tags.get("highway") == "steps":
        return ("escalera eléctrica" if tags.get("conveying")
                else "escalera")
    if tags.get("highway") == "footway":
        return "pasillo" if tags.get("indoor") else "andador"
    return "way"
