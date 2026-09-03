"""Contexto de OSM alrededor de una estación: consulta, caché y lectura.

El archivo generado tiene que engancharse con lo que ya existe en OSM en
vez de ser una isla, y además tiene que leerse: entran los nodos de
acceso ya enlazados en la base, el contorno de la estación cuando OSM lo
tiene, y congelado —id real, sin tocar— todo lo que rodea a la estación
a menos de `CONTEXT_EMBED_M`: banquetas, calles, vías urbanas,
transporte público, edificios y barreras. Solo las peatonales reciben
tramos de conexión desde los accesos.

La caché en `data/osm/context/<slug>.json` está versionada a propósito:
es lo que hace reproducible la exportación sin red y sin depender de que
Overpass conteste igual mañana.
"""
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .geometry import point_segment_distance

ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
USER_AGENT = ("pendientes-y-escaleras/1.0 (Bandatos; relevamiento de "
              "escaleras del Metro CDMX; https://bandatos.org)")
RETRY_STATUS = (429, 502, 503, 504)
RETRY_PAUSES = (5, 20, 60)

# La consulta tiene que cubrir el radio de embebido medido desde el
# nodo más lejano de la estación, no desde el ancla: nuestros nodos
# llegan a ~80 m del ancla, así que 80 + 120 = 200 es el mínimo real y
# 250 deja margen para plantillas más extendidas.
DEFAULT_RADIUS_M = 250

# Ways a las que un acceso se puede conectar directamente.
FOOTWAY_HIGHWAYS = ("footway", "path", "pedestrian", "steps")
# Calles: nunca son destino de un connector, pero sí tienen que verse en
# JOSM para ubicar la estación en su manzana.
ROAD_HIGHWAYS = ("motorway", "trunk", "primary", "secondary", "tertiary",
                 "unclassified", "residential", "living_street", "service",
                 "motorway_link", "trunk_link", "primary_link",
                 "secondary_link", "tertiary_link")
# Vías férreas de transporte urbano que pasan por el entorno.
TRACK_RAILWAYS = ("subway", "light_rail", "tram")
# Contornos de estación que vale la pena traer para no duplicarlos.
OUTLINE_BUILDINGS = ("train_station", "transportation")
# Distancia a la que un objeto del entorno se considera parte de la
# escena de la estación y entra al archivo.
CONTEXT_EMBED_M = 120.0


class OverpassError(Exception):
    pass


def build_query(osm_ids: list[int], lat: float, lon: float,
                radius: int = DEFAULT_RADIUS_M) -> str:
    """Consulta acotada: enlaces de la base y el entorno de la manzana.

    Peatonales, calles, vías urbanas, transporte público, edificios y
    barreras. Lo que entra al archivo se decide después, por distancia
    a nuestros nodos (`CONTEXT_EMBED_M`); aquí se descarga de más.
    """
    around = f"around:{radius},{lat:.7f},{lon:.7f}"
    foot = "|".join(FOOTWAY_HIGHWAYS)
    buildings = "|".join(OUTLINE_BUILDINGS)
    roads = "|".join(ROAD_HIGHWAYS)
    tracks = "|".join(TRACK_RAILWAYS)
    parts = [f'way({around})["highway"~"^({foot})$"];',
             f'way({around})["highway"~"^({roads})$"];',
             f'way({around})["railway"~"^({tracks})$"];',
             f'way({around})["building"~"^({buildings})$"];',
             # Todos los edificios, no solo los contornos de estación:
             # delimitan la manzana, la explanada y el camino a la
             # banqueta, y algunos accesos ya están mapeados como
             # edificio. Solo ways: `document.py` no escribe relaciones,
             # así que los multipolígonos quedan fuera.
             f'way({around})["building"];',
             # Bardas, muros y rejas: son lo que impide que un camino
             # dibujado sobre el papel exista en la calle.
             f'way({around})["barrier"];',
             f'node({around})["public_transport"];',
             f'way({around})["public_transport"];',
             f'node({around})["highway"="bus_stop"];',
             f'node({around})["railway"="tram_stop"];',
             f'node({around})["amenity"="bus_station"];',
             f'way({around})["amenity"="bus_station"];']
    if osm_ids:
        parts.insert(0, f"node(id:{','.join(str(i) for i in osm_ids)});")
    body = "\n  ".join(parts)
    return (f"[out:json][timeout:180];\n(\n  {body}\n);\nout meta;\n"
            f">;\nout meta;\n")


def run_query(query: str, timeout: int = 200) -> dict:
    """Ejecuta la consulta probando los dos endpoints, con reintentos."""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last = None
    for endpoint in ENDPOINTS:
        for pause in (0,) + RETRY_PAUSES:
            if pause:
                time.sleep(pause)
            req = urllib.request.Request(
                endpoint, data=data,
                headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                last = f"{endpoint} HTTP {exc.code}"
                if exc.code not in RETRY_STATUS:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last = f"{endpoint}: {exc}"
            except json.JSONDecodeError as exc:
                last = f"{endpoint}: respuesta no es JSON ({exc})"
                break
    raise OverpassError(f"Overpass no respondió; último intento: {last}")


def load_raw(path: Path, osm_ids, lat, lon, radius=DEFAULT_RADIUS_M,
             refresh: bool = False) -> tuple[dict, str]:
    """Devuelve (json crudo, origen) usando la caché versionada."""
    if path.exists() and not refresh:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), f"caché {path}"
    try:
        raw = run_query(build_query(list(osm_ids), lat, lon, radius))
    except OverpassError as exc:
        if path.exists():
            with open(path, encoding="utf-8") as fh:
                return json.load(fh), f"caché {path} (Overpass falló: {exc})"
        raise OverpassError(
            f"{exc}. Sin red y sin caché en {path}: vuelve a intentar con "
            f"conexión, o exporta con --no-context para generar el archivo "
            f"sin objetos de OSM.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    return raw, f"Overpass ({path} actualizado)"


@dataclass
class ForeignNode:
    osm_id: int
    lat: float
    lon: float
    tags: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)


@dataclass
class ForeignWay:
    osm_id: int
    node_ids: list[int]
    tags: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)


META_KEYS = ("version", "timestamp", "changeset", "user", "uid")


class StationContext:
    """Los objetos de OSM del entorno, ya proyectados al marco local."""

    def __init__(self, raw: dict, frame, source: str = ""):
        self.raw = raw
        self.frame = frame
        self.source = source
        self.nodes: dict[int, ForeignNode] = {}
        self.ways: dict[int, ForeignWay] = {}
        for el in raw.get("elements", []):
            meta = {k: el[k] for k in META_KEYS if k in el}
            if el["type"] == "node":
                self.nodes[el["id"]] = ForeignNode(
                    el["id"], el["lat"], el["lon"],
                    dict(el.get("tags", {})), meta)
            elif el["type"] == "way":
                self.ways[el["id"]] = ForeignWay(
                    el["id"], list(el.get("nodes", [])),
                    dict(el.get("tags", {})), meta)

    # ---------------- consultas ----------------

    def local(self, osm_id: int) -> tuple[float, float]:
        node = self.nodes[osm_id]
        return self.frame.to_local(node.lat, node.lon)

    def is_footway(self, way: ForeignWay) -> bool:
        return way.tags.get("highway") in FOOTWAY_HIGHWAYS

    def is_outline(self, way: ForeignWay) -> bool:
        return (way.tags.get("building") in OUTLINE_BUILDINGS
                or way.tags.get("public_transport") == "station")

    @staticmethod
    def is_building(way: ForeignWay) -> bool:
        return bool(way.tags.get("building"))

    @staticmethod
    def is_barrier(way: ForeignWay) -> bool:
        return bool(way.tags.get("barrier"))

    @staticmethod
    def is_public_transport(element) -> bool:
        tags = element.tags
        return bool(tags.get("public_transport")
                    or tags.get("highway") == "bus_stop"
                    or tags.get("railway") == "tram_stop"
                    or tags.get("amenity") == "bus_station")

    def classify(self, element) -> str:
        """Clase con la que el resumen cuenta cada objeto del entorno."""
        tags = element.tags
        if isinstance(element, ForeignWay) and self.is_outline(element):
            return "contorno"
        if self.is_public_transport(element):
            return "transporte público"
        if tags.get("highway") in FOOTWAY_HIGHWAYS:
            return "peatonal"
        if tags.get("highway") in ROAD_HIGHWAYS:
            return "calle"
        if tags.get("railway") in TRACK_RAILWAYS:
            return "vía férrea"
        if isinstance(element, ForeignWay) and self.is_building(element):
            return "edificio"
        if isinstance(element, ForeignWay) and self.is_barrier(element):
            return "barrera"
        return "otro"

    def scene_elements(self):
        """Todo lo del entorno que puede entrar como objeto congelado.

        Peatonales, calles, vías urbanas, transporte público, edificios
        y barreras. Es lo que hace que el archivo abierto en JOSM se vea
        dentro de su manzana y no flotando. Los contornos de estación
        quedan fuera: los coloca `_build_station_area`, que decide si el
        área sale del KML, de OSM o de las dos.
        """
        ways, nodes = [], []
        for way in sorted(self.ways.values(), key=lambda w: w.osm_id):
            if self.is_outline(way):
                continue
            if (self.is_footway(way)
                    or way.tags.get("highway") in ROAD_HIGHWAYS
                    or way.tags.get("railway") in TRACK_RAILWAYS
                    or self.is_building(way)
                    or self.is_barrier(way)
                    or self.is_public_transport(way)):
                ways.append(way)
        for node in sorted(self.nodes.values(), key=lambda n: n.osm_id):
            if node.tags and self.is_public_transport(node):
                nodes.append(node)
        return ways, nodes

    def outline_ways(self) -> list[ForeignWay]:
        out = []
        for way in self.ways.values():
            if (way.tags.get("building") in OUTLINE_BUILDINGS
                    or way.tags.get("public_transport") == "station"):
                out.append(way)
        return sorted(out, key=lambda w: w.osm_id)

    def local_line(self, way: ForeignWay):
        out = []
        for nid in way.node_ids:
            node = self.nodes.get(nid)
            if node is not None:
                out.append(self.frame.to_local(node.lat, node.lon))
        return out

    def nearest_point(self, u: float, v: float, max_dist: float):
        """Punto más cercano sobre una peatonal, no necesariamente vértice.

        Sirve para saber hacia dónde queda la banqueta: el vértice más
        cercano de una línea paralela puede estar muy en diagonal y daría
        un rumbo equivocado.
        """
        best = None
        for way in sorted(self.ways.values(), key=lambda w: w.osm_id):
            if not self.is_footway(way):
                continue
            line = self.local_line(way)
            for a, b in zip(line, line[1:]):
                d, t = point_segment_distance((u, v), a, b)
                if best is not None and d >= best[2]:
                    continue
                point = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                best = (way, point, d)
        if best is None or best[2] > max_dist:
            return None
        return best

    def nearest_vertices(self, u: float, v: float, max_dist: float
                         ) -> list[tuple[ForeignWay, int, float]]:
        """Vértice más cercano de cada way peatonal dentro de `max_dist`.

        Una por way, y siempre un vértice existente: así el connector se
        engancha sin modificar la geometría ajena. Solo peatonales: el
        eje de una calzada no es una banqueta, y conectarse a él es peor
        que no conectarse.
        """
        found = []
        for way in sorted(self.ways.values(), key=lambda w: w.osm_id):
            if not self.is_footway(way):
                continue
            best = None
            for nid in way.node_ids:
                node = self.nodes.get(nid)
                if node is None:
                    continue
                nu, nv = self.frame.to_local(node.lat, node.lon)
                d = math.hypot(nu - u, nv - v)
                if best is None or d < best[2]:
                    best = (way, nid, d)
            if best is None or best[2] > max_dist:
                continue
            found.append(best)
        return sorted(found, key=lambda t: t[2])
