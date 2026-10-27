"""Ensamblado del documento OSM a partir del grafo y de la plantilla."""
from __future__ import annotations

import math
from collections import Counter

from . import arms as A
from . import fit as F
from . import tags as T
from .document import SNAP_TOLERANCE_M, OsmDocument
from .geometry import (LocalFrame, band_edges, closest_point_on_rings,
                       distance_to_ring,
                       insert_points_into_ring, overlap_ratio,
                       point_along_polyline, point_in_polygon,
                       point_in_polygon_tol, point_segment_distance,
                       polygon_centroid,
                       polygon_signed_area, right_of, ring_crossings,
                       ring_sides, segment_intersection, side_index_facing,
                       side_index_for_name, simplify_ring,
                       split_pinched_ring, square_corners, unit)
from .graph import StationGraph
from .kml import fold_name
from .overpass import CONTEXT_EMBED_M
from .template import FamilyTemplate, TemplateError

LOCATION_PLATFORM = 0
LOCATION_ENTRANCE = 2
LOCATION_GENERIC = 3

# Un acceso se engancha a la red peatonal existente si la tiene a esta
# distancia; más allá, el tramo sería una invención, no una conexión.
# Los connectors que Ricardo trazó en San Pedro al cruce de la Avenida
# Revolución miden unos 42.5 y 44.7 m en su archivo (41.2 y 42.1 m los
# generados).
CONNECTOR_MAX_M = 45.0
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
# Un `building=transportation|train_station` que comparte con el área del
# KML menos que esto (intersección sobre unión) no es el contorno de la
# estación sino un pabellón de acceso: en San Joaquín los dos pabellones
# dan 0.05 y el contorno de Portales 0.71.
OUTLINE_MIN_IOU = 0.25
# Un edificio es pabellón de una cascada si al menos esta fracción de su
# planta cae dentro del área del KML: la salida está debajo de él.
PAVILION_MIN_INSIDE = 0.5
# Una entrada `railway=subway_entrance` de OSM dentro del pabellón, o a
# esta distancia de sus muros, es la entrada de ese pabellón aunque la
# base no la tenga enlazada.
ENTRANCE_ADOPT_M = 2.0
# Lo más que un edificio de OSM que usa la estación puede sobresalir del
# área para que el generador lo meta moviendo sus vértices. Es la
# tolerancia de dos dibujos de manos distintas sobre la misma esquina
# (`FOREIGN_REUSE_M`); más allá ya es una discrepancia que se revisa.
BUILDING_FIT_MAX_M = 0.5
# Una puerta a esta distancia del anillo de una explanada de OSM está
# sobre su borde: se mete como vértice suyo y queda conectada.
PLAZA_DOOR_M = 0.3
# El nodo de estación no se encima en un nodo nuestro: si cae más cerca
# que esto, se corre sobre el eje hasta despejarlo.
STATION_NODE_CLEAR_M = 1.0
# Margen con el que el encaje juzga que un punto cabe en el área; el
# mismo que usa la validación.
FIT_TOLERANCE_M = 0.3
# Si ninguna orientación cabe con los largos de la plantilla, se acortan
# las cascadas a lo largo de su eje en estos pasos antes de rendirse.
FIT_SCALES = (0.95, 0.9, 0.85, 0.8, 0.75, 0.7)

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
# Un banco apilado encima de otro se corre de lado para que en JOSM se
# vean las dos capas; tiene que quedar holgado sobre SNAP_TOLERANCE_M.
DEFAULT_STACK_OFFSET_M = 1.0
# Criterio general del trazo: ninguna línea a menos de unos 0.3 m de una
# línea de otro nivel. Sigue por encima de SNAP_TOLERANCE_M, así que no
# hay pegado.
MIN_STACK_CLEARANCE_M = 0.3
# Los dos aproches no se pueden comer el tramo: sin este mínimo, un
# banco entre dos nodos cercanos deja las escaleras en un solo punto y
# el way sale con un vértice.
MIN_BANK_STAIR_M = 2.0

STATION_AREA_MODES = ("kml", "osm", "none")


class StationBuilder:

    def __init__(self, graph: StationGraph, template: FamilyTemplate,
                 frame: LocalFrame, trace: bool = True, context=None,
                 station_area: str | None = None, kml_polygon=None,
                 context_radius: float = CONTEXT_EMBED_M):
        self.graph = graph
        self.context_radius = context_radius
        self.template = template
        self.doc = OsmDocument(frame)
        self.trace = trace
        self.context = context
        self.station_area = station_area or template.station_area
        self.kml_polygon = kml_polygon
        self.warnings: list[str] = []
        self.conflicts: list[str] = []
        # Lo que impide dar el archivo por bueno sin ser un fallo de la
        # plantilla: el command lo junta con los errores de validación.
        self.errors: list[str] = []
        self.report: dict[str, list] = {"connectors": [], "buildings": [],
                                        "context": [], "streets": [],
                                        "banks": [], "area": [],
                                        "platforms": [], "fit": [],
                                        "station": [], "osm": [],
                                        "untemplated": []}
        self._missing_nodes: dict[str, str] = {}
        self._fit_pavilions: dict[str, tuple] = {}
        self._auto_links: dict[str, object] = {}
        self._spines: dict[str, object] = {}
        self._pending_turnstiles: list = []
        self._levelless: set[str] = set()
        self._missing_links: set[str] = set()
        self._entrance_nodes: dict[str, int] = {}
        self._entrance_points: dict[str, tuple[float, float]] = {}
        self._buildings: dict[str, dict] = {}
        self._banks: dict[str, dict] = {}
        self._slots: dict[int, tuple[int, int]] = {}
        self._embedded_ways: dict[int, object] = {}
        # Anillos del KML en metros locales —exterior primero, después las
        # islas— y los vértices de andén que hay que meterles, con el
        # anillo al que van: el área se dibuja al final, pero su forma se
        # decide junto con los andenes.
        self._area_rings: list[list[tuple[float, float]]] | None = None
        self._area_inserts: list[tuple[int, int, float, tuple]] = []
        self._band: tuple[float, float] | None = None

    # ---------------- API ----------------

    def build(self) -> OsmDocument:
        self._prepare_area()
        self._fit_template()
        self._link_declared_entrances()
        self._plan_buildings()
        self._plan_banks()
        self._place_missing_nodes()
        self._build_platforms()
        self._build_entrances()
        self._build_buildings()
        self._fit_buildings_in_area()
        self._build_extra_ways()
        used = self._build_pathways()
        self.doc.weld()
        self._build_turnstiles()
        self._build_connectors()
        self._build_station_area()
        self._build_context_extras()
        self._place_station_node()
        self._describe_context()
        kept = self.doc.settle_deletes()
        if kept:
            self.report["osm"].append(
                f"{len(kept)} nodos de OSM que se iban a dar de baja siguen "
                f"en uso por otro way del archivo y se conservan: "
                + ", ".join(str(nid) for nid in sorted(kept)))
        self.warnings += self.template.bank_warnings
        self.warnings += self.template.route_warnings
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
        override = self.template.area_override
        if override:
            self._area_rings = self._override_rings(override)
            pinches = None
        elif not self.kml_polygon:
            self.warnings.append(
                "no se pudo leer el polígono KML de la estación; el "
                "archivo va sin área de estación y los andenes conservan "
                "el largo de la plantilla")
            return
        else:
            ring = [self.doc.frame.to_local(lat, lon)
                    for lat, lon in self.kml_polygon]
            try:
                self._area_rings, pinches = split_pinched_ring(ring)
            except ValueError as exc:
                raise TemplateError(f"polígono KML de la estación: {exc}")
        if pinches:
            self.report["area"].append(
                f"{len(pinches)} pellizcos del KML (cortes de ancho cero, "
                f"el más abierto a {max(pinches):.2f} m) separados en un "
                f"contorno y {len(self._area_rings) - 1} islas: el área "
                f"sale como multipolígono con anillos inner")
        self._demote_pavilion_outlines()
        self._band = band_edges(self._area_rings)
        if self._band is None:
            self.warnings.append(
                "no se pudo medir la franja de andenes del polígono KML; "
                "los andenes que la pidan caen en la v de la plantilla")
            return
        self.report["area"].append(
            f"franja de andenes del KML: v de {self._band[0]:.2f} a "
            f"{self._band[1]:.2f} ({self._band[1] - self._band[0]:.2f} m "
            f"de ancho, eje en v={sum(self._band) / 2:.2f})")

    def _override_rings(self, override: dict):
        """Anillos del área que el bloque de la estación trae en lat/lon.

        Es la corrección a mano del KML que la estación ya aprobó: va en
        coordenadas y no en metros para no depender del rumbo con que se
        genere. Sin los vértices de andén, que el generador vuelve a meter.
        """
        def ring(points):
            return [self.doc.frame.to_local(float(lat), float(lon))
                    for lat, lon in points]
        rings = [ring(override["outer"])]
        rings += [ring(r) for r in override.get("inner", [])]
        if any(len(r) < 3 for r in rings):
            raise TemplateError(
                f"el área del bloque de {self.template.station} trae un "
                f"anillo de menos de tres vértices")
        self.report["area"].append(
            f"área del bloque de {self.template.station}, no del KML: "
            f"outer de {len(rings[0])} vértices y {len(rings) - 1} islas"
            + (f" ({override['source']})" if override.get("source") else ""))
        return rings

    def _demote_pavilion_outlines(self) -> None:
        """Un «contorno de estación» chico es el pabellón de un acceso.

        En San Joaquín los dos pabellones están mapeados como
        `building=transportation`, la etiqueta de los contornos; tomarlos
        por contorno los reformaría con el KML y daría de baja nodos del
        pabellón. Ricardo: «Te inventaste los edificios de entrada en
        lugar de respetar los que ya tenía bien establecidos
        openStreetMap». Lo que distingue a uno de otro es cuánto comparte
        con el área de la estación.
        """
        if self.context is None:
            return
        for way in sorted(self.context.ways.values(),
                          key=lambda w: w.osm_id):
            if not self.context.has_outline_tags(way):
                continue
            ring = self.context.local_line(way)
            if len(ring) > 2 and ring[0] == ring[-1]:
                ring = ring[:-1]
            if len(ring) < 3:
                continue
            iou = overlap_ratio(self._area_rings, ring)
            if iou >= OUTLINE_MIN_IOU:
                continue
            self.context.demoted.add(way.osm_id)
            if iou > 0:
                self.report["area"].append(
                    f"el way {way.osm_id} (building="
                    f"{way.tags.get('building', '—')}) comparte "
                    f"{iou:.0%} con el área del KML: se trata como "
                    f"pabellón de acceso, no como contorno de estación")

    def _underground(self) -> bool:
        levels = [s.level_index for s in self.graph.stops.values()
                  if s.location_type_id == LOCATION_PLATFORM
                  and s.level_index is not None]
        return bool(levels) and min(levels) < 0

    # ---------------- encaje en el área ----------------

    def _fit_template(self) -> None:
        """Ajusta la plantilla al KML de esta estación antes de dibujar.

        La plantilla es el trazo de su estación de referencia. Aquí se
        deforman los corredores hacia los ramales medidos y cada cascada
        se mueve en bloque a la orientación que cabe en el área, anclada
        al pabellón de OSM; en la propia estación de referencia todo
        coincide y la plantilla queda intacta.
        """
        spec = self.template.fit
        data = self.template.data
        arms = data.get("arms")
        if spec and self._area_rings and self._band is not None:
            groups = [self._cascade_group(name, raw) for name, raw
                      in sorted(spec.get("cascades", {}).items())]
            warp = self._corridor_warp(spec)
            if warp is not None:
                in_cascade = self._cascade_membership(groups)
                data = F.warp_template_data(data, warp, in_cascade)
            for group in groups:
                data = self._fit_cascade(data, group, warp)
        elif not self.template.local_patch and not arms:
            self.template.area_rings = self._area_rings
            return
        # Los hechos de la estación escritos en su propio marco van
        # encima de lo que el encaje decidió: son lo que su versión
        # aprobada corrigió a mano.
        old = self.template
        data = old.apply_local_patch(data)
        if old.local_patch:
            self.report["fit"].append(
                f"bloque de {old.station}: piezas «local» aplicadas sobre el "
                f"encaje ({', '.join(sorted(old.local_patch))})")
        if arms:
            # Después del bloque local, para que también él pueda nombrar
            # los brazos en vez de escribir sus u.
            data = self._resolve_arms(data, arms)
        self.template = FamilyTemplate(data, old.path)
        self.template.station = old.station
        self.template.area_override = old.area_override
        self.template.area_rings = self._area_rings

    def _resolve_arms(self, data: dict, spec: dict) -> dict:
        """Plantilla con los brazos del puente y los lóbulos medidos.

        Las puertas que la plantilla ubica en la cara de un lóbulo quedan
        sobre el anillo del área, y se anotan para que el área las tome
        como vértices: el pabellón es el lóbulo, y su puerta es un punto
        de su muro.
        """
        if not self._area_rings or self._band is None:
            raise TemplateError(
                f"la plantilla {self.template.family} nombra los brazos del "
                f"área (`arm`) y esta exportación no tiene área de estación "
                f"ni franja medida")
        probe = float(spec.get("probe", A.DEFAULT_ARM_PROBE_M))
        try:
            arms = A.measure_arms(self._area_rings[0], self._band, probe)
            data, doors = A.resolve_arm_refs(data, arms)
        except A.ArmError as exc:
            raise TemplateError(f"brazos del área: {exc}")
        for side, arm in sorted(arms.items()):
            self.report["fit"].append(
                f"brazo {side}: eje en u={arm.axis_u:.2f} (u de "
                f"{arm.span[0]:.2f} a {arm.span[1]:.2f}); lóbulo de u "
                f"{arm.lobe[0]:.2f} a {arm.lobe[1]:.2f} y v {arm.face_v:.2f}"
                f" a {arm.wall_v:.2f} ({arm.lobe[1] - arm.lobe[0]:.1f} × "
                f"{abs(arm.wall_v - arm.face_v):.1f} m); puerta en "
                f"({arm.door[0]:.2f}, {arm.door[1]:.2f})")
        for key in doors:
            spec_node = data["nodes"][key]
            self._snap_to_area(key, (spec_node["u"], spec_node["v"]))
        return data

    def _cascade_group(self, name: str, raw: dict) -> dict:
        nodes = set()
        for bank_id in raw["banks"]:
            bank = self.template.bank(bank_id)
            nodes |= {bank["from"], bank["to"]}
        building_key = raw.get("building")
        inner = None
        if building_key:
            nodes.add(building_key)
            building = self.template.node(building_key).get("building", {})
            inner = building.get("inner_node")
            if inner:
                nodes.add(inner)
        return {"name": name, "banks": list(raw["banks"]),
                "side": raw.get("side", "+v"), "building": building_key,
                "inner": inner, "nodes": nodes,
                "anchor": (float(raw["anchor"][0]), float(raw["anchor"][1]))}

    @staticmethod
    def _cascade_membership(groups):
        nodes = set().union(*(g["nodes"] for g in groups)) if groups else set()

        def member(kind, item) -> bool:
            if kind == "node":
                return item in nodes
            if item.get("bank"):
                return True
            return {item["from"], item["to"]} <= nodes
        return member

    def _corridor_warp(self, spec: dict):
        """Deformación de los corredores, o None si no hace falta."""
        reference = spec["reference"]
        probe = float(spec.get("branch_probe", F.DEFAULT_BRANCH_PROBE_M))
        tolerance = float(spec.get("tolerance", F.DEFAULT_WARP_TOLERANCE_M))
        target = F.measure(self._area_rings, self._band, probe)
        worst, why = F.compare_measures(reference, target)
        if math.isinf(worst):
            self.warnings.append(
                f"no se pudo medir el KML como el de la estación de "
                f"referencia ({why}); los corredores van tal como los trae "
                f"la plantilla")
            return None
        fmt = ", ".join
        self.report["fit"].append(
            "ramales del KML: oriente "
            + fmt(f"{u:.1f}" for u in target["branches"]["+v"])
            + "; poniente "
            + fmt(f"{u:.1f}" for u in target["branches"]["-v"])
            + f"; vestíbulos transversales en v="
            f"{target['transversal']['+v']:.1f} y "
            f"{target['transversal']['-v']:.1f} (la referencia: "
            + fmt(f"{u:.1f}" for u in reference["branches"]["+v"])
            + f"; {reference['transversal']['+v']:.1f} y "
            f"{reference['transversal']['-v']:.1f})")
        if worst <= tolerance:
            self.report["fit"].append(
                f"corredores: el KML coincide con la referencia (máximo "
                f"{worst:.1f} m), la plantilla va tal cual")
            return None
        ref_branches = F.mean_branches(reference)
        target_branches = F.mean_branches(target)
        self.report["fit"].append(
            f"corredores deformados (el KML se aparta hasta {worst:.1f} m): "
            "ramales en u "
            + fmt(f"{a:.1f}→{b:.1f}" for a, b in zip(ref_branches,
                                                     target_branches)))
        return F.CorridorWarp(ref_branches, target_branches,
                              reference["band"], self._band,
                              reference["transversal"],
                              target["transversal"])

    def _cascade_pavilion(self, group: dict):
        """(way, cuadrilátero) del pabellón de OSM bajo el que sale la
        cascada, o None.

        Es el edificio que cae casi entero dentro del área del KML y del
        lado de la franja que le toca: la salida de la estación está
        debajo de él. Si hay más de uno, el de más superficie dentro.
        """
        if self.context is None:
            return None
        best = None
        for way in sorted(self.context.ways.values(),
                          key=lambda w: w.osm_id):
            if (not self.context.is_building(way)
                    or self.context.is_outline(way)):
                continue
            ring = self.context.local_line(way)
            if len(ring) > 2 and ring[0] == ring[-1]:
                ring = ring[:-1]
            if len(ring) < 3:
                continue
            quad = simplify_ring(ring, BUILDING_SIMPLIFY_M)
            if len(quad) != 4:
                continue
            centre = polygon_centroid(quad)
            if group["side"] == "+v" and centre[1] <= self._band[1]:
                continue
            if group["side"] == "-v" and centre[1] >= self._band[0]:
                continue
            share = F.inside_fraction(quad, self._area_rings)
            if share < PAVILION_MIN_INSIDE:
                continue
            area = abs(polygon_signed_area(quad)) * share
            if best is None or area > best[0]:
                best = (area, way, quad)
        return None if best is None else (best[1], best[2])

    def _fit_cascade(self, data: dict, group: dict, warp) -> dict:
        """Mueve la cascada a la orientación que cabe en el área.

        Primero se prueba tal como la dibuja la plantilla; si no cabe, las
        ocho simetrías del cuadrado ancladas al pabellón de OSM, y si
        tampoco, las mismas con la cascada acortada. Entre las que caben:
        la que no pone las escaleras contra la puerta que OSM ya tiene,
        la paralela a las vías como en San Pedro, la de aproche más corto.
        """
        found = self._cascade_pavilion(group)
        if found is not None and group["building"]:
            self._fit_pavilions[group["building"]] = found
        ref_anchor = group["anchor"]
        entrance = self._declared_entrance_point(group["building"])
        if found is not None:
            target_anchor = polygon_centroid(found[1])
        elif entrance is not None:
            # Sin pabellón, el punto fijo de la salida es la entrada que
            # OSM ya tiene: la cascada se lleva a ella.
            target_anchor = entrance
        elif warp is not None:
            target_anchor = tuple(warp.point(ref_anchor))
        else:
            target_anchor = ref_anchor
        first = data["banks"][group["banks"][0]]
        du, dv = F.direction_vector(first.get("direction", "+u"))
        axis = (abs(du), abs(dv))
        moves = [(F.RigidMove(F.DIHEDRAL[0][0], ref_anchor, ref_anchor,
                              axis), "tal como la dibuja la plantilla")]
        if found is None and entrance is not None:
            # Tal como está, la escalera a la calle no llega a la entrada.
            moves = []
        for scale in (1.0,) + FIT_SCALES:
            for matrix, label in F.DIHEDRAL:
                moves.append((F.RigidMove(matrix, ref_anchor, target_anchor,
                                          axis, scale), label))
        tried = []
        chosen = None
        for index, (move, label) in enumerate(moves):
            scale = move.scale
            if chosen is not None and scale != chosen[0]["move"].scale:
                break
            result = self._try_cascade(data, group, move, found)
            result.update({"move": move, "label": label, "index": index})
            tried.append(result)
            if result["move"].identity and result["fits"]:
                chosen = [result]
                break
            if result["fits"] and not result["move"].identity:
                chosen = (chosen or []) + [result]
        name = group["name"]
        if chosen is None and self._placed_locally(group):
            # La estación coloca la cascada en su propio marco: lo que el
            # encaje no logró no llega al archivo, y la regla del área la
            # vuelve a juzgar la validación sobre lo que sí se dibuja.
            best = min(tried, key=lambda r: (len(r["outside"]),
                                             r["worst"]))
            self.report["fit"].append(
                f"cascada {name}: el encaje no la acomoda (la mejor, "
                f"{best['label']}, deja {len(best['outside'])} puntos "
                f"fuera), pero el bloque «local» de {self.template.station} "
                f"coloca todos sus bancos")
            return data
        if chosen is None:
            best = min(tried, key=lambda r: (len(r["outside"]),
                                             r["worst"]))
            self.errors.append(
                f"la cascada {name} no cabe en el área del KML en ninguna "
                f"orientación ni acortada al {FIT_SCALES[-1]:.0%}: la "
                f"mejor ({best['label']}) deja {len(best['outside'])} "
                f"puntos fuera, hasta {best['worst']:.1f} m")
            pick = best
        else:
            pick = min(chosen, key=lambda r: (
                not r["move"].identity, r["door_clash"], not r["parallel"],
                r["approach"], F.matrix_det(r["move"].matrix) < 0,
                r["index"]))
        self._report_cascade(group, pick, tried, found)
        return pick["data"]

    def _placed_locally(self, group: dict) -> bool:
        """¿El bloque `local` de la estación da posición a todos los
        bancos de la cascada?"""
        banks = (self.template.local_patch or {}).get("banks") or {}
        return all((banks.get(b) or {}).get("junction")
                   or (banks.get(b) or {}).get("axis")
                   for b in group["banks"])

    def _declared_entrance_point(self, key):
        """Posición de la entrada de OSM que la plantilla enlaza al acceso
        `key` con `osm_node`, o None."""
        if not key or self.context is None:
            return None
        osm_id = (self.template.nodes.get(key) or {}).get("osm_node")
        if osm_id is None or int(osm_id) not in self.context.nodes:
            return None
        return self.context.local(int(osm_id))

    def _try_cascade(self, data: dict, group: dict, move, pavilion) -> dict:
        """Planea la cascada movida en una copia y mide si cabe."""
        moved = F.move_cascade(data, group, move)
        template = FamilyTemplate(moved, self.template.path)
        template.area_rings = self._area_rings
        trial = StationBuilder(self.graph, template, self.doc.frame,
                               trace=False, station_area="none")
        trial._plan_banks()
        points = []
        count = Counter(e.get("bank") for e in template.edges)
        for bank_id in group["banks"]:
            bank = trial._banks[bank_id]
            n = count.get(bank_id, 0)
            ru, rv = bank["slot_right"]
            for k in range(n):
                off = bank["spacing"] * (k - (n - 1) / 2)
                # La escalera entera, no solo sus puntas: en San Antonio
                # las dos puntas caían dentro y el tramo cruzaba un hueco
                # del área.
                points += F.sample_segment(
                    (bank["start"][0] + ru * off, bank["start"][1] + rv * off),
                    (bank["end"][0] + ru * off, bank["end"][1] + rv * off))
            points += [bank["junction_from"], bank["junction_to"]]
        approach = 0.0
        for extra in template.extra_ways:
            via = any(isinstance(i, dict) and i.get("cascade") == (
                group["name"]) for i in extra["geometry"])
            if extra.get("cascade") != group["name"] and not via:
                continue
            try:
                line = template.resolve_geometry(extra["geometry"])
            except TemplateError:
                continue
            if via:
                approach = sum(math.hypot(b[0] - a[0], b[1] - a[1])
                               for a, b in zip(line, line[1:]))
                for a, b in zip(line, line[1:]):
                    points += F.sample_segment(a, b)
            else:
                points += line
        hub = template.overrides.get(group["inner"]) if group["inner"] else (
            None)
        entrance = self._declared_entrance_point(group["building"])
        if entrance is not None:
            # La escalera que desemboca en la entrada de OSM llega a la
            # calle: esa punta está afuera por definición.
            points = [p for p in points if math.hypot(
                p[0] - entrance[0], p[1] - entrance[1]) > SNAP_TOLERANCE_M]
        outside = F.outside_points(self._area_rings, points, FIT_TOLERANCE_M)
        hub_ok = True
        door_clash = False
        if pavilion is not None and hub is not None:
            hub_ok = point_in_polygon_tol(pavilion[1], hub,
                                          FIT_TOLERANCE_M)[0]
            door_clash = self._stairs_on_entrance(
                template, group["building"], pavilion[1])
        axis = move.vector(move.axis)
        return {"data": moved, "outside": outside,
                "worst": max((d for d, _ in outside), default=0.0),
                "fits": not outside and hub_ok, "hub_ok": hub_ok,
                "door_clash": door_clash, "approach": approach,
                "parallel": abs(axis[0]) > abs(axis[1]), "trial": trial}

    def _stairs_on_entrance(self, template, key: str, quad) -> bool:
        """¿Las escaleras entran por el muro donde OSM ya tiene la puerta?"""
        spec = template.node(key).get("building", {})
        name = spec.get("stair_side")
        if not name or self.context is None:
            return False
        sides = ring_sides(quad)[1]
        stair = side_index_for_name(sides, name)
        for node in self.context.subway_entrances():
            p = self.context.local(node.osm_id)
            if not (point_in_polygon(quad, p) or distance_to_ring(
                    quad, p) <= ENTRANCE_ADOPT_M):
                continue
            nearest = min(range(len(sides)), key=lambda i: (
                point_segment_distance(p, sides[i]["a"], sides[i]["b"])[0]))
            if nearest == stair:
                return True
        return False

    def _report_cascade(self, group, pick, tried, pavilion) -> None:
        move = pick["move"]
        entrance = self._declared_entrance_point(group["building"])
        if pick["move"].identity:
            where = (f"sin moverla (pabellón {pavilion[0].osm_id})"
                     if pavilion else "sin moverla")
        elif pavilion:
            where = f"anclada al pabellón {pavilion[0].osm_id}"
        elif entrance is not None:
            where = "sin pabellón de OSM: anclada a la entrada de OSM"
        else:
            where = "sin pabellón de OSM: anclada donde la plantilla"
        if not pick["fits"]:
            why = (f"no cabe: es la que menos se sale, "
                   f"{len(pick['outside'])} puntos fuera, hasta "
                   f"{pick['worst']:.1f} m")
        elif pick["move"].identity:
            why = "cabe íntegra en el área"
        else:
            reasons = ["cabe íntegra en el área"]
            if not pick["door_clash"]:
                reasons.append("las escaleras no entran por el muro de la "
                               "puerta que OSM ya tiene")
            if pick["parallel"]:
                reasons.append("paralela a las vías, como San Pedro")
            why = ", ".join(reasons)
        scale = (f", acortada al {move.scale:.0%}" if move.scale != 1.0
                 else "")
        self.report["fit"].append(
            f"cascada {group['name']}: {pick['label']}, {where}{scale} — "
            f"{why}")
        trial = pick["trial"]
        for bank_id in group["banks"]:
            bank = trial._banks[bank_id]
            spec = trial.template.banks[bank_id]
            length = math.hypot(bank["end"][0] - bank["start"][0],
                                bank["end"][1] - bank["start"][1])
            self.report["fit"].append(
                f"  banco {bank_id}: hacia "
                f"{F.direction_label(bank['direction'])}, "
                f"{length:.1f} m"
                + (f" (la plantilla: {float(spec['length']) / move.scale:g}"
                   f" m)" if move.scale != 1.0 and "length" in spec else ""))
        for result in tried:
            if result is pick or result["move"].scale != move.scale:
                continue
            if result["fits"]:
                state = "también cabe, " + self._why_not(result, pick)
            elif not result["hub_ok"]:
                state = "el centro del pabellón queda fuera de él"
            else:
                state = (f"{len(result['outside'])} puntos fuera, hasta "
                         f"{result['worst']:.1f} m")
            self.report["fit"].append(f"  descartada {result['label']}: "
                                      f"{state}")

    @staticmethod
    def _why_not(result, pick) -> str:
        if result["door_clash"] and not pick["door_clash"]:
            return ("pero las escaleras entrarían por el muro donde OSM "
                    "tiene la puerta")
        if pick["parallel"] and not result["parallel"]:
            return "pero se prefiere paralela a las vías, como San Pedro"
        if result["approach"] > pick["approach"] + 1e-6:
            return (f"pero el pasillo desde el vestíbulo sería "
                    f"{result['approach'] - pick['approach']:.1f} m más "
                    f"largo")
        return "pero se prefiere un giro a un reflejo"

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
        if not self._area_rings:
            return nominal
        crossings = ring_crossings(self._area_rings, v)
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
        if not self._area_rings:
            return point
        dist, ring_index, index, t, snapped = closest_point_on_rings(
            self._area_rings, point)
        if dist > PLATFORM_SNAP_WARN_M:
            self.warnings.append(
                f"un vértice del andén {key} estaba a {dist:.1f} m del "
                f"anillo del área y se movió hasta él")
        if not any(math.hypot(p[0] - snapped[0], p[1] - snapped[1]) < 1e-3
                   for _, _, _, p in self._area_inserts):
            self._area_inserts.append((ring_index, index, t, snapped))
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
        """(anillo, lados, way adoptado o None) del edificio de acceso.

        Si el encaje ya identificó el pabellón de la cascada, ese manda:
        es el que decidió hacia dónde corren las escaleras.
        """
        found = self._fit_pavilions.get(key) or self._adoptable_building(
            point)
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
            spec = self.template.nodes.get(key, {}).get("building")
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
            doors = [self._door_point(sides, stair, i, spec)
                     for i in door_sides]
            facing = (self.context.nearest_point(*centre, FACING_SEARCH_M)
                      if self.context else None)
            if adopted is not None:
                self._link_osm_entrance(key, stop, ring)
            entrance = self._entrance_door(key, stop, sides, door_sides,
                                           facing)
            closed = self._closed_doors(key, spec, sides, door_sides)
            closed = self._keep_live_entrance_open(key, stop, entrance,
                                                   closed)
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
                "hub": centre,
                "stair_side": stair, "door_sides": door_sides,
                "doors": doors, "entrance": entrance, "inner": inner,
                "graph_door": graph_door, "adopted": adopted,
                "closed_doors": closed,
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

    def _link_declared_entrances(self) -> None:
        """Accesos que la plantilla enlaza a una entrada de OSM.

        `osm_node` en un nodo de acceso hace lo que haría el enlace de la
        base: el acceso es ese nodo de OSM y no un gemelo. Sin edificio de
        acceso, el acceso se queda donde OSM lo tiene y lo que llega del
        grafo termina ahí: es el caso de un acceso a cielo abierto.
        """
        if self.context is None:
            return
        for key, stop in sorted(self.graph.stops.items()):
            spec = self.template.nodes.get(key) or {}
            osm_id = spec.get("osm_node")
            if osm_id is None or stop.location_type_id != LOCATION_ENTRANCE:
                continue
            node = self.context.nodes.get(int(osm_id))
            if node is None:
                self.warnings.append(
                    f"la plantilla enlaza el acceso {key} al nodo OSM "
                    f"{osm_id}, que el contexto no trae; se dibuja donde "
                    f"la plantilla lo pone")
                continue
            self._auto_links[stop.key] = node
            where = ""
            if not spec.get("building"):
                point = self.context.local(node.osm_id)
                where = (f", y queda donde OSM lo tiene ({point[0]:.1f}, "
                         f"{point[1]:.1f})")
                if spec.get("relocate"):
                    # La versión aprobada movió la entrada de OSM (Polanco
                    # 05: hasta la punta de la pestaña del área); es un
                    # cambio a OSM y por eso sale en el reporte.
                    osm_point = point
                    point = (float(spec["u"]), float(spec["v"]))
                    moved = math.hypot(point[0] - osm_point[0],
                                       point[1] - osm_point[1])
                    where = (f", movida por la plantilla de ({osm_point[0]:.1f}"
                             f", {osm_point[1]:.1f}) a ({point[0]:.1f}, "
                             f"{point[1]:.1f}), {moved:.1f} m")
                self.template.overrides[key] = point
            self.report["osm"].append(
                f"el acceso {key} es la entrada {node.osm_id} de OSM "
                f"(«{node.tags.get('name', '')}»), por la plantilla{where}")

    def _place_missing_nodes(self) -> None:
        """Nodos del grafo que la plantilla no ubica: se ponen y se avisan.

        El archivo se escribe igual, para que la estación se pueda abrir y
        afinar: el nodo va al centro de sus vecinos ya ubicados (a 3 m del
        único, si solo tiene uno), y lleva `fixme`.
        """
        placed = set(self.template.nodes) | set(self.template.overrides)
        missing = [k for k in sorted(self.graph.stops) if k not in placed]
        for key in missing:
            stop = self.graph.stops[key]
            if stop.location_type_id == LOCATION_PLATFORM:
                raise TemplateError(
                    f"la plantilla {self.template.family} no ubica el andén "
                    f"{key}; un andén no se puede improvisar")
            near = []
            for pw in self.graph.pathways:
                ends = {pw.from_key, pw.to_key}
                if key not in ends:
                    continue
                other = (ends - {key}).pop() if len(ends) > 1 else key
                if other in placed and other not in missing:
                    try:
                        near.append(self.template.point(other))
                    except TemplateError:
                        continue
            if len(near) > 1:
                point = (sum(p[0] for p in near) / len(near),
                         sum(p[1] for p in near) / len(near))
            elif near:
                du, dv = near[0]
                length = math.hypot(du, dv) or 1.0
                point = (du + 3.0 * du / length, dv + 3.0 * dv / length)
            else:
                point = (0.0, 0.0)
            self.template.overrides[key] = point
            self._missing_nodes[key] = (
                f"Ubicación provisional: la plantilla "
                f"{self.template.family} no ubica el nodo {key} "
                f"(«{stop.name}»); el generador lo puso al centro de sus "
                f"vecinos. Revisar su posición.")
            self.warnings.append(
                f"la plantilla no ubica el nodo {key} («{stop.name}»); se "
                f"puso en ({point[0]:.1f}, {point[1]:.1f}) con fixme")

    def _door_point(self, sides, stair: int, index: int, spec: dict):
        """Puerta del muro `index`: al medio, o corrida hacia el fondo.

        En los pabellones de L7 las puertas de los dos muros largos no
        están al medio sino cerca del muro opuesto a las escaleras, que
        es donde estas desembocan; `side_door_inset` dice a cuántos
        metros de ese muro van.
        """
        side = sides[index]
        inset = spec.get("side_door_inset")
        far = (stair + len(sides) // 2) % len(sides)
        if inset is None or len(sides) != 4 or index == far:
            return side["mid"]
        a, b = side["a"], side["b"]
        fu, fv = sides[far]["mid"]
        # Se mide desde la punta del muro que toca el muro del fondo.
        if math.hypot(b[0] - fu, b[1] - fv) < math.hypot(a[0] - fu,
                                                         a[1] - fv):
            a, b = b, a
        corner = a
        du, dv = unit(a, b)
        inset = min(float(inset), side["length"])
        return (corner[0] + du * inset, corner[1] + dv * inset)

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

    def _link_osm_entrance(self, key: str, stop, ring) -> None:
        """Entrada de OSM del pabellón adoptado, aunque la base no la enlace.

        En San Joaquín cada pabellón trae su `railway=subway_entrance`
        junto al muro que da a la explanada, y la base no tiene enlace a
        ninguno; sin esto el archivo dibujaba una puerta propia a metro y
        medio de la que OSM ya tiene. Si hay varias, la más cercana al
        centro del pabellón.
        """
        if self.context is None or stop.osm_id:
            return
        centre = polygon_centroid(ring)
        best = None
        for node in self.context.subway_entrances():
            p = self.context.local(node.osm_id)
            if not (point_in_polygon(ring, p) or distance_to_ring(
                    ring, p) <= ENTRANCE_ADOPT_M):
                continue
            d = math.hypot(p[0] - centre[0], p[1] - centre[1])
            if best is None or d < best[0]:
                best = (d, node)
        if best is not None:
            self._auto_links[stop.key] = best[1]
            self.report["osm"].append(
                f"el acceso {key} adopta la entrada {best[1].osm_id} de "
                f"OSM, que está en su pabellón y la base no enlaza")

    def _keep_live_entrance_open(self, key, stop, entrance: int,
                                 closed: list[int]) -> list[int]:
        """Una puerta que OSM tiene como entrada en uso no se clausura.

        `closed_doors` es relevamiento de la estación de referencia; si en
        la hermana cae justo donde OSM tiene una entrada abierta, gana lo
        que está en el mapa y se avisa para revisarlo en campo.
        """
        node = self._foreign_link(stop)
        if (node is None or entrance not in closed
                or node.tags.get("railway") != "subway_entrance"):
            return closed
        self.warnings.append(
            f"la plantilla clausura la puerta del edificio de {key} donde "
            f"OSM tiene la entrada en uso {node.osm_id}; se deja abierta "
            f"y hay que confirmar en campo cuál puerta está cerrada")
        return [i for i in closed if i != entrance]

    def _foreign_link(self, stop):
        """Nodo de OSM enlazado en la base, si el contexto lo trajo."""
        if self.context is not None and stop.key in self._auto_links:
            return self._auto_links[stop.key]
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
            if key in self._missing_nodes:
                tags["fixme"] = self._missing_nodes[key]
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
            centre_id = self.doc.node_at(*plan["hub"])
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
                self._attach_osm_plazas(key, plan, door_ids)
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
            # Donde OSM ya tiene la explanada no se dibuja otra encima.
            if plan["plaza_half"] and not plan.get("osm_plazas"):
                plaza = self.doc.add_way(
                    square_corners(plan["centre"][0], plan["centre"][1],
                                   plan["plaza_half"]),
                    T.plaza_tags(), [], kind="plaza",
                    label=f"explanada {key}", closed=True)
                self.doc.outdoor.update(plaza.nodes)
                plan["plaza_way"] = plaza

    def _station_buildings(self):
        """Edificios de OSM que la estación usa: los pabellones adoptados
        y cualquiera que contenga o roce (2 m) uno de sus accesos."""
        found = {plan["adopted"].osm_id: plan["adopted"]
                 for plan in self._buildings.values() if plan["adopted"]}
        if self.context is None:
            return list(found.values())
        entrances = [(self.doc.nodes[nid].u, self.doc.nodes[nid].v)
                     for nid in self._entrance_nodes.values()]
        for way in sorted(self.context.ways.values(),
                          key=lambda w: w.osm_id):
            if way.osm_id in found or not self.context.is_building(way):
                continue
            if self.context.is_outline(way):
                continue
            ring = self.context.local_line(way)
            if len(ring) < 3:
                continue
            if any(point_in_polygon(ring, p) or distance_to_ring(ring, p)
                   <= ENTRANCE_ADOPT_M for p in entrances):
                found[way.osm_id] = way
        return [found[k] for k in sorted(found)]

    def _fit_buildings_in_area(self) -> None:
        """El edificio de OSM que usa la estación cabe entero en el área.

        Ricardo, 22 de octubre de 2026: el pabellón entero va dentro del
        área. Si sobresale poco (`BUILDING_FIT_MAX_M`), sus vértices de
        fuera se llevan al punto más cercano del borde, que es lo mínimo
        que lo mete; si sobresale más, el edificio no se toca y se avisa,
        porque ya no es un ajuste de dibujo sino una discrepancia entre
        OSM y el KML que alguien tiene que mirar. Cada nodo movido se
        reporta: es un elemento de OSM que Ricardo revisa uno por uno.
        """
        if not self._area_rings or self.station_area != "kml":
            return
        outer = self._area_rings[0]
        for way in self._station_buildings():
            ids = list(dict.fromkeys(way.node_ids))
            moves = []
            for nid in ids:
                node = self.context.nodes.get(nid) if self.context else None
                if node is None:
                    continue
                p = (self.doc.nodes[nid].u, self.doc.nodes[nid].v) if (
                    nid in self.doc.nodes) else self.context.local(nid)
                if point_in_polygon(outer, p):
                    continue
                dist, _, _, _, target = closest_point_on_rings([outer], p)
                moves.append((nid, node, p, target, dist))
            # Los muros también: el área puede meterse en el edificio por
            # una muesca sin que ningún vértice quede fuera (San Antonio).
            ring = [(self.doc.nodes[n].u, self.doc.nodes[n].v)
                    if n in self.doc.nodes else self.context.local(n)
                    for n in way.node_ids if n in self.context.nodes]
            wall = max((d for d, _ in F.outside_points(
                outer, [q for a, b in zip(ring, ring[1:])
                        for q in F.sample_segment(a, b, 0.25)], 0.0)),
                default=0.0)
            if not moves and wall <= 0.01:
                continue
            worst = max([m[4] for m in moves] + [wall])
            if worst > BUILDING_FIT_MAX_M or not moves:
                self.warnings.append(
                    f"el edificio de OSM {way.osm_id} que usa la estación "
                    f"sobresale del área hasta {worst:.2f} m ({len(moves)} "
                    f"vértices fuera"
                    + ("; el área se mete en él por sus muros"
                       if wall > 0.01 else "")
                    + f"); pasa de {BUILDING_FIT_MAX_M:g} m o no se arregla "
                    f"moviendo vértices, así que no se movió: hay que "
                    f"decidir si se corrige el área o el edificio")
                continue
            if way.osm_id not in self._embedded_ways:
                self._embed(way)
            for nid, node, p, target, dist in moves:
                self.doc.adopt_node(node, target[0], target[1], {})
                self.report["osm"].append(
                    f"nodo {nid} del edificio {way.osm_id} movido {dist:.2f} "
                    f"m, de ({p[0]:.2f}, {p[1]:.2f}) a ({target[0]:.2f}, "
                    f"{target[1]:.2f}), para que el edificio quepa en el "
                    f"área")

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

    def _attach_osm_plazas(self, key: str, plan: dict, door_ids) -> None:
        """Las puertas que dan a una explanada de OSM quedan en su borde.

        En San Joaquín la explanada es un multipolígono que comparte muros
        con el pabellón; una puerta sobre ese muro se mete como vértice
        del anillo de la explanada, y así el acceso queda conectado a
        ella sin un connector que corra pegado a la pared. La explanada
        se embebe con su relación y todos sus anillos; solo cambian los
        anillos que reciben una puerta.
        """
        if self.context is None:
            return
        attached = []
        for rel, ring_way in self.context.plaza_rings():
            line = self.context.local_line(ring_way)
            hits = []
            for nid in door_ids:
                node = self.doc.nodes[nid]
                for a, b in zip(line, line[1:]):
                    d, t = point_segment_distance((node.u, node.v), a, b)
                    if d <= PLAZA_DOOR_M and 0.0 < t < 1.0:
                        hits.append(nid)
                        break
            if not hits:
                continue
            way = self._embed_plaza(rel, ring_way)
            self.doc.adopt_way(way)
            for nid in hits:
                self.doc.insert_node_id(way, nid)
            owner = rel.osm_id if rel is not None else ring_way.osm_id
            attached.append(owner)
            self.report["osm"].append(
                f"edificio {key}: {len(hits)} puerta(s) sobre el anillo "
                f"{ring_way.osm_id} de la explanada "
                + (f"(relación {rel.osm_id})" if rel is not None
                   else "(way)")
                + "; el anillo sale con action=modify")
        plan["osm_plazas"] = sorted(set(attached))
        for item in self.report["buildings"]:
            if item["key"] == key:
                item["osm_plazas"] = plan["osm_plazas"]

    def _embed_plaza(self, rel, ring_way):
        """Embebe una explanada entera: relación y anillos, congelados."""
        if rel is None:
            return self._embed(ring_way)
        self.doc.add_foreign_relation(rel)
        for kind, ref, _ in rel.members:
            if kind == "way" and ref in self.context.ways:
                self._embed(self.context.ways[ref])
        return self._embedded_ways[ring_way.osm_id]

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
            spec = self.template.nodes.get(key) or {}
            if "connector" in spec:
                self._declared_connector(key, start_id, spec["connector"])
                continue
            plan = self._buildings.get(key, {})
            plaza = plan.get("plaza_way")
            done = set()
            joined = set(plan.get("osm_plazas", []))
            targets = [
                t for t in self.context.nearest_vertices(
                    start.u, start.v, CONNECTOR_MAX_M)
                if self.context.plaza_relation(t[0]) not in joined
                and t[0].osm_id not in joined]
            if not targets and not joined:
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

    def _declared_connector(self, key: str, start_id: int, spec) -> None:
        """El connector que la versión aprobada dibujó a mano.

        Reemplaza los rectos al vértice más cercano de cada peatonal: en
        Polanco Pablo los llevó en L por la banqueta hasta un vértice
        concreto. `false` deja el acceso sin connector, a propósito.
        """
        if not spec:
            self.report["connectors"].append({
                "key": key, "way": None, "highway": None, "footway": None,
                "length": 0.0, "vertex": None, "shared": False,
                "through_plaza": False, "declared": "sin connector"})
            return
        target = self.context.nodes.get(int(spec["osm_node"]))
        if target is None:
            self.warnings.append(
                f"la plantilla lleva el connector de {key} al nodo OSM "
                f"{spec['osm_node']}, que el contexto no trae; queda sin "
                f"connector")
            return
        end_id = self.doc.add_foreign_node(target)
        ids = [start_id] + [self.doc.node_at(float(u), float(v))
                            for u, v in spec.get("points", [])] + [end_id]
        way = self.doc.add_way_from_ids(
            ids, T.connector_tags(), [0.0], kind="connector",
            label=f"{key}->{target.osm_id}")
        nodes = [self.doc.nodes[n] for n in way.nodes]
        length = sum(math.hypot(b.u - a.u, b.v - a.v)
                     for a, b in zip(nodes, nodes[1:]))
        self.report["connectors"].append({
            "key": key, "way": None, "highway": "footway", "footway": None,
            "length": length, "vertex": target.osm_id, "shared": False,
            "through_plaza": False, "declared": "de la plantilla"})

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
        # Solo esquinas de edificio: el área subterránea no se cose a
        # explanadas, jardines ni barreras, que siguen otra lógica.
        allowed = (self.context.building_node_ids() if self.context
                   else None)
        for u, v in ring:
            nid = None
            for node in self.doc.nodes.values():
                # Un nodo de OSM que adoptamos y colocamos (la puerta de un
                # lóbulo) es tan nuestro como uno nuevo.
                if (node.foreign and node.frozen) or node.action == "delete":
                    continue
                if math.hypot(node.u - u, node.v - v) <= SNAP_TOLERANCE_M:
                    nid = node.id
                    break
            if nid is None:
                nid = self.doc.reuse_foreign_node(u, v, self.context,
                                                  allowed=allowed)
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
        """Área de estación: un way cerrado, o multipolígono si hay islas.

        Sin islas el área es un solo way con sus etiquetas, como lo pide
        OSM para un polígono simple —Ricardo, 22 de octubre de 2026—. Con
        islas va un anillo outer y uno inner por isla, las etiquetas en
        la relación y los anillos sin etiquetas.
        """
        if not self._area_rings:
            return
        rings = []
        for r, ring in enumerate(self._area_rings):
            inserts = [(i, t, p) for k, i, t, p in self._area_inserts
                       if k == r]
            rings.append(insert_points_into_ring(ring, inserts))
        flat = self._area_node_ids([p for ring in rings for p in ring])
        ids = []
        for ring in rings:
            ids.append(flat[:len(ring)])
            flat = flat[len(ring):]
        tags = T.station_area_tags(self.graph.station_name,
                                   self._underground())
        islands = len(rings) > 1
        if not outlines:
            outer = self.doc.add_way_from_ids(
                ids[0], {} if islands else tags, [], kind="station_area",
                label="área de estación (KML)"
                + (": outer" if islands else ""), closed=True)
        else:
            outer, tags = self._reshape_outline(outlines, rings[0], ids[0],
                                                tags, islands)
        if not islands:
            return
        members = [("way", outer.id, "outer")]
        for k, ring_ids in enumerate(ids[1:], start=1):
            inner = self.doc.add_way_from_ids(
                ring_ids, {}, [], kind="station_area",
                label=f"área de estación (KML): isla {k}", closed=True)
            members.append(("way", inner.id, "inner"))
        rel = self.doc.add_relation(
            members, {"type": "multipolygon", **tags}, kind="station_area",
            label="área de estación")
        self.report["area"].append(
            f"multipolígono {rel.id}: outer {outer.id} con "
            f"{len(outer.nodes) - 1} vértices y {len(members) - 1} inner")

    def _reshape_outline(self, outlines, ring, ids, tags, islands):
        """El contorno de OSM se queda con su id y toma la forma del KML.

        El trazo del KML es mejor que el contorno de OSM, así que el way
        conserva id e historia y cambia de forma; en sus etiquetas OSM
        gana cada conflicto. Con islas el way pasa a ser el outer: sus
        etiquetas se mudan a la relación y queda como anillo sin ellas.
        """
        best = max(outlines, key=lambda w: overlap_ratio(
            ring, self.context.local_line(w)))
        way = self._embed(best)
        label = "área de estación (KML sobre el contorno de OSM)"
        conflicts, deleted, kept = self.doc.adopt_way(
            way, tags, ids, kind="station_area",
            label=label + (": outer" if islands else ""))
        merged = way.tags
        if islands:
            way.tags = {}
        moved = "; sus etiquetas pasan a la relación" if islands else ""
        self.report["area"].append(
            f"contorno de OSM {way.id} reformado con el polígono del KML: "
            f"{len(ids)} vértices, {len(deleted)} nodos suyos dados de "
            f"baja, {len(kept)} conservados por tener etiquetas{moved}")
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
        return way, merged

    def _build_context_extras(self) -> None:
        """Banquetas, explanadas, calles, vías, transporte público,
        edificios y bardas.

        No se conectan a nada y no se tocan: están para que quien abra el
        archivo en JOSM vea la estación dentro de su manzana y no
        flotando. Entra lo que roza la extensión de la estación más
        `context_radius` (`CONTEXT_EMBED_M` por omisión). Los contornos
        de estación no pasan por aquí: `_build_station_area` ya los
        embebió y `scene_elements` los excluye, así que ninguno entra dos
        veces como edificio genérico.
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
                         self.context_radius):
                self._embed(way)
        for rel, ring_way in self.context.plaza_rings():
            if rel is None or rel.osm_id in self.doc.relations:
                continue
            if _near_any(self.context.local_line(ring_way), own,
                         self.context_radius):
                self._embed_plaza(rel, ring_way)
        for node in nodes:
            if node.osm_id in self.doc.nodes:
                continue
            if _near_any([self.context.local(node.osm_id)], own,
                         self.context_radius):
                self.doc.add_foreign_node(node)

    def _place_station_node(self) -> None:
        """Lleva el nodo de estación de OSM al cruce de la estación.

        Es la excepción a no mover lo ajeno. En San Pedro el nodo estaba
        31 m al oriente, y Ricardo lo movió a mano sobre el eje, en el
        paso bajo las vías: «es más preciso el mío y consistente con todo
        lo demás que se subirá». La plantilla dice en qué u está el cruce
        (`station_node`); la v es el eje de la franja de andenes. Como el
        nodo suele ser vértice de la línea `railway=subway`, la línea se
        dobla con él.
        """
        spec = self.template.station_node
        if not spec or self.context is None:
            return
        wanted = fold_name(self.graph.station_name)
        found = [n for n in self.context.station_nodes()
                 if fold_name(n.tags.get("name", "")) == wanted]
        if not found:
            self.warnings.append(
                f"OSM no tiene nodo de estación llamado «"
                f"{self.graph.station_name}» en el contexto; no se "
                f"recolocó ninguno")
            return
        node = min(found, key=lambda n: math.hypot(
            *self.context.local(n.osm_id)))
        u = float(spec["u"])
        if "v" in spec:
            v = float(spec["v"])
        elif self._band is not None:
            v = sum(self._band) / 2
        else:
            v = 0.0
        u, shift = self._clear_station_point(u, v)
        before = self.context.local(node.osm_id)
        self.doc.adopt_node(node, u, v, {})
        moved = math.hypot(u - before[0], v - before[1])
        self.report["station"].append(
            f"nodo de estación {node.osm_id}: de ({before[0]:.1f}, "
            f"{before[1]:.1f}) a ({u:.1f}, {v:.1f}), {moved:.1f} m"
            + (f"; corrido {shift:+.1f} m en u para no encimarse en un "
               f"nodo del trazo" if shift else ""))

    def _clear_station_point(self, u: float, v: float):
        """(u despejada, corrimiento): sin encimarse en un nodo nuestro."""
        own = [(n.u, n.v) for n in self.doc.nodes.values()
               if not n.foreign]
        for step in range(0, 21):
            for shift in ((step * 0.5,) if step == 0 else
                          (step * 0.5, -step * 0.5)):
                if all(math.hypot(u + shift - a, v - b)
                       >= STATION_NODE_CLEAR_M for a, b in own):
                    return u + shift, shift
        return u, 0.0

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
            raw = spec["levels"] if "levels" in spec else [spec["level"]]
            levels = [float(x) for x in raw]
            tags = T.footway_tags(levels)
            if spec.get("name"):
                tags["name"] = spec["name"]
            tags.update(spec.get("tags", {}))
            way = self.doc.add_way(points, tags, levels, kind="extra",
                                   label=spec.get("name", "extra"))
            # La segunda boca de un acceso doble (Polanco oriente) no es
            # un nodo del grafo; el extra_way que llega a ella la etiqueta.
            if spec.get("end_tags"):
                self.doc.nodes[way.nodes[-1]].tags.update(spec["end_tags"])
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
        circulación. Con `axis` o con `junction` + `direction` + `length`
        las escaleras dejan de ser colineales con los nodos del grafo y
        son los nodos los que se mueven a los extremos del banco. Los
        bancos apilados se planean después del banco sobre el que van,
        porque toman de él el eje.
        """
        pending = sorted(self.template.banks.items())
        while pending:
            ready = [(k, s) for k, s in pending
                     if s.get("stacked_on") in (None, *self._banks)]
            if not ready:
                raise TemplateError(
                    f"los bancos {', '.join(k for k, _ in pending)} se "
                    f"apilan sobre bancos que no existen o en círculo")
            for bank_id, spec in ready:
                self._plan_bank(bank_id, spec)
            pending = [(k, s) for k, s in pending if k not in self._banks]
        self._sync_building_hubs()

    def _bank_leads(self, spec: dict) -> tuple[float, float]:
        raw = spec.get("lead", DEFAULT_BANK_LEAD_M)
        if isinstance(raw, (list, tuple)):
            return float(raw[0]), float(raw[1])
        return float(raw), float(raw)

    def _plan_bank(self, bank_id: str, spec: dict) -> None:
        from_key, to_key = spec["from"], spec["to"]
        lead_from, lead_to = self._bank_leads(spec)
        spacing = float(spec.get("spacing", DEFAULT_BANK_SPACING_M))
        lower = self._banks.get(spec.get("stacked_on"))
        stack_offset = None
        explicit = bool(spec.get("axis") or spec.get("junction"))
        if spec.get("axis"):
            axis = spec["axis"]
            start = (float(axis[0][0]), float(axis[0][1]))
            end = (float(axis[1][0]), float(axis[1][1]))
            direction = unit(start, end)
        elif spec.get("junction"):
            if "direction" in spec:
                direction = _direction(spec["direction"])
            elif lower is not None:
                direction = lower["direction"]
            else:
                raise TemplateError(
                    f"el banco «{bank_id}» declara junction sin direction "
                    f"ni stacked_on")
            junction = (float(spec["junction"][0]),
                        float(spec["junction"][1]))
            if lower is not None:
                stack_offset = float(spec.get("stack_offset",
                                              DEFAULT_STACK_OFFSET_M))
                junction = self._stacked_junction(
                    lower, junction, direction, stack_offset, spec)
            start = (junction[0] + direction[0] * lead_from,
                     junction[1] + direction[1] * lead_from)
            length = float(spec["length"])
            end = (start[0] + direction[0] * length,
                   start[1] + direction[1] * length)
        else:
            start = end = None
        if explicit:
            junction_from = (start[0] - direction[0] * lead_from,
                             start[1] - direction[1] * lead_from)
            junction_to = (end[0] + direction[0] * lead_to,
                           end[1] + direction[1] * lead_to)
            # `place` dice cuál de los dos nodos del grafo se muda al
            # banco. Sin él, dos bancos encadenados se pisarían el nodo
            # que comparten y el edificio perdería su centro.
            place = spec.get("place", ["from", "to"])
            for which, key, point in (("from", from_key, junction_from),
                                      ("to", to_key, junction_to)):
                if which not in place:
                    continue
                if (key in self.template.overrides
                        and key not in self._building_inner_keys()):
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
            if run - lead_from - lead_to < MIN_BANK_STAIR_M:
                clamped = max(0.0, (run - MIN_BANK_STAIR_M) / 2)
                self.warnings.append(
                    f"el banco «{bank_id}» pide {lead_from:g} y "
                    f"{lead_to:g} m de aproche sobre un tramo de "
                    f"{run:.1f} m; se recortaron a {clamped:.1f} m para "
                    f"que las escaleras midan algo")
                lead_from = lead_to = clamped
            start = (junction_from[0] + direction[0] * lead_from,
                     junction_from[1] + direction[1] * lead_from)
            end = (junction_to[0] - direction[0] * lead_to,
                   junction_to[1] - direction[1] * lead_to)
        uphill = self._uphill(from_key, to_key, direction)
        right = right_of(uphill)
        # La regla de sentidos es del mundo, no de la plantilla: en la
        # hermana espejo la derecha de quien sube es la izquierda del
        # marco local.
        slot_right = ((-right[0], -right[1]) if self.doc.frame.mirror
                      else right)
        self._banks[bank_id] = {
            "from": from_key, "to": to_key, "start": start, "end": end,
            "junction_from": junction_from, "junction_to": junction_to,
            "spacing": spacing, "direction": direction, "right": right,
            "slot_right": slot_right,
        }
        self.template.bank_junctions[bank_id] = {
            "from": junction_from, "to": junction_to}
        self.report["banks"].append({
            "id": bank_id, "from": from_key, "to": to_key,
            "spacing": spacing, "lead": (lead_from, lead_to),
            "length": math.hypot(end[0] - start[0], end[1] - start[1]),
            "explicit_axis": explicit, "stacked_on": spec.get("stacked_on"),
            "stack_offset": stack_offset, "clearance": None,
        })

    def _stacked_junction(self, lower: dict, junction, direction,
                          offset: float, spec: dict):
        """Nodo de encuentro de un banco apilado, sobre el eje del de abajo.

        Del `junction` declarado solo vale cuánto avanza a lo largo del
        eje: la posición lateral la dan el eje del banco de abajo y
        `stack_offset`, para que las dos capas no se encimen en planta.
        """
        du, dv = lower["direction"]
        along = ((junction[0] - lower["start"][0]) * du
                 + (junction[1] - lower["start"][1]) * dv)
        uphill = self._uphill(spec["from"], spec["to"], direction)
        ru, rv = right_of(uphill)
        return (lower["start"][0] + du * along + ru * offset,
                lower["start"][1] + dv * along + rv * offset)

    def _uphill(self, from_key: str, to_key: str, direction):
        """Dirección del eje mirando desde el nivel bajo hacia el alto."""
        stops = self.graph.stops
        if from_key not in stops or to_key not in stops:
            return direction
        lf = stops[from_key].level_index
        lt = stops[to_key].level_index
        if lf is not None and lt is not None and lt < lf:
            return (-direction[0], -direction[1])
        return direction

    def _building_inner_keys(self) -> set:
        return {plan["inner"] for plan in self._buildings.values()
                if plan["inner"]}

    def _sync_building_hubs(self) -> None:
        """El centro del pabellón va donde desembocan sus escaleras.

        Si un banco recolocó el nodo interior, ese punto es el nodo del
        que salen las puertas; el centroide se queda solo para la
        explanada.
        """
        for key, plan in self._buildings.items():
            inner = plan["inner"]
            if not inner or inner not in self.template.overrides:
                continue
            hub = self.template.overrides[inner]
            plan["hub"] = hub
            if not plan["graph_door"]:
                self.template.overrides[key] = hub

    def _assign_bank_slots(self, items) -> dict:
        """Posición lateral de cada escalera de banco, por la regla de L7.

        Ricardo: «avanzas por la derecha, los que vienen en el otro
        sentido los ves a tu izquierda, no importa si subes o bajas»; y
        la fija siempre en medio. Mirando el banco desde el nivel bajo:
        las que bajan a la izquierda, las fijas al centro y las que suben
        a la derecha. Un `slot` escrito en la plantilla manda sobre la
        regla, pero solo si todo el banco lo trae y sin repetirse.
        """
        groups: dict[str, list] = {}
        for pw, spec, layout in items:
            groups.setdefault(layout[0], []).append((pw, spec, layout))
        slots = {}
        for bank_id, members in groups.items():
            manual = [layout[1] for _, _, layout in members]
            if all(m is not None for m in manual):
                if len(set(manual)) == len(manual):
                    for (_, spec, _), slot in zip(members, manual):
                        slots[id(spec)] = (slot, len(members))
                    continue
                self.warnings.append(
                    f"el banco «{bank_id}» tenía posiciones laterales "
                    f"repetidas; se repartieron por la regla de sentidos")
            elif any(m is not None for m in manual):
                self.warnings.append(
                    f"el banco «{bank_id}» fija `slot` solo en algunas "
                    f"escaleras; se ignoraron y manda la regla de sentidos")
            ranked = sorted(members, key=lambda m: (
                self._bank_rank(m[0]), m[0].mode_id, m[0].index))
            for slot, (_, spec, _) in enumerate(ranked):
                slots[id(spec)] = (slot, len(members))
        return slots

    def _bank_rank(self, pw) -> int:
        """0 baja, 1 fija, 2 sube: el orden de izquierda a derecha."""
        if pw.mode_id != T.MODE_ESCALATOR:
            return 1
        if pw.is_bidirectional:
            # La reversible de L7 baja de ordinario; una familia donde
            # suba lo declara en la plantilla.
            return 2 if self.template.reversible_runs == "up" else 0
        lf = self.graph.stops[pw.from_key].level_index or 0.0
        lt = self.graph.stops[pw.to_key].level_index or 0.0
        return 2 if lt > lf else 0

    def _check_stack_clearance(self) -> None:
        """Distancia en planta entre un banco apilado y el de abajo.

        `node_at` pega nodos sin mirar el nivel y la soldadura cose los
        nodos de encuentro del nivel compartido, así que una escalera o
        un nodo de encuentro de arriba encima de una línea de abajo
        acaba unido a ella.
        """
        for item in self.report["banks"]:
            lower_id = item["stacked_on"]
            if lower_id is None:
                continue
            upper, lower = self._banks[item["id"]], self._banks[lower_id]
            lower_lines = self._bank_line_offsets(lower_id, lower["right"])
            ru, rv = lower["right"]
            origin = lower["start"]

            def lateral(p):
                return (p[0] - origin[0]) * ru + (p[1] - origin[1]) * rv

            upper_pts = [upper["junction_from"], upper["junction_to"]]
            upper_lines = [lateral(p) for p in upper_pts]
            upper_lines += [
                lateral(upper["start"]) + off
                for off in self._bank_line_offsets(item["id"],
                                                   lower["right"])]
            if not lower_lines:
                continue
            clearance = min(abs(a - b) for a in upper_lines
                            for b in lower_lines)
            item["clearance"] = clearance
            # El margen absorbe el redondeo de un banco girado: 0.5 m
            # justos tienen que valer igual en la hermana.
            if clearance < MIN_STACK_CLEARANCE_M - 1e-6:
                self.warnings.append(
                    f"el banco «{item['id']}» va apilado sobre "
                    f"«{lower_id}» y una de sus escaleras o nodos de "
                    f"encuentro queda a {clearance:.2f} m en planta de una "
                    f"escalera de abajo; cambia su stack_offset o su "
                    f"spacing")

    def _bank_line_offsets(self, bank_id: str, right) -> list[float]:
        """Desplazamiento lateral de cada escalera, medido sobre `right`."""
        bank = self._banks[bank_id]
        count = bank.get("count", 0)
        su, sv = bank["slot_right"]
        dot = su * right[0] + sv * right[1]
        return [dot * bank["spacing"] * (slot - (count - 1) / 2)
                for slot in range(count)]

    def _bank_segment(self, spec: dict, layout) -> tuple[dict, tuple, tuple]:
        """(banco, punta del lado `from`, punta del lado `to`) del tramo."""
        bank = self._banks[layout[0]]
        slot, count = self._slots[id(spec)]
        offset = bank["spacing"] * (slot - (count - 1) / 2)
        ru, rv = bank["slot_right"]
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
            # Con aproche 0 la escalera llega al nodo mismo: en San
            # Antonio desemboca en la entrada de OSM, sin tramo corto.
            if math.hypot(junction[0] - tip[0],
                          junction[1] - tip[1]) <= SNAP_TOLERANCE_M:
                continue
            join = self.doc.add_way(
                [junction, tip], T.footway_tags([level]), [level],
                kind="footway",
                label=f"{spec['from']}->{spec['to']} {end}")
            if len(join.nodes) == 2:
                self.doc.bank_tips.add(join.nodes[-1])

    def _build_pathways(self) -> set:
        used = set()
        resolved = []
        for pw in self.graph.pathways:
            key, spec = self.template.edge(
                pw.from_key, pw.to_key, pw.mode_id, pw.index,
                bidirectional=pw.is_bidirectional)
            if spec is None:
                resolved.append((pw, self._untemplated_edge(pw)))
                continue
            used.add(key)
            resolved.append((pw, spec))
        in_banks = [(pw, spec, self.template.bank_layout(spec))
                    for pw, spec in resolved
                    if self.template.bank_layout(spec) is not None]
        self._slots = self._assign_bank_slots(in_banks)
        for _, spec, layout in in_banks:
            self._banks[layout[0]]["count"] = layout[2]
        self._check_stack_clearance()
        for pw, spec in resolved:
            self._build_pathway(pw, spec)
        for key, text in sorted(self._missing_nodes.items()):
            nid = self.doc.node_at(*self.template.point(key))
            self.doc.nodes[nid].tags["fixme"] = text
        return used

    def _untemplated_edge(self, pw) -> dict:
        """Arista recta para un pathway que la plantilla no dibuja.

        El comando no aborta: la estación se escribe con ese tramo en línea
        recta entre sus extremos, marcado con `fixme` y en la lista de
        avisos, para afinarlo en JOSM o enseñárselo a la plantilla.
        """
        label = (f"{pw.from_key}->{pw.to_key}, modo {pw.mode_id}, índice "
                 f"{pw.index}")
        fixme = (f"Trazo provisional: la plantilla {self.template.family} "
                 f"no dibuja este pathway ({label}); el generador lo unió "
                 f"en línea recta entre sus extremos. Revisar la geometría.")
        self.warnings.append(
            f"la plantilla no dibuja el pathway {pw.pathway_id} ({label}); "
            f"va recto entre sus extremos con fixme")
        self.report["untemplated"].append(
            {"pathway_id": pw.pathway_id, "label": label})
        ends = [pw.from_key, pw.to_key]
        geometry = []
        for key, other in zip(ends, reversed(ends)):
            if self.graph.stops[key].location_type_id != LOCATION_PLATFORM:
                geometry.append(key)
                continue
            # Un andén no es un punto: el tramo arranca de su senda, a la
            # altura del otro extremo.
            try:
                u = self.template.point(other)[0]
            except (TemplateError, KeyError):
                u = 0.0
            geometry.append({"spine": key, "u": u})
        return {"from": pw.from_key, "to": pw.to_key, "mode": pw.mode_id,
                "index": pw.index, "geometry": geometry,
                "tags": {"fixme": fixme}}

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


BANK_DIRECTIONS = {"+u": (1.0, 0.0), "-u": (-1.0, 0.0),
                   "+v": (0.0, 1.0), "-v": (0.0, -1.0)}


def _direction(raw) -> tuple[float, float]:
    """`+u`/`-u`/`+v`/`-v`, o grados medidos de +u hacia +v."""
    if isinstance(raw, str):
        try:
            return BANK_DIRECTIONS[raw]
        except KeyError:
            raise TemplateError(
                f"dirección de banco desconocida: {raw!r}; usa +u, -u, "
                f"+v, -v o grados")
    angle = math.radians(float(raw))
    return (math.cos(angle), math.sin(angle))


def _kind(mode_id: int) -> str:
    if mode_id == T.MODE_STAIRS:
        return "steps"
    if mode_id == T.MODE_ESCALATOR:
        return "escalator"
    if mode_id == T.MODE_ELEVATOR:
        return "elevator"
    return "footway"
