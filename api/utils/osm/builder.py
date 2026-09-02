"""Ensamblado del documento OSM a partir del grafo y de la plantilla."""
from __future__ import annotations

from . import tags as T
from .document import OsmDocument
from .geometry import LocalFrame, point_along_polyline
from .graph import StationGraph
from .template import FamilyTemplate, TemplateError

LOCATION_PLATFORM = 0
LOCATION_ENTRANCE = 2
LOCATION_GENERIC = 3


class StationBuilder:

    def __init__(self, graph: StationGraph, template: FamilyTemplate,
                 frame: LocalFrame, trace: bool = True):
        self.graph = graph
        self.template = template
        self.doc = OsmDocument(frame)
        self.trace = trace
        self.warnings: list[str] = []
        self._spines: dict[str, object] = {}
        self._pending_turnstiles: list = []
        self._levelless: set[str] = set()

    # ---------------- API ----------------

    def build(self) -> OsmDocument:
        self._build_platforms()
        self._build_entrances()
        self._build_extra_ways()
        used = self._build_pathways()
        self.doc.weld()
        self._build_turnstiles()
        missing = self.template.unused_edges(used)
        for edge in missing:
            self.warnings.append(
                f"la plantilla define la arista {edge['from']}->"
                f"{edge['to']} (modo {edge['mode']}, índice "
                f"{edge.get('index', 0)}) pero el grafo no la tiene")
        if not self.trace:
            self.doc.strip_trace(T.TRACE_KEYS)
        return self.doc

    # ---------------- piezas ----------------

    def _trace(self, **kwargs) -> dict:
        return T.trace_tags(**kwargs) if self.trace else {}

    def _level_of(self, stop, pw=None) -> float:
        """Nivel del stop; avisa una vez si la base no lo tiene."""
        if stop.level_index is not None:
            return stop.level_index
        if stop.key not in self._levelless:
            self._levelless.add(stop.key)
            where = f", visto desde el pathway {pw.pathway_id}" if pw else ""
            self.warnings.append(
                f"el stop {stop.stop_id} no tiene nivel en la base{where}; "
                f"se dibuja como si fuera el nivel 0")
        return 0.0

    def _build_platforms(self) -> None:
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_PLATFORM:
                continue
            spec = self.template.node(key)
            u, v = float(spec["u"]), float(spec["v"])
            try:
                length = float(spec["length"])
                width = float(spec["width"])
            except KeyError as exc:
                raise TemplateError(
                    f"el andén {key} de la plantilla "
                    f"{self.template.family} no trae {exc.args[0]}; "
                    f"todo nodo de andén necesita length y width")
            level = self._level_of(stop)
            underground = bool(spec.get("underground", level < 0))
            outline = [
                (u - length / 2, v - width / 2),
                (u + length / 2, v - width / 2),
                (u + length / 2, v + width / 2),
                (u - length / 2, v + width / 2),
            ]
            tags = T.platform_tags(self.graph.station_name, stop.name,
                                   level, stop.level_name, underground)
            tags.update(spec.get("tags", {}))
            tags.update(self._trace(stop_id=stop.stop_id,
                                    miro_id=stop.miro_id))
            self.doc.add_way(outline, tags, [level], kind="platform",
                             label=key, closed=True)
            margin = float(spec.get("spine_margin", 3.0))
            spine_v = v + float(spec.get("spine_v", 0.0))
            spine_pts = [(u - length / 2 + margin, spine_v),
                         (u + length / 2 - margin, spine_v)]
            spine_tags = T.platform_spine_tags(level)
            spine_tags.update(self._trace(stop_id=stop.stop_id))
            self._spines[key] = self.doc.add_way(
                spine_pts, spine_tags, [level], kind="spine", label=key)

    def _build_entrances(self) -> None:
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_ENTRANCE:
                continue
            u, v = self.template.point(key)
            level = self._level_of(stop)
            tags = T.entrance_tags(stop.name, stop.entrance, level)
            tags.update(self._trace(stop_id=stop.stop_id,
                                    miro_id=stop.miro_id))
            self.doc.node_at(u, v, tags)

    def _build_extra_ways(self) -> None:
        """Geometría que la plantilla añade y el grafo no modela.

        Los grafos del relevamiento son topológicos: un vestíbulo es un
        nodo, no una superficie. Para que el .osm sea navegable hacen
        falta tramos de unión (la losa de un puente, el reparto de un
        andén) que se declaran aquí y se marcan como añadidos.
        """
        for spec in self.template.extra_ways:
            points = self.template.resolve_geometry(spec["geometry"])
            levels = [float(x) for x in spec.get("levels", [spec["level"]])]
            tags = T.footway_tags(levels)
            if spec.get("name"):
                tags["name"] = spec["name"]
            tags.update(spec.get("tags", {}))
            self.doc.add_way(points, tags, levels, kind="extra",
                             label=spec.get("name", "extra"))

    def _build_pathways(self) -> set:
        used = set()
        for pw in self.graph.pathways:
            key, spec = self.template.edge(
                pw.from_key, pw.to_key, pw.mode_id, pw.index,
                bidirectional=pw.is_bidirectional)
            if spec is None:
                raise TemplateError(
                    f"la plantilla {self.template.family} no dibuja el "
                    f"pathway {pw.pathway_id} ({pw.from_key}->{pw.to_key}"
                    f", modo {pw.mode_id}, índice {pw.index})")
            used.add(key)
            self._build_pathway(pw, spec)
        return used

    def _build_pathway(self, pw, spec) -> None:
        # La geometría está escrita en el sentido from->to de la
        # plantilla, que puede ser el inverso del que guardó la base.
        from_stop = self.graph.stops[spec["from"]]
        to_stop = self.graph.stops[spec["to"]]
        lf = self._level_of(from_stop, pw)
        lt = self._level_of(to_stop, pw)
        if lf == lt and pw.mode_id in (T.MODE_STAIRS, T.MODE_ESCALATOR):
            self.warnings.append(
                f"el pathway {pw.pathway_id} ({from_stop.stop_id} -> "
                f"{to_stop.stop_id}, modo {pw.mode_id}) une dos stops del "
                f"mismo nivel ({lf:g}); se le puso incline=up por defecto")
        points = self.template.resolve_geometry(
            spec["geometry"], float(spec.get("bow", 0.0)))
        # Bidireccional se dibuja siempre de abajo hacia arriba; el de un
        # solo sentido conserva la flecha que el equipo trazó en Miró.
        reverse = pw.is_bidirectional and lt < lf
        if reverse:
            points = list(reversed(points))
        try:
            tags = T.way_tags_for_pathway(pw.mode_id, pw.is_bidirectional,
                                          lf, lt, reverse)
        except T.UnsupportedModeError as exc:
            raise T.UnsupportedModeError(
                f"pathway {pw.pathway_id} ({pw.from_key}->{pw.to_key}): "
                f"{exc}")
        name = spec.get("name") or self._derive_name(pw, from_stop, to_stop)
        if name:
            tags["name"] = name
        tags.update(spec.get("tags", {}))
        tags.update(self._trace(pathway_id=pw.pathway_id,
                                miro_id=pw.miro_id))
        way = self.doc.add_way(points, tags, [lf, lt],
                               kind=_kind(pw.mode_id),
                               label=f"{pw.from_key}->{pw.to_key}")
        turn = spec.get("turnstile")
        if turn:
            self._pending_turnstiles.append((way, turn, lf, lt))

    def _derive_name(self, pw, from_stop, to_stop) -> str | None:
        """Los pasillos heredan el nombre del nodo que los describe."""
        if pw.mode_id != T.MODE_WALKWAY:
            return None
        for stop in (from_stop, to_stop):
            if stop.name.lower().startswith("pasillo"):
                return stop.name
        return None

    def _build_turnstiles(self) -> None:
        for way, turn, lf, lt in self._pending_turnstiles:
            anchor = self.template.point(turn["from"])
            end_a = self.doc.nodes[way.nodes[0]]
            end_b = self.doc.nodes[way.nodes[-1]]
            line = [(self.doc.nodes[n].u, self.doc.nodes[n].v)
                    for n in way.nodes]
            if (abs(end_b.u - anchor[0]) + abs(end_b.v - anchor[1])
                    < abs(end_a.u - anchor[0]) + abs(end_a.v - anchor[1])):
                line.reverse()
            u, v = point_along_polyline(line,
                                        float(turn.get("distance", 5.0)))
            level = float(turn.get("level", lf if lf == lt else lf))
            self.doc.insert_on_way(way, u, v, T.turnstile_tags(level))


def _kind(mode_id: int) -> str:
    if mode_id == T.MODE_STAIRS:
        return "steps"
    if mode_id == T.MODE_ESCALATOR:
        return "escalator"
    if mode_id == T.MODE_ELEVATOR:
        return "elevator"
    return "footway"
