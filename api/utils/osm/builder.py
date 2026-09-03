"""Ensamblado del documento OSM a partir del grafo y de la plantilla."""
from __future__ import annotations

import math

from . import tags as T
from .document import SNAP_TOLERANCE_M, OsmDocument
from .geometry import (LocalFrame, band_edges, closest_point_on_ring,
                       distance_to_ring,
                       insert_points_into_ring, overlap_ratio,
                       point_along_polyline, point_in_polygon,
                       point_segment_distance, polygon_centroid,
                       polygon_signed_area, right_of, ring_crossings,
                       ring_sides, segment_intersection, side_index_facing,
                       side_index_for_name, simplify_ring, square_corners,
                       unit)
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
# Un edificio de OSM a esta distancia del acceso es el edificio de ese
# acceso y se adopta en vez de inventar un cuadrado al lado.
BUILDING_ADOPT_M = 10.0
# Vértices de OSM más desviados que esto no son ruido de digitalización:
# el polígono deja de ser un cuadrilátero y no se adopta.
BUILDING_SIMPLIFY_M = 0.5

# Un vértice de andén que hay que correr más que esto para ponerlo sobre
# el anillo del área es un desacuerdo entre plantilla y KML, no un ajuste;
# se suelda igual, pero se avisa.
PLATFORM_SNAP_WARN_M = 3.0
# El largo medido siempre se reporta; solo se avisa cuando discrepa del
# nominal lo bastante para que sea la plantilla la que está mal.
PLATFORM_LENGTH_WARN_M = 2.0
# Si los cruces del anillo con la línea del andén dejan menos que esta
# fracción del largo de la plantilla, el KML no tiene corredor a esa v:
# vale más el largo nominal que un andén truncado que desconecta el grafo.
MIN_RING_LENGTH_RATIO = 0.5

DEFAULT_BANK_SPACING_M = 4.0
DEFAULT_BANK_LEAD_M = 4.0
# Los dos aproches no se pueden comer el tramo: sin este mínimo, un
# banco entre dos nodos cercanos deja las escaleras en un solo punto y
# el way sale con un vértice.
MIN_BANK_STAIR_M = 2.0

STATION_AREA_MODES = ("kml", "osm", "none")


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
                                        "context": [], "streets": [],
                                        "banks": [], "area": [],
                                        "platforms": []}
        self._spines: dict[str, object] = {}
        self._pending_turnstiles: list = []
        self._levelless: set[str] = set()
        self._missing_links: set[str] = set()
        self._entrance_nodes: dict[str, int] = {}
        self._entrance_points: dict[str, tuple[float, float]] = {}
        self._buildings: dict[str, dict] = {}
        self._banks: dict[str, dict] = {}
        self._embedded_ways: dict[int, object] = {}
        # Anillo del KML en metros locales y los vértices de andén que hay
        # que meterle: el área se dibuja al final, pero su forma se
        # decide junto con los andenes.
        self._area_ring: list[tuple[float, float]] | None = None
        self._area_inserts: list[tuple[int, float, tuple]] = []
        self._band: tuple[float, float] | None = None

    # ---------------- API ----------------

    def build(self) -> OsmDocument:
        self._prepare_area()
        self._plan_buildings()
        self._plan_banks()
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
        self.warnings += self.template.bank_warnings
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

    def _prepare_area(self) -> None:
        """Proyecta el anillo del KML antes de dibujar nada.

        El área ya no se emite al final como una figura aparte: delimita
        los andenes y comparte sus vértices, así que su forma tiene que
        estar disponible desde el primer paso.
        """
        if self.station_area not in STATION_AREA_MODES:
            raise TemplateError(
                f"station_area «{self.station_area}» desconocido; usa uno "
                f"de {', '.join(STATION_AREA_MODES)}")
        if self.station_area != "kml":
            return
        if not self.kml_polygon:
            self.warnings.append(
                "no se pudo leer el polígono KML de la estación; el "
                "archivo va sin área de estación y los andenes conservan "
                "el largo de la plantilla")
            return
        self._area_ring = [self.doc.frame.to_local(lat, lon)
                           for lat, lon in self.kml_polygon]
        self._band = band_edges(self._area_ring)
        if self._band is None:
            self.warnings.append(
                "no se pudo medir la franja de andenes del polígono KML; "
                "los andenes que la pidan caen en la v de la plantilla")
            return
        self.report["area"].append(
            f"franja de andenes del KML: v de {self._band[0]:.2f} a "
            f"{self._band[1]:.2f} ({self._band[1] - self._band[0]:.2f} m "
            f"de ancho, eje en v={sum(self._band) / 2:.2f})")

    def _underground(self) -> bool:
        levels = [s.level_index for s in self.graph.stops.values()
                  if s.location_type_id == LOCATION_PLATFORM
                  and s.level_index is not None]
        return bool(levels) and min(levels) < 0

    # ---------------- andenes ----------------

    def _platform_extent(self, key: str, u: float, length: float,
                         v: float, fit: str) -> tuple[float, float]:
        """Puntas del andén, medidas sobre el anillo del área.

        Con `fit` «ring» las puntas son los cruces del anillo con la
        línea del andén: el área tiene el mismo largo que el andén. El
        anillo es una figura ramificada, así que de todos los cruces se
        toman los más cercanos a las puntas que declara la plantilla,
        para no salirse por un pasillo lateral. Con «centred» manda el
        largo de la plantilla y el anillo solo dice dónde centrarlo:
        es el caso en que el área abarca más estación que andén.
        """
        nominal = (u - length / 2, u + length / 2)
        if not self._area_ring:
            return nominal
        crossings = ring_crossings(self._area_ring, v)
        if fit == "centred":
            if len(crossings) < 2:
                self.warnings.append(
                    f"el anillo del área no cruza la línea del andén "
                    f"{key} (v={v:g}); no hay dónde centrar sus "
                    f"{length:g} m y se usa la u de la plantilla")
                return nominal
            middle = (min(crossings) + max(crossings)) / 2
            return middle - length / 2, middle + length / 2
        if fit != "ring":
            raise TemplateError(
                f"el andén {key} declara length_fit «{fit}»; usa ring o "
                f"centred")
        if len(crossings) < 2:
            self.warnings.append(
                f"el anillo del área no cruza la línea del andén {key} "
                f"(v={v:g}) en dos puntos; se conserva el largo de la "
                f"plantilla, {length:g} m")
            return nominal
        u0 = min(crossings, key=lambda c: abs(c - nominal[0]))
        u1 = min(crossings, key=lambda c: abs(c - nominal[1]))
        if u1 - u0 < MIN_RING_LENGTH_RATIO * length:
            self.warnings.append(
                f"el área del KML no tiene corredor a la altura del andén "
                f"{key} (v={v:g}): los cruces más cercanos a sus puntas "
                f"dejan {max(u1 - u0, 0.0):.1f} m contra los {length:g} m "
                f"de la plantilla, así que se conserva el largo nominal")
            return nominal
        if abs((u1 - u0) - length) > PLATFORM_LENGTH_WARN_M:
            self.warnings.append(
                f"el andén {key} sale de {u1 - u0:.1f} m medidos sobre el "
                f"anillo del área, contra los {length:g} m de la "
                f"plantilla")
        return u0, u1

    def _snap_to_area(self, key: str, point) -> tuple[float, float]:
        """Vértice de andén movido al anillo del área y anotado para él.

        La regla es que todo vértice de andén sea también vértice del
        área, sin excepción: donde el desacuerdo es grande se avisa, pero
        el nodo se comparte igual.
        """
        if not self._area_ring:
            return point
        dist, index, t, snapped = closest_point_on_ring(
            self._area_ring, point)
        if dist > PLATFORM_SNAP_WARN_M:
            self.warnings.append(
                f"un vértice del andén {key} estaba a {dist:.1f} m del "
                f"anillo del área y se movió hasta él")
        if not any(math.hypot(p[0] - snapped[0], p[1] - snapped[1]) < 1e-3
                   for _, _, p in self._area_inserts):
            self._area_inserts.append((index, t, snapped))
        return snapped

    def _platform_width(self, key: str, spec: dict) -> float:
        """Ancho del andén, derivado de la franja del KML cuando se puede.

        Ricardo: «cada vía mide 3 metros, 6.5 donde están juntas, igual
        manda el kml». Así que en una estación de dos andenes laterales
        lo que se declara no es el ancho sino el hueco de vías
        (`track_gap`), y el ancho es lo que sobra de la franja repartido
        entre los dos; en una de andén central, `width: "band"` dice que
        el andén ocupa la franja entera porque las vías quedan fuera.
        """
        band = None if self._band is None else self._band[1] - self._band[0]
        gap = spec.get("track_gap")
        if gap is not None:
            if band is None:
                self.warnings.append(
                    f"el andén {key} pide track_gap pero no hay franja "
                    f"medida; se usa el width de la plantilla")
            else:
                return (band - float(gap)) / 2
        raw = spec.get("width")
        if raw == "band":
            if band is None:
                raise TemplateError(
                    f"el andén {key} pide width=\"band\" y no hay franja "
                    f"medida; sin el KML no se puede saber cuánto mide")
            return band
        if raw is None:
            raise TemplateError(
                f"el andén {key} de la plantilla {self.template.family} "
                f"no trae width ni track_gap")
        return float(raw)

    def _platform_v(self, key: str, spec: dict, width: float) -> float:
        """Dónde cae el eje del andén, medido sobre la franja del KML.

        La plantilla dice de qué borde de la franja cuelga el andén, no
        en qué v está: así la misma familia sirve para las hermanas, cuyo
        polígono está en otro sitio respecto del ancla. `v` a secas
        sobrevive como respaldo y como única opción sin KML.
        """
        side = spec.get("band_side")
        if side is None or self._band is None:
            if side is not None:
                self.warnings.append(
                    f"el andén {key} pide band_side={side} pero no hay "
                    f"franja medida; se usa la v de la plantilla")
            if "v" not in spec:
                raise TemplateError(
                    f"el andén {key} de la plantilla "
                    f"{self.template.family} no trae v ni band_side")
            return float(spec["v"])
        inset = float(spec.get("band_inset", width / 2))
        low, high = self._band
        if side == "+v":
            return high - inset
        if side == "-v":
            return low + inset
        if side == "axis":
            return (low + high) / 2 + float(spec.get("band_inset", 0.0))
        raise TemplateError(
            f"el andén {key} declara band_side «{side}»; usa +v, -v o axis")

    def _build_platforms(self) -> None:
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_PLATFORM:
                continue
            spec = self.template.node(key)
            u = float(spec["u"])
            if "length" not in spec:
                raise TemplateError(
                    f"el andén {key} de la plantilla "
                    f"{self.template.family} no trae length")
            length = float(spec["length"])
            width = self._platform_width(key, spec)
            v = self._platform_v(key, spec, width)
            level = self._level_of(stop)
            underground = bool(spec.get("underground", level < 0))
            margin = float(spec.get("spine_margin", 0.0))
            spine_v = v + float(spec.get("spine_v", 0.0))
            fit = spec.get("length_fit", "ring")
            u0, u1 = self._platform_extent(key, u, length, v, fit)
            # Los lados cortos solo son vértices del área cuando el andén
            # llega hasta ella; si el área abarca más estación que andén,
            # las puntas caen dentro y no hay nada a lo que soldarlas.
            snap_ends = fit == "ring"

            def vertex(point, on_ring=True):
                return (self._snap_to_area(key, point)
                        if on_ring else point)

            spine_pts = [vertex((u0 + margin, spine_v), snap_ends),
                         vertex((u1 - margin, spine_v), snap_ends)]
            # Las dos puntas de la línea de circulación son vértices de
            # los lados cortos del andén: sin eso el polígono y la línea
            # se tocan en pantalla pero no comparten nodo.
            outline = [
                vertex((u0, v - width / 2)),
                vertex((u1, v - width / 2)),
                vertex((u1, spine_v), snap_ends),
                vertex((u1, v + width / 2)),
                vertex((u0, v + width / 2)),
                vertex((u0, spine_v), snap_ends),
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
            # Las aristas se cuelgan de la senda con {"spine": …}: sin
            # esto tendrían que traer la v escrita a mano, que es
            # justamente lo que deja de valer en la estación hermana.
            self.template.spine_anchors[key] = spine_v
            self.report["platforms"].append(
                f"{key}: eje v={v:.2f}, ancho {width:g} m, senda "
                f"v={spine_v:.2f}, u de {u0:.1f} a {u1:.1f} "
                f"({u1 - u0:.1f} m; la plantilla decía {length:g})")

    # ---------------- accesos y edificios ----------------

    def _adoptable_building(self, point):
        """Edificio de OSM que ya es el del acceso, o None.

        Se prefiere el más pequeño de los que contienen o rozan el
        acceso: en una manzana mapeada, el pabellón del metro está dentro
        de figuras mayores y el criterio de área es lo que lo distingue.
        """
        if self.context is None:
            return None
        best = None
        for way in sorted(self.context.ways.values(),
                          key=lambda w: w.osm_id):
            if not self.context.is_building(way):
                continue
            if self.context.is_outline(way):
                continue
            ring = self.context.local_line(way)
            if len(ring) > 2 and ring[0] == ring[-1]:
                ring = ring[:-1]
            if len(ring) < 3:
                continue
            if not point_in_polygon(ring, point):
                if distance_to_ring(ring, point) > BUILDING_ADOPT_M:
                    continue
            area = abs(polygon_signed_area(ring))
            if best is None or area < best[0]:
                best = (area, way, ring)
        return None if best is None else (best[1], best[2])

    def _building_shape(self, key: str, spec: dict, point):
        """(anillo, lados, way adoptado o None) del edificio de acceso."""
        found = self._adoptable_building(point)
        if found is not None:
            way, ring = found
            quad = simplify_ring(ring, BUILDING_SIMPLIFY_M)
            if len(quad) == 4:
                return quad, ring_sides(quad)[1], way
            self.warnings.append(
                f"el edificio de OSM {way.osm_id} está sobre el acceso "
                f"{key} pero al podar sus vértices casi colineales quedan "
                f"{len(quad)} lados, no cuatro; se dibuja el cuadrado de "
                f"la plantilla en su lugar")
        half = float(spec.get("side", DEFAULT_BUILDING_SIDE_M)) / 2
        quad = square_corners(point[0], point[1], half)
        return quad, ring_sides(quad)[1], None

    def _plan_buildings(self) -> None:
        """Decide forma, lado de las escaleras, puertas y explanada.

        Corre antes que nada porque el edificio recoloca nodos de la
        plantilla: el nodo interior pasa al centro del edificio y el
        acceso a la puerta que le toca. Modelo: el grafo del relevamiento
        tiene un solo acceso por edificio y el edificio tiene tres
        puertas, así que lo que llega del grafo termina en el centro y
        cada puerta se alcanza por su tramo centro→puerta; el acceso del
        grafo es una de esas tres puertas.
        """
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_ENTRANCE:
                continue
            spec = self.template.node(key).get("building")
            if not spec:
                continue
            anchor = self.template.point(key)
            ring, sides, adopted = self._building_shape(key, spec, anchor)
            centre = polygon_centroid(ring)
            stair_name = spec.get("stair_side")
            if stair_name:
                stair = side_index_for_name(sides, stair_name)
            else:
                # Las escaleras vienen de la estación, así que salen por
                # el lado que mira al origen del marco local.
                stair = side_index_facing(sides, centre, (0.0, 0.0))
            door_sides = [i for i in range(len(sides)) if i != stair]
            doors = [sides[i]["mid"] for i in door_sides]
            facing = (self.context.nearest_point(*centre, FACING_SEARCH_M)
                      if self.context else None)
            entrance = self._entrance_door(key, stop, sides, door_sides,
                                           facing)
            # El medio lado es la distancia perpendicular a la banqueta,
            # no la del vértice más cercano: lo que tiene que caer sobre
            # la banqueta es el borde de la explanada, y el vértice más
            # próximo de una línea paralela queda en diagonal y lo deja
            # corto.
            plaza_half = facing[2] if facing is not None else None
            inner = spec.get("inner_node")
            if inner:
                self.template.overrides[inner] = centre
            # Cuando el grafo ya trae un pathway del nodo interior al
            # acceso, ese pathway es el tramo centro→puerta y no hace
            # falta generarlo; si no lo trae, el acceso del grafo termina
            # en el centro y las tres puertas salen de ahí.
            graph_door = bool(inner and self.template.has_edge_between(
                key, inner))
            self.template.overrides[key] = (
                doors[entrance] if graph_door else centre)
            self._entrance_points[key] = doors[entrance]
            self._buildings[key] = {
                "ring": ring, "sides": sides, "centre": centre,
                "stair_side": stair, "door_sides": door_sides,
                "doors": doors, "entrance": entrance, "inner": inner,
                "graph_door": graph_door, "adopted": adopted,
                "closed_doors": self._closed_doors(key, spec, sides,
                                                   door_sides),
                "plaza_half": plaza_half,
            }
            self.report["buildings"].append({
                "key": key, "side": _side_label(sides[stair]),
                "adopted": adopted.osm_id if adopted else None,
                "sides_m": [round(sides[i]["length"], 1)
                            for i in range(len(sides))],
                "entrance_side": _side_label(sides[door_sides[entrance]]),
                "plaza_half": plaza_half, "inner": inner,
                "closed_doors": self._buildings[key]["closed_doors"],
            })

    def _closed_doors(self, key: str, spec: dict, sides,
                      door_sides) -> list[int]:
        """Puertas clausuradas, por índice o por el lado al que dan.

        El índice depende del orden en que se recorre el edificio y de
        cuál es el lado de las escaleras, así que se admite además el
        rumbo del muro (`"+u"`), que es como se relevó: «la que da al
        norte está cerrada».
        """
        out = []
        for item in spec.get("closed_doors", []):
            if isinstance(item, str):
                index = side_index_for_name(sides, item)
                if index not in door_sides:
                    self.warnings.append(
                        f"el edificio de {key} declara cerrada la puerta "
                        f"del lado {item}, que es el lado por donde salen "
                        f"las escaleras y no tiene puerta")
                    continue
                out.append(door_sides.index(index))
            else:
                out.append(int(item))
        return out

    def _entrance_door(self, key, stop, sides, door_sides, facing) -> int:
        """Cuál de las tres puertas es el acceso que el grafo conoce.

        Manda el nodo que ya existe en OSM: si el relevamiento lo enlazó,
        la puerta señalizada es la del muro al que ese nodo está pegado.
        Sin nodo enlazado se elige la que mira a la banqueta más cercana.
        """
        node = self._foreign_link(stop)
        target = None
        if node is not None:
            target = self.doc.frame.to_local(node.lat, node.lon)
        elif facing is not None:
            target = facing[1]
        if target is None:
            self.warnings.append(
                f"el edificio de {key} no tuvo ni nodo de OSM enlazado ni "
                f"banqueta cercana; el acceso se puso en la primera "
                f"puerta")
            return 0
        best, best_dist = 0, None
        for i, index in enumerate(door_sides):
            side = sides[index]
            dist, _ = point_segment_distance(target, side["a"], side["b"])
            if best_dist is None or dist < best_dist:
                best, best_dist = i, dist
        return best

    def _foreign_link(self, stop):
        """Nodo de OSM enlazado en la base, si el contexto lo trajo."""
        if self.context is None or not stop.osm_id:
            return None
        if (stop.osm_type or "node") != "node":
            return None
        node = self.context.nodes.get(stop.osm_id)
        # El aviso se da una sola vez: el edificio de acceso consulta el
        # enlace al planear la puerta y otra vez al dibujar el nodo.
        if node is None and stop.key not in self._missing_links:
            self._missing_links.add(stop.key)
            self.warnings.append(
                f"el stop {stop.stop_id} apunta al nodo OSM {stop.osm_id} "
                f"pero el contexto descargado no lo trae; se dibuja como "
                f"nodo nuevo")
        return node

    def _build_entrances(self) -> None:
        for key, stop in sorted(self.graph.stops.items()):
            if stop.location_type_id != LOCATION_ENTRANCE:
                continue
            # En un edificio de acceso el nodo va sobre el muro, no donde
            # la plantilla dejó al acceso: ahí queda el centro, que es de
            # donde salen los tres tramos a las puertas.
            u, v = self._entrance_points.get(key) or self.template.point(key)
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
            centre_id = self.doc.node_at(*plan["centre"])
            self.doc.outdoor.add(centre_id)
            door_ids = []
            for i, (du, dv) in enumerate(plan["doors"]):
                if i == plan["entrance"]:
                    door_ids.append(self._entrance_nodes[key])
                    continue
                door_ids.append(self.doc.node_at(
                    du, dv, T.door_tags(i in plan["closed_doors"])))
            if plan["entrance"] in plan["closed_doors"]:
                node = self.doc.nodes[self._entrance_nodes[key]]
                node.tags.pop("railway", None)
                node.tags["disused:railway"] = "subway_entrance"
            self.doc.outdoor.update(door_ids)
            if plan["adopted"] is not None:
                self._adopt_building(key, plan, door_ids)
            else:
                outline = self._building_outline(plan, door_ids)
                self.doc.outdoor.update(outline)
                self.doc.add_way_from_ids(
                    outline, T.access_building_tags(), [], kind="building",
                    label=f"edificio {key}", closed=True)
            for i, door_id in enumerate(door_ids):
                # La puerta del acceso ya está unida al centro por el
                # pathway del grafo cuando la plantilla declara el nodo
                # interior; repetirlo dejaría dos ways idénticos.
                if plan["graph_door"] and i == plan["entrance"]:
                    continue
                self.doc.add_way_from_ids(
                    [door_id, centre_id], T.footway_tags([0.0]), [0.0],
                    kind="building_way", label=f"puerta {key}-{i}")
            if plan["plaza_half"]:
                plaza = self.doc.add_way(
                    square_corners(plan["centre"][0], plan["centre"][1],
                                   plan["plaza_half"]),
                    T.plaza_tags(), [], kind="plaza",
                    label=f"explanada {key}", closed=True)
                self.doc.outdoor.update(plaza.nodes)
                plan["plaza_way"] = plaza

    def _adopt_building(self, key: str, plan: dict, door_ids) -> None:
        """Reusa el edificio que OSM ya tiene, metiéndole las puertas.

        No se le añade `building=yes` ni se le mueve un vértice: lo único
        que cambia es que sus muros llevan ahora los nodos de las puertas.
        """
        way = self._embed(plan["adopted"])
        conflicts, deleted, kept = self.doc.adopt_way(
            way, kind="building", label=f"edificio {key}")
        for door_id in door_ids:
            self.doc.insert_node_id(way, door_id)
        if deleted or kept:
            self.warnings.append(
                f"al adoptar el edificio {way.id} para {key} quedaron "
                f"{len(deleted)} vértices sin uso y {len(kept)} con "
                f"etiquetas propias")
        for tag_key, osm_value, ours in conflicts:
            self.conflicts.append(
                f"edificio {key} (way OSM {way.id}): {tag_key} vale "
                f"«{osm_value}» en OSM y nosotros proponíamos «{ours}»")

    def _building_outline(self, plan, door_ids):
        """Cuadrado de la plantilla con las puertas como vértices."""
        ids = [self.doc.node_at(*corner) for corner in plan["ring"]]
        out = []
        for i in range(len(ids)):
            a = self.doc.nodes[ids[i]]
            b = self.doc.nodes[ids[(i + 1) % len(ids)]]
            out.append(ids[i])
            extra = [nid for nid in door_ids
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
        if mode == "none":
            return
        outlines = self.context.outline_ways() if self.context else []
        if mode == "osm":
            if self.context is None:
                self.warnings.append(
                    "station_area pide el contorno de OSM pero se exportó "
                    "sin contexto")
                return
            if not outlines:
                self.warnings.append(
                    "OSM no tiene contorno de estación aquí y "
                    "station_area=osm no dibuja el polígono del KML; el "
                    "archivo va sin área de estación")
            for way in outlines:
                self._embed(way)
            return
        self._build_kml_area(outlines)

    def _area_node_ids(self, ring) -> list[int]:
        """Nodos del anillo, compartiendo lo que ya está en su sitio.

        Primero manda lo nuestro —los vértices de andén ya colocados—, y
        después un nodo de OSM que ocupe el mismo punto: el KML se
        digitalizó sobre las mismas esquinas de edificio que ya están
        mapeadas, y emitir un gemelo a centímetros sería un error del
        archivo, no del dibujo.
        """
        ids = []
        reused = []
        for u, v in ring:
            nid = None
            for node in self.doc.nodes.values():
                if node.foreign or node.action == "delete":
                    continue
                if math.hypot(node.u - u, node.v - v) <= SNAP_TOLERANCE_M:
                    nid = node.id
                    break
            if nid is None:
                nid = self.doc.reuse_foreign_node(u, v, self.context)
                if nid is not None:
                    reused.append(nid)
            if nid is None:
                nid = self.doc.node_at(u, v)
            ids.append(nid)
        if reused:
            self.report["area"].append(
                f"{len(reused)} vértices del anillo son nodos que ya "
                f"existen en OSM: {', '.join(str(i) for i in reused)}")
        return ids

    def _build_kml_area(self, outlines) -> None:
        if not self._area_ring:
            return
        ring = insert_points_into_ring(self._area_ring, self._area_inserts)
        ids = self._area_node_ids(ring)
        tags = T.station_area_tags(self.graph.station_name,
                                   self._underground())
        if not outlines:
            self.doc.add_way_from_ids(
                ids, tags, [], kind="station_area",
                label="área de estación (KML)", closed=True)
            return
        # El trazo del KML es mejor que el contorno de OSM, así que el
        # contorno se queda con su id y su historia y cambia de forma.
        best = max(outlines, key=lambda w: overlap_ratio(
            ring, self.context.local_line(w)))
        way = self._embed(best)
        conflicts, deleted, kept = self.doc.adopt_way(
            way, tags, ids, kind="station_area",
            label="área de estación (KML sobre el contorno de OSM)")
        self.report["area"].append(
            f"contorno de OSM {way.id} reformado con el polígono del KML: "
            f"{len(ids)} vértices, {len(deleted)} nodos suyos dados de "
            f"baja, {len(kept)} conservados por tener etiquetas")
        for tag_key, osm_value, ours in conflicts:
            self.conflicts.append(
                f"área de estación (way OSM {way.id}): {tag_key} vale "
                f"«{osm_value}» en OSM y nosotros proponíamos «{ours}»; "
                f"se conservó el de OSM")
        for other in outlines:
            if other is best:
                continue
            self._embed(other)
            self.warnings.append(
                f"OSM tiene más de un contorno de estación aquí; el "
                f"{other.osm_id} se embebe congelado y solo el {way.id} "
                f"recibió la forma del KML")

    def _build_context_extras(self) -> None:
        """Banquetas, calles, vías, transporte público, edificios y bardas.

        No se conectan a nada y no se tocan: están para que quien abra el
        archivo en JOSM vea la estación dentro de su manzana y no
        flotando. Entra lo que roza la extensión de la estación más
        `CONTEXT_EMBED_M`. Los contornos de estación no pasan por aquí:
        `_build_station_area` ya los embebió y `scene_elements` los
        excluye, así que ninguno entra dos veces como edificio genérico.
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
            way = self.doc.add_way(points, tags, levels, kind="extra",
                                   label=spec.get("name", "extra"))
            # Los torniquetes de una estación pueden caer en un tramo que
            # el grafo no modela —el vestíbulo de San Pedro solo recibe
            # escaleras, y un torniquete no va sobre `highway=steps`.
            turn = spec.get("turnstile")
            if turn:
                self._pending_turnstiles.append(
                    (way, turn, levels[0], levels[-1]))

    # ---------------- bancos de escaleras ----------------

    def _plan_banks(self) -> None:
        """Eje y nodos de encuentro de cada juego de escaleras paralelas.

        Un tramo de dos, tres o cuatro escaleras que no arranca del andén
        va en paralelo y desemboca por los dos extremos en un solo nodo,
        `lead` metros más allá sobre la línea central: de ahí sigue la
        circulación. Con `axis` explícito las escaleras dejan de ser
        colineales con los nodos del grafo y son los nodos los que se
        mueven al final del eje.
        """
        for bank_id, spec in sorted(self.template.banks.items()):
            from_key, to_key = spec["from"], spec["to"]
            lead = float(spec.get("lead", DEFAULT_BANK_LEAD_M))
            spacing = float(spec.get("spacing", DEFAULT_BANK_SPACING_M))
            axis = spec.get("axis")
            if axis:
                start = (float(axis[0][0]), float(axis[0][1]))
                end = (float(axis[1][0]), float(axis[1][1]))
                direction = unit(start, end)
                junction_from = (start[0] - direction[0] * lead,
                                 start[1] - direction[1] * lead)
                junction_to = (end[0] + direction[0] * lead,
                               end[1] + direction[1] * lead)
                # `place` dice cuál de los dos nodos del grafo se muda al
                # banco. Sin él, dos bancos encadenados se pisarían el
                # nodo que comparten y el edificio perdería su centro.
                place = spec.get("place", ["from", "to"])
                for which, key, point in (("from", from_key, junction_from),
                                          ("to", to_key, junction_to)):
                    if which not in place:
                        continue
                    if key in self.template.overrides:
                        self.warnings.append(
                            f"el banco «{bank_id}» recoloca {key}, que ya "
                            f"había sido recolocado; revisa los `place` de "
                            f"la plantilla")
                    self.template.overrides[key] = point
            else:
                junction_from = self.template.point(from_key)
                junction_to = self.template.point(to_key)
                direction = unit(junction_from, junction_to)
                run = math.hypot(junction_to[0] - junction_from[0],
                                 junction_to[1] - junction_from[1])
                if run - 2 * lead < MIN_BANK_STAIR_M:
                    clamped = max(0.0, (run - MIN_BANK_STAIR_M) / 2)
                    self.warnings.append(
                        f"el banco «{bank_id}» pide {lead:g} m de aproche "
                        f"en cada punta sobre un tramo de {run:.1f} m; se "
                        f"recortaron a {clamped:.1f} m para que las "
                        f"escaleras midan algo")
                    lead = clamped
                start = (junction_from[0] + direction[0] * lead,
                         junction_from[1] + direction[1] * lead)
                end = (junction_to[0] - direction[0] * lead,
                       junction_to[1] - direction[1] * lead)
            self._banks[bank_id] = {
                "from": from_key, "to": to_key, "start": start, "end": end,
                "junction_from": junction_from, "junction_to": junction_to,
                "spacing": spacing, "lead": lead,
                "right": right_of(direction),
            }
            self.report["banks"].append({
                "id": bank_id, "from": from_key, "to": to_key,
                "spacing": spacing, "lead": lead,
                "explicit_axis": bool(axis),
            })

    def _bank_segment(self, spec: dict, layout) -> tuple[dict, tuple, tuple]:
        """(banco, punta del lado `from`, punta del lado `to`) del tramo."""
        bank_id, slot, count = layout
        bank = self._banks[bank_id]
        offset = bank["spacing"] * (slot - (count - 1) / 2)
        ru, rv = bank["right"]
        start = (bank["start"][0] + ru * offset,
                 bank["start"][1] + rv * offset)
        end = (bank["end"][0] + ru * offset, bank["end"][1] + rv * offset)
        if spec["from"] == bank["to"]:
            return bank, end, start
        return bank, start, end

    def _build_bank_joins(self, spec, bank, tips, lf, lt) -> None:
        """Tramos cortos de cada escalera al nodo de encuentro del banco."""
        junctions = (bank["junction_from"], bank["junction_to"])
        if spec["from"] == bank["to"]:
            junctions = (bank["junction_to"], bank["junction_from"])
        for junction, tip, level, end in zip(junctions, tips, (lf, lt),
                                             ("from", "to")):
            self.doc.add_way(
                [junction, tip], T.footway_tags([level]), [level],
                kind="footway",
                label=f"{spec['from']}->{spec['to']} {end}")

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
        layout = self.template.bank_layout(spec)
        bank = tips = None
        if layout is None:
            points = self.template.resolve_geometry(
                spec["geometry"], float(spec.get("bow", 0.0)))
        else:
            bank, tip_from, tip_to = self._bank_segment(spec, layout)
            tips = (tip_from, tip_to)
            points = [tip_from, tip_to]
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
        if bank is not None:
            self._build_bank_joins(spec, bank, tips, lf, lt)
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
            # El ancla dice desde qué punta se mide; en un extra_way, que
            # no tiene nodos del grafo, se admite el punto suelto.
            origin = turn["from"]
            anchor = (self.template.point(origin) if isinstance(origin, str)
                      else (float(origin[0]), float(origin[1])))
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


def _side_label(side) -> str:
    """Rumbo de un lado en las direcciones del marco local, para el aviso."""
    nu, nv = side["normal"]
    if abs(nu) >= abs(nv):
        return "+u" if nu >= 0 else "-u"
    return "+v" if nv >= 0 else "-v"


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
