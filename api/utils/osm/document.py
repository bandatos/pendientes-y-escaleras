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
    # Un objeto «ajeno» es uno que ya existe en OSM: se escribe con su id
    # real y su `version`, y `frozen` marca los que solo vienen de
    # contexto y no se pueden mover, pegar ni soldar por accidente.
    foreign: bool = False
    frozen: bool = False
    action: str | None = None
    meta: dict = field(default_factory=dict)
    latlon: tuple[float, float] | None = None


@dataclass
class OsmWay:
    id: int
    nodes: list[int]
    tags: dict = field(default_factory=dict)
    levels: tuple[float, ...] = ()
    kind: str = "way"
    label: str = ""
    foreign: bool = False
    frozen: bool = False
    action: str | None = None
    meta: dict = field(default_factory=dict)


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
            if node.frozen:
                continue
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
        return self.add_way_from_ids(ids, tags, levels, kind, label, closed)

    def add_way_from_ids(self, ids, tags: dict, levels, kind: str = "way",
                         label: str = "", closed: bool = False) -> OsmWay:
        ids = list(ids)
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

    # ---------------- objetos ajenos ----------------

    def add_foreign_node(self, foreign) -> int:
        """Registra un nodo que ya existe en OSM, tal cual está."""
        if foreign.osm_id in self.nodes:
            return foreign.osm_id
        u, v = self.frame.to_local(foreign.lat, foreign.lon)
        self.nodes[foreign.osm_id] = OsmNode(
            foreign.osm_id, u, v, dict(foreign.tags), foreign=True,
            frozen=True, meta=dict(foreign.meta),
            latlon=(foreign.lat, foreign.lon))
        return foreign.osm_id

    def add_foreign_way(self, foreign, context, kind: str = "context",
                        label: str = "") -> OsmWay:
        for nid in foreign.node_ids:
            node = context.nodes.get(nid)
            if node is not None:
                self.add_foreign_node(node)
        ids = [n for n in foreign.node_ids if n in self.nodes]
        way = OsmWay(foreign.osm_id, ids, dict(foreign.tags), (), kind,
                     label or str(foreign.osm_id), foreign=True,
                     frozen=True, meta=dict(foreign.meta))
        self.ways.append(way)
        return way

    def adopt_node(self, foreign, u: float, v: float, tags: dict) -> int:
        """Reutiliza un nodo de OSM como nodo nuestro, marcándolo modify.

        Se queda con el valor de OSM en toda clave que ya traiga: el
        archivo propone lo que falta, nunca pisa lo que otra persona
        mapeó. Devuelve el id real y la lista de conflictos.
        """
        merged = dict(foreign.tags)
        conflicts = []
        for key, value in tags.items():
            if key not in merged:
                merged[key] = value
            elif str(merged[key]) != str(value):
                conflicts.append((key, merged[key], value))
        node = self.nodes.get(foreign.osm_id)
        if node is None:
            node = OsmNode(foreign.osm_id, u, v, merged, foreign=True,
                           meta=dict(foreign.meta))
            self.nodes[foreign.osm_id] = node
        else:
            node.u, node.v, node.tags = u, v, merged
        node.frozen = False
        node.latlon = None
        node.action = "modify"
        return foreign.osm_id, conflicts

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
            if way.frozen:
                continue
            for nid in (way.nodes[0], way.nodes[-1]):
                endpoints.append((nid, way))
        for nid, source in endpoints:
            node = self.nodes[nid]
            if node.frozen:
                continue
            p = (node.u, node.v)
            for way in self.ways:
                if way is source or way.frozen or nid in way.nodes:
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

    def insert_node_id(self, way: OsmWay, nid: int) -> None:
        """Mete un nodo ya existente como vértice del way que lo cruza."""
        if nid in way.nodes:
            return
        node = self.nodes[nid]
        best = None
        for i in range(len(way.nodes) - 1):
            a = self.nodes[way.nodes[i]]
            b = self.nodes[way.nodes[i + 1]]
            d, _ = point_segment_distance(
                (node.u, node.v), (a.u, a.v), (b.u, b.v))
            if best is None or d < best[0]:
                best = (d, i)
        way.nodes.insert(best[1] + 1, nid)

    # ---------------- salida ----------------

    def strip_trace(self, keys) -> None:
        for holder in list(self.nodes.values()) + self.ways:
            for key in keys:
                holder.tags.pop(key, None)

    def bounds(self) -> tuple[float, float, float, float]:
        # Solo los objetos nuestros: el encuadre es el de la estación que
        # se está dibujando, no el del contexto que se trajo para pegarse.
        own = [n for n in self.nodes.values() if not n.foreign]
        coords = [self.frame.to_wgs84(n.u, n.v) for n in own or
                  list(self.nodes.values())]
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        return min(lats), min(lons), max(lats), max(lons)

    def frame_comment(self) -> str:
        """Marco local del archivo, para que `diff_station_osm` lo lea."""
        return (f"  <!-- frame anchor={self.frame.lat:.7f},"
                f"{self.frame.lon:.7f} bearing={self.frame.bearing_deg} "
                f"mirror={'true' if self.frame.mirror else 'false'} -->")

    def to_xml(self, generator: str = "pendientes-y-escaleras") -> str:
        minlat, minlon, maxlat, maxlon = self.bounds()
        out = ["<?xml version='1.0' encoding='UTF-8'?>",
               f"<osm version='0.6' generator='{_esc(generator)}' "
               f"upload='never'>",
               self.frame_comment(),
               f"  <bounds minlat='{minlat:.7f}' minlon='{minlon:.7f}' "
               f"maxlat='{maxlat:.7f}' maxlon='{maxlon:.7f}'/>"]
        for node in sorted(self.nodes.values(), key=lambda n: -n.id):
            if node.latlon:
                lat, lon = node.latlon
            else:
                lat, lon = self.frame.to_wgs84(node.u, node.v)
            head = (f"  <node id='{node.id}' visible='true' "
                    f"lat='{lat:.7f}' lon='{lon:.7f}'{_meta(node)}")
            if not node.tags:
                out.append(head + "/>")
                continue
            out.append(head + ">")
            out += _tag_lines(node.tags, "    ")
            out.append("  </node>")
        for way in sorted(self.ways, key=lambda w: -w.id):
            out.append(f"  <way id='{way.id}' visible='true'{_meta(way)}>")
            out += [f"    <nd ref='{nid}'/>" for nid in way.nodes]
            out += _tag_lines(way.tags, "    ")
            out.append("  </way>")
        out.append("</osm>")
        return "\n".join(out) + "\n"


def _meta(holder) -> str:
    """Atributos de versión de un objeto ajeno; vacío para los nuestros.

    Sin `version` JOSM trata el objeto como nuevo y lo subiría duplicado;
    `action='modify'` solo va donde deliberadamente lo cambiamos.
    """
    if not holder.foreign:
        return ""
    parts = []
    if holder.action:
        parts.append(f" action='{holder.action}'")
    for key in ("version", "timestamp", "changeset", "user", "uid"):
        if key in holder.meta:
            parts.append(f" {key}='{_esc(holder.meta[key])}'")
    return "".join(parts)


def _tag_lines(tags: dict, indent: str) -> list[str]:
    return [f"{indent}<tag k='{_esc(k)}' v='{_esc(v)}'/>"
            for k, v in tags.items()]
