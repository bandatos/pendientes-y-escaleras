"""Documento OSM en memoria: registro de nodos, ways, soldadura y XML."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .geometry import LocalFrame, point_segment_distance

# Dos puntos más cercanos que esto son el mismo nodo: evita duplicados
# invisibles cuando plantilla y soldadura llegan al mismo sitio.
SNAP_TOLERANCE_M = 0.25


@dataclass
class OsmNode:
    id: int
    u: float
    v: float
    tags: dict = field(default_factory=dict)


@dataclass
class OsmWay:
    id: int
    nodes: list[int]
    tags: dict = field(default_factory=dict)
    levels: tuple[float, ...] = ()
    kind: str = "way"
    label: str = ""


def _esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace("'", "&apos;")
            .replace('"', "&quot;"))


class OsmDocument:

    def __init__(self, frame: LocalFrame):
        self.frame = frame
        self.nodes: dict[int, OsmNode] = {}
        self.ways: list[OsmWay] = []
        self._next_id = -1

    def _new_id(self) -> int:
        i = self._next_id
        self._next_id -= 1
        return i

    def node_at(self, u: float, v: float, tags: dict | None = None) -> int:
        """Devuelve el id del nodo en (u, v), reutilizando el cercano."""
        for node in self.nodes.values():
            if math.hypot(node.u - u, node.v - v) <= SNAP_TOLERANCE_M:
                if tags:
                    node.tags.update(tags)
                return node.id
        nid = self._new_id()
        self.nodes[nid] = OsmNode(nid, u, v, dict(tags or {}))
        return nid

    def add_way(self, points, tags: dict, levels, kind: str = "way",
                label: str = "", closed: bool = False) -> OsmWay:
        ids = [self.node_at(u, v) for u, v in points]
        if closed and ids[0] != ids[-1]:
            ids.append(ids[0])
        deduped = [ids[0]]
        for nid in ids[1:]:
            if nid != deduped[-1]:
                deduped.append(nid)
        way = OsmWay(self._new_id(), deduped, dict(tags),
                     tuple(sorted(set(levels))), kind, label)
        self.ways.append(way)
        return way

    # ---------------- soldadura ----------------

    def weld(self, tolerance: float = SNAP_TOLERANCE_M) -> int:
        """Inserta los extremos de cada way en los ways que atraviesan.

        Sin esto la conectividad sería solo visual: dos líneas que se
        tocan en pantalla pero no comparten nodo no son un grafo. Solo
        suelda entre ways que comparten algún nivel, para no coser un
        pasillo del +1 con el andén del 0 que pasa por debajo.
        """
        inserted = 0
        endpoints = []
        for way in self.ways:
            for nid in (way.nodes[0], way.nodes[-1]):
                endpoints.append((nid, way))
        for nid, source in endpoints:
            node = self.nodes[nid]
            p = (node.u, node.v)
            for way in self.ways:
                if way is source or nid in way.nodes:
                    continue
                if not set(way.levels) & set(source.levels):
                    continue
                best = None
                for i in range(len(way.nodes) - 1):
                    a = self.nodes[way.nodes[i]]
                    b = self.nodes[way.nodes[i + 1]]
                    d, t = point_segment_distance(
                        p, (a.u, a.v), (b.u, b.v))
                    if d <= tolerance and 0.0 < t < 1.0:
                        if best is None or d < best[0]:
                            best = (d, i)
                if best is not None:
                    way.nodes.insert(best[1] + 1, nid)
                    inserted += 1
        return inserted

    def insert_on_way(self, way: OsmWay, u: float, v: float,
                      tags: dict) -> int:
        """Añade un nodo etiquetado sobre el segmento más cercano."""
        if len(way.nodes) < 2:
            raise ValueError(
                f"no se puede insertar un nodo en el way {way.id} "
                f"({way.label}): tiene menos de dos nodos")
        best = None
        for i in range(len(way.nodes) - 1):
            a = self.nodes[way.nodes[i]]
            b = self.nodes[way.nodes[i + 1]]
            d, _ = point_segment_distance((u, v), (a.u, a.v), (b.u, b.v))
            if best is None or d < best[0]:
                best = (d, i)
        nid = self.node_at(u, v, tags)
        if nid not in way.nodes:
            way.nodes.insert(best[1] + 1, nid)
        else:
            self.nodes[nid].tags.update(tags)
        return nid

    # ---------------- salida ----------------

    def strip_trace(self, keys) -> None:
        for holder in list(self.nodes.values()) + self.ways:
            for key in keys:
                holder.tags.pop(key, None)

    def bounds(self) -> tuple[float, float, float, float]:
        coords = [self.frame.to_wgs84(n.u, n.v) for n in self.nodes.values()]
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        return min(lats), min(lons), max(lats), max(lons)

    def to_xml(self, generator: str = "pendientes-y-escaleras") -> str:
        minlat, minlon, maxlat, maxlon = self.bounds()
        out = ["<?xml version='1.0' encoding='UTF-8'?>",
               f"<osm version='0.6' generator='{_esc(generator)}' "
               f"upload='never'>",
               f"  <bounds minlat='{minlat:.7f}' minlon='{minlon:.7f}' "
               f"maxlat='{maxlat:.7f}' maxlon='{maxlon:.7f}'/>"]
        for node in sorted(self.nodes.values(), key=lambda n: -n.id):
            lat, lon = self.frame.to_wgs84(node.u, node.v)
            head = (f"  <node id='{node.id}' visible='true' "
                    f"lat='{lat:.7f}' lon='{lon:.7f}'")
            if not node.tags:
                out.append(head + "/>")
                continue
            out.append(head + ">")
            out += _tag_lines(node.tags, "    ")
            out.append("  </node>")
        for way in sorted(self.ways, key=lambda w: -w.id):
            out.append(f"  <way id='{way.id}' visible='true'>")
            out += [f"    <nd ref='{nid}'/>" for nid in way.nodes]
            out += _tag_lines(way.tags, "    ")
            out.append("  </way>")
        out.append("</osm>")
        return "\n".join(out) + "\n"


def _tag_lines(tags: dict, indent: str) -> list[str]:
    return [f"{indent}<tag k='{_esc(k)}' v='{_esc(v)}'/>"
            for k, v in tags.items()]
