"""Ensamblado del documento OSM a partir del grafo y de la plantilla."""
from __future__ import annotations

import math

from . import tags as T
from .document import SNAP_TOLERANCE_M, OsmDocument
from .geometry import (LocalFrame, facing_side, opposite_side,
                       point_along_polyline, point_segment_distance,
                       segment_intersection, side_segment, square_corners)
from .graph import StationGraph
from .overpass import CONTEXT_EMBED_M
from .template import FamilyTemplate, TemplateError

LOCATION_PLATFORM = 0
LOCATION_ENTRANCE = 2
LOCATION_GENERIC = 3

# Un acceso se engancha a la red peatonal existente si la tiene a esta
# distancia; más allá, el tramo sería una invención, no una conexión.
CONNECTOR_MAX_M = 40.0
# Para elegir el lado de la puerta y el tamaño de la explanada se mira
# más lejos: la banqueta puede estar fuera del alcance de un connector.
FACING_SEARCH_M = 120.0
DEFAULT_BUILDING_SIDE_M = 12.0

STATION_AREA_MODES = ("kml", "osm", "both", "none")


class StationBuilder:

    def __init__(self, graph: StationGraph, template: FamilyTemplate,
                 frame: LocalFrame, trace: bool = True, context=None,
                 station_area: str | None = None, kml_polygon=None):
        self.graph = graph
        self.template = template
        self.doc = OsmDocument(frame)
        self.trace = trace
        self.context = context
        self.station_area = station_area or template.station_area
        self.kml_polygon = kml_polygon
        self.warnings: list[str] = []
        self.conflicts: list[str] = []
        self.report: dict[str, list] = {"connectors": [], "buildings": [],
                                        "context": [], "streets": []}
        self._spines: dict[str, object] = {}
        self._pending_turnstiles: list = []
        self._levelless: set[str] = set()
        self._entrance_nodes: dict[str, int] = {}
        self._buildings: dict[str, dict] = {}
        self._embedded_ways: dict[int, object] = {}

    # ---------------- API ----------------

    def build(self) -> OsmDocument:
        self._plan_buildings()
        self._build_platforms()
        self._build_entrances()
        self._build_buildings()
        self._build_extra_ways()
        used = self._build_pathways()
        self.doc.weld()
        self._build_turnstiles()
        self._build_connectors()
        self._build_station_area()
        self._build_context_extras()
        self._describe_context()
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
            if float(stop.level_index) != int(stop.level_index):
                raise T.NonIntegerLevelError(
                    f"el stop {stop.stop_id} («{stop.name}») está en el "
                    f"nivel {stop.level_index:g}, que no es entero: "
                    f"`level=*` de OSM no lo puede expresar y redondearlo "
                    f"dibujaría el entrepiso sobre otro nivel. Hay que "
                    f"decidir cómo se mapea el entrepiso antes de exportar "
                    f"esta estación")
            return float(stop.level_index)
        if stop.key not in self._levelless:
            self._levelless.add(stop.key)
            where = f", visto desde el pathway {pw.pathway_id}" if pw else ""
            self.warnings.append(
                f"el stop {stop.stop_id} no tiene nivel en la base{where}; "
                f"se dibuja como si fuera el nivel 0")
        return 0.0

    def _underground(self) -> bool:
        levels = [s.level_index for s in self.graph.stops.values()
                  if s.location_type_id == LOCATION_PLATFORM
                  and s.level_index is not None]
        return bool(levels) and min(levels) < 0

    # ---------------- andenes ----------------

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
            margin = float(spec.get("spine_margin", 0.0))
            spine_v = v + float(spec.get("spine_v", 0.0))
            u0, u1 = u - length / 2, u + length / 2
            spine_pts = [(u0 + margin, spine_v), (u1 - margin, spine_v)]
            # Las dos puntas de la línea de circulación son vértices de
            # los lados cortos del andén: sin eso el polígono y la línea
            # se tocan en pantalla pero no comparten nodo.
            outline = [
                (u0, v - width / 2),
                (u1, v - width / 2),
                (u1, spine_v),
                (u1, v + width / 2),
                (u0, v + width / 2),
                (u0, spine_v),
            ]
            tags = T.platform_tags(self.graph.station_name, stop.name,
                                   level, stop.level_name, underground)
            tags.update(spec.get("tags", {}))
            tags.update(self._trace(stop_id=stop.stop_id,
                                    miro_id=stop.miro_id))
            self.doc.add_way(outline, tags, [level], kind="platform",
                             label=key, closed=True)
            spine_tags = T.platform_spine_tags(level)
            spine_tags.update(self._trace(stop_id=stop.stop_id))
            self._spines[key] = self.doc.add_way(
                spine_pts, spine_tags, [level], kind="spine", label=key)

    # ---------------- accesos y edificios ----------------

    def _plan_buildings(self) -> None:
        """Decide lado de puerta, puertas y explanada de cada edificio.

        Corre antes que nada porque el edificio recoloca dos nodos de la
        plantilla: el acceso pasa a la puerta central y el nodo interior
        al centro del lado opuesto, que es donde arranca la cascada.
        """
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_ENTRANCE:
                continue
            spec = self.template.node(key).get("building")
            if not spec:
                continue
            cu, cv = self.template.point(key)
            half = float(spec.get("side", DEFAULT_BUILDING_SIDE_M)) / 2
            facing = (self.context.nearest_point(cu, cv, FACING_SEARCH_M)
                      if self.context else None)
            side = spec.get("door_side")
            if side is None:
                if facing is None:
                    # Sin contexto no hay banqueta a la que mirar: las
                    # puertas dan a la calle, o sea al lado que se aleja
                    # del eje de la estación.
                    side = "+v" if cv >= 0 else "-v"
                    self.warnings.append(
                        f"el edificio de {key} no tuvo banqueta cercana; "
                        f"las puertas se pusieron al lado {side} por "
                        f"omisión")
                else:
                    side = facing_side(cu, cv, facing[1])
            far = opposite_side(side)
            a, b = side_segment(cu, cv, half, side)
            doors = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                     for f in (0.25, 0.5, 0.75)]
            fa, fb = side_segment(cu, cv, half, far)
            far_mid = ((fa[0] + fb[0]) / 2, (fa[1] + fb[1]) / 2)
            # El medio lado es la distancia perpendicular a la banqueta,
            # no la del vértice más cercano: lo que tiene que caer sobre
            # la banqueta es el borde de la explanada, y el vértice más
            # próximo de una línea paralela queda en diagonal y lo deja
            # corto.
            plaza_half = facing[2] if facing is not None else None
            self.template.overrides[key] = doors[1]
            inner = spec.get("inner_node")
            if inner:
                self.template.overrides[inner] = far_mid
            self._buildings[key] = {
                "centre": (cu, cv), "half": half, "side": side,
                "doors": doors, "far_mid": far_mid, "inner": inner,
                "closed_doors": [int(i) for i in
                                 spec.get("closed_doors", [])],
                "plaza_half": plaza_half,
            }
            self.report["buildings"].append({
                "key": key, "side": side, "half": half,
                "plaza_half": plaza_half, "inner": inner,
                "closed_doors": self._buildings[key]["closed_doors"],
            })

    def _foreign_link(self, stop):
        """Nodo de OSM enlazado en la base, si el contexto lo trajo."""
        if self.context is None or not stop.osm_id:
            return None
        if (stop.osm_type or "node") != "node":
            return None
        node = self.context.nodes.get(stop.osm_id)
        if node is None:
            self.warnings.append(
                f"el stop {stop.stop_id} apunta al nodo OSM {stop.osm_id} "
                f"pero el contexto descargado no lo trae; se dibuja como "
                f"nodo nuevo")
        return node

    def _build_entrances(self) -> None:
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_ENTRANCE:
                continue
            u, v = self.template.point(key)
            level = self._level_of(stop)
            tags = T.entrance_tags(stop.name, stop.entrance, level)
            tags.update(self._trace(stop_id=stop.stop_id,
                                    miro_id=stop.miro_id))
            foreign = self._foreign_link(stop)
            if foreign is None:
                self._entrance_nodes[key] = self.doc.node_at(u, v, tags)
                continue
            # El acceso ya existe en OSM: se reutiliza ese nodo en vez de
            # dibujar un gemelo a diez centímetros.
            nid, conflicts = self.doc.adopt_node(foreign, u, v, tags)
            self._entrance_nodes[key] = nid
            for tag_key, osm_value, ours in conflicts:
                self.conflicts.append(
                    f"{stop.stop_id} (nodo OSM {nid}): {tag_key} vale "
                    f"«{osm_value}» en OSM y nosotros proponíamos "
                    f"«{ours}»; se conservó el de OSM")

    def _build_buildings(self) -> None:
        for key, plan in sorted(self._buildings.items()):
            cu, cv = plan["centre"]
            half = plan["half"]
            door_ids = []
            for i, (du, dv) in enumerate(plan["doors"]):
                if i == 1:
                    door_ids.append(self._entrance_nodes[key])
                    continue
                door_ids.append(self.doc.node_at(
                    du, dv, T.door_tags(i in plan["closed_doors"])))
            if 1 in plan["closed_doors"]:
                node = self.doc.nodes[self._entrance_nodes[key]]
                node.tags.pop("railway", None)
                node.tags["disused:railway"] = "subway_entrance"
            far_id = self.doc.node_at(*plan["far_mid"])
            outline = self._building_outline(cu, cv, half, plan,
                                             door_ids, far_id)
            self.doc.add_way_from_ids(
                outline, T.access_building_tags(), [], kind="building",
                label=f"edificio {key}", closed=True)
            # El tramo interior puerta central → lado opuesto lo dibuja el
            # propio grafo cuando hay un pathway entre el acceso y el nodo
            # interior; si no lo hay, el edificio quedaría sin salida.
            if not (plan["inner"] and self.template.has_edge_between(
                    key, plan["inner"])):
                self.doc.add_way_from_ids(
                    [door_ids[1], far_id], T.footway_tags([0.0]), [0.0],
                    kind="footway", label=f"interior {key}")
            for i in (0, 2):
                self.doc.add_way_from_ids(
                    [door_ids[i], door_ids[1]], T.footway_tags([0.0]),
                    [0.0], kind="footway", label=f"puerta {key}-{i}")
            if plan["plaza_half"]:
                plaza = self.doc.add_way(
                    square_corners(cu, cv, plan["plaza_half"]),
                    T.plaza_tags(), [], kind="plaza",
                    label=f"explanada {key}", closed=True)
                plan["plaza_way"] = plaza

    def _building_outline(self, cu, cv, half, plan, door_ids, far_id):
        """Cuadrado del edificio con puertas y salida como vértices."""
        ids = []
        for corner in square_corners(cu, cv, half):
            ids.append(self.doc.node_at(*corner))
        out = []
        for i in range(4):
            a = self.doc.nodes[ids[i]]
            b = self.doc.nodes[ids[(i + 1) % 4]]
            out.append(ids[i])
            extra = [nid for nid in door_ids + [far_id]
                     if _on_segment(self.doc.nodes[nid], a, b)]
            extra.sort(key=lambda nid: math.hypot(
                self.doc.nodes[nid].u - a.u, self.doc.nodes[nid].v - a.v))
            out += extra
        return out

    # ---------------- contexto y conectores ----------------

    def _embed(self, way):
        if way.osm_id not in self._embedded_ways:
            self._embedded_ways[way.osm_id] = self.doc.add_foreign_way(
                way, self.context)
        return self._embedded_ways[way.osm_id]

    def _build_connectors(self) -> None:
        """Un tramo recto del acceso a cada peatonal existente cercana.

        Se hace uno por way distinta y no solo al más cercano porque en
        una esquina el acceso da a dos banquetas; Ricardo poda en JOSM
        los que sobren, que es más barato que adivinar aquí cuál vale.
        Solo peatonales: si no hay ninguna, el acceso se queda sin
        conectar y se avisa, porque enganchar el acceso al eje de una
        calzada sería peor dato que ninguno.
        """
        if self.context is None:
            return
        for key in sorted(self._entrance_nodes):
            start_id = self._entrance_nodes[key]
            start = self.doc.nodes[start_id]
            plan = self._buildings.get(key, {})
            plaza = plan.get("plaza_way")
            done = set()
            targets = self.context.nearest_vertices(
                start.u, start.v, CONNECTOR_MAX_M)
            if not targets:
                self.warnings.append(
                    f"el acceso {key} no tiene ninguna vía peatonal de OSM "
                    f"a menos de {CONNECTOR_MAX_M:g} m; queda sin connector "
                    f"a la banqueta")
            for way, nid, dist in targets:
                self._embed(way)
                if nid in done:
                    # Dos ways que se cruzan comparten el vértice: un
                    # segundo tramo hasta el mismo nodo sería una copia
                    # exacta del primero y no añade conectividad.
                    self.report["connectors"].append({
                        "key": key, "way": way.osm_id,
                        "highway": way.tags.get("highway"),
                        "footway": way.tags.get("footway"),
                        "length": dist, "vertex": nid, "shared": True,
                        "through_plaza": plaza is not None})
                    continue
                done.add(nid)
                ids = [start_id, nid]
                end = self.doc.nodes[nid]
                if plaza is not None:
                    crossing = self._plaza_crossing(
                        plaza, start_id, nid)
                    if crossing is not None and crossing not in ids:
                        ids.insert(1, crossing)
                self.doc.add_way_from_ids(
                    ids, T.connector_tags(), [0.0], kind="connector",
                    label=f"{key}->{way.osm_id}")
                self.report["connectors"].append({
                    "key": key, "way": way.osm_id,
                    "highway": way.tags.get("highway"),
                    "footway": way.tags.get("footway"),
                    "length": dist, "vertex": nid, "shared": False,
                    "through_plaza": plaza is not None,
                })

    def _plaza_crossing(self, plaza, start_id: int, end_id: int):
        """Nodo compartido donde el connector cruza el borde de la plaza.

        Si el cruce cae encima de una de las dos puntas del connector se
        reutiliza esa punta —incluida la del vértice de banqueta, que es
        ajeno y no se puede mover—: crear ahí un nodo propio dejaría dos
        nodos a centímetros uno del otro sobre la misma línea.
        """
        ends = [(nid, self.doc.nodes[nid]) for nid in (start_id, end_id)]
        a = (ends[0][1].u, ends[0][1].v)
        b = (ends[1][1].u, ends[1][1].v)
        for i in range(len(plaza.nodes) - 1):
            p = self.doc.nodes[plaza.nodes[i]]
            q = self.doc.nodes[plaza.nodes[i + 1]]
            hit = segment_intersection(a, b, (p.u, p.v), (q.u, q.v))
            if hit is None:
                continue
            nid = None
            for end_nid, node in ends:
                if math.hypot(node.u - hit[0],
                              node.v - hit[1]) <= SNAP_TOLERANCE_M:
                    nid = end_nid
                    break
            if nid is None:
                nid = self.doc.node_at(*hit)
            self.doc.insert_node_id(plaza, nid)
            return nid
        return None

    def _build_station_area(self) -> None:
        mode = self.station_area
        if mode not in STATION_AREA_MODES:
            raise TemplateError(
                f"station_area «{mode}» desconocido; usa uno de "
                f"{', '.join(STATION_AREA_MODES)}")
        if mode == "none":
            return
        outlines = self.context.outline_ways() if self.context else []
        if mode in ("kml", "both"):
            self._build_kml_area(mode, outlines)
        if mode in ("osm", "both"):
            if self.context is None:
                self.warnings.append(
                    "station_area pide el contorno de OSM pero se exportó "
                    "sin contexto")
                return
            if not outlines:
                self.warnings.append(
                    "OSM no tiene contorno de estación aquí; el archivo va "
                    "solo con el polígono del KML")
            for way in outlines:
                self._embed(way)

    def _build_kml_area(self, mode: str, outlines) -> None:
        if not self.kml_polygon:
            self.warnings.append(
                "no se pudo leer el polígono KML de la estación; el "
                "archivo va sin área de estación")
            return
        note = None
        if mode == "both":
            # En modo «both» el archivo lleva las dos huellas para que se
            # elija en JOSM; la nota dice cuál es la otra.
            ids = ", ".join(str(w.osm_id) for w in outlines) or "ninguno"
            note = f"candidato KML; comparar con el contorno OSM {ids}"
        points = [self.doc.frame.to_local(lat, lon)
                  for lat, lon in self.kml_polygon]
        tags = T.station_area_tags(self.graph.station_name,
                                   self._underground(), note)
        self.doc.add_way(points, tags, [], kind="station_area",
                         label="área de estación (KML)", closed=True)

    def _build_context_extras(self) -> None:
        """Calles, vías férreas y transporte público del entorno.

        No se conectan a nada y no se tocan: están para que quien abra el
        archivo en JOSM vea la estación dentro de su manzana y no
        flotando. Entra lo que roza la extensión de la estación más 50 m.
        """
        if self.context is None:
            return
        own = [(n.u, n.v) for n in self.doc.nodes.values() if not n.foreign]
        if not own:
            return
        ways, nodes = self.context.scene_elements()
        for way in ways:
            if way.osm_id in self._embedded_ways:
                continue
            if _near_any(self.context.local_line(way), own,
                         CONTEXT_EMBED_M):
                self._embed(way)
        for node in nodes:
            if node.osm_id in self.doc.nodes:
                continue
            if _near_any([self.context.local(node.osm_id)], own,
                         CONTEXT_EMBED_M):
                self.doc.add_foreign_node(node)

    def _describe_context(self) -> None:
        if self.context is None:
            return
        counts: dict[str, int] = {}
        streets = set()
        for way in self.doc.ways:
            if not way.foreign:
                continue
            source = self.context.ways.get(way.id)
            if source is None:
                continue
            kind = self.context.classify(source)
            counts[f"ways: {kind}"] = counts.get(f"ways: {kind}", 0) + 1
            if kind in ("calle", "vía férrea") and source.tags.get("name"):
                streets.add(source.tags["name"])
        for node in self.doc.nodes.values():
            if not (node.foreign and node.tags):
                continue
            source = self.context.nodes.get(node.id)
            if source is None:
                continue
            kind = self.context.classify(source)
            counts[f"nodos: {kind}"] = counts.get(f"nodos: {kind}", 0) + 1
        self.report["context"] = sorted(counts.items())
        self.report["streets"] = sorted(streets)

    # ---------------- resto ----------------

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


def _near_any(points, targets, max_dist: float) -> bool:
    for pu, pv in points:
        for tu, tv in targets:
            if math.hypot(pu - tu, pv - tv) <= max_dist:
                return True
    return False


def _on_segment(node, a, b, tol: float = 0.05) -> bool:
    d, t = point_segment_distance((node.u, node.v), (a.u, a.v), (b.u, b.v))
    return d <= tol and 0.0 < t < 1.0


def _kind(mode_id: int) -> str:
    if mode_id == T.MODE_STAIRS:
        return "steps"
    if mode_id == T.MODE_ESCALATOR:
        return "escalator"
    if mode_id == T.MODE_ELEVATOR:
        return "elevator"
    return "footway"
