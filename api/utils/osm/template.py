"""Carga y resolución de las plantillas de familia arquitectónica."""
from __future__ import annotations

import json
from pathlib import Path

from .fit import orthogonal_route
from .geometry import offset_midpoint


class TemplateError(Exception):
    pass


class FamilyTemplate:

    def __init__(self, data: dict, path: Path):
        self.path = path
        # El encaje en una hermana reescribe la plantilla a partir de los
        # datos crudos, así que se conservan tal como vinieron.
        self.data = data
        self.fit: dict | None = data.get("fit")
        self.station_node: dict | None = data.get("station_node")
        # Anillo del área en metros locales, para trazar los codos de un
        # `via` cuando la cascada se movió y sus puntos ya no valen.
        self.area_ring: list[tuple[float, float]] | None = None
        self.route_warnings: list[str] = []
        self.family = data.get("family") or path.stem
        self.description = data.get("description", "")
        self.nodes: dict[str, dict] = data.get("nodes", {})
        self.edges: list[dict] = data.get("edges", [])
        self.extra_ways: list[dict] = data.get("extra_ways", [])
        self.banks: dict[str, dict] = data.get("banks", {})
        self.station_area: str = data.get("station_area", "kml")
        # Hacia dónde corre de ordinario una escalera reversible, que
        # decide de qué lado del banco va: en L7 bajan.
        self.reversible_runs: str = data.get("reversible_runs", "down")
        # El edificio de acceso mueve el acceso a la puerta y el nodo
        # interior al centro del lado opuesto; el resto de la plantilla
        # sigue nombrando esas claves, así que la corrección se aplica
        # aquí y no en cada geometría.
        self.overrides: dict[str, tuple[float, float]] = {}
        # v de la senda de cada andén, que solo se sabe al dibujarlo
        # porque sale de la franja del KML; las geometrías se cuelgan de
        # ella con {"spine": "P-01", "u": 15}.
        self.spine_anchors: dict[str, float] = {}
        self._index = {}
        for edge in self.edges:
            key = (edge["from"], edge["to"], edge["mode"],
                   edge.get("index", 0))
            if key in self._index:
                raise TemplateError(f"arista duplicada en plantilla: {key}")
            self._index[key] = edge
        self.bank_warnings: list[str] = []
        self._bank_members: dict[int, tuple[str, int | None, int]] = {}
        # Nodos de encuentro de cada banco, que solo se conocen al
        # planearlo; los extra_ways se cuelgan de ellos con
        # {"bank": "cascada-oriente-1", "end": "to"}.
        self.bank_junctions: dict[str, dict[str, tuple[float, float]]] = {}
        self._index_banks()

    def _index_banks(self) -> None:
        """Agrupa las aristas de cada banco de escaleras.

        La posición lateral de cada escalera no se fija aquí: la
        calcula el generador con la regla de sentidos, que necesita los
        niveles del grafo. Un `slot` escrito a mano queda como override.
        """
        groups: dict[str, list[dict]] = {}
        for edge in self.edges:
            bank_id = edge.get("bank")
            if bank_id is None:
                continue
            if bank_id not in self.banks:
                raise TemplateError(
                    f"la arista {edge['from']}->{edge['to']} de la "
                    f"plantilla {self.family} pide el banco «{bank_id}», "
                    f"que la sección banks no declara")
            groups.setdefault(bank_id, []).append(edge)
        for bank_id, members in groups.items():
            for edge in members:
                manual = edge.get("slot")
                self._bank_members[id(edge)] = (
                    bank_id, None if manual is None else int(manual),
                    len(members))

    def bank_layout(self, edge: dict):
        """(clave del banco, slot manual o None, cuántas escaleras) o None."""
        return self._bank_members.get(id(edge))

    def bank(self, bank_id: str) -> dict:
        try:
            return self.banks[bank_id]
        except KeyError:
            raise TemplateError(
                f"la plantilla {self.family} no declara el banco {bank_id}")

    @classmethod
    def load(cls, path: Path) -> "FamilyTemplate":
        with open(path, encoding="utf-8") as fh:
            return cls(json.load(fh), path)

    def node(self, key: str) -> dict:
        try:
            return self.nodes[key]
        except KeyError:
            raise TemplateError(
                f"la plantilla {self.family} no ubica el nodo {key}")

    def point(self, key: str) -> tuple[float, float]:
        if key in self.overrides:
            return self.overrides[key]
        spec = self.node(key)
        return float(spec["u"]), float(spec["v"])

    def edge(self, from_key: str, to_key: str, mode: int, index: int,
             bidirectional: bool = False) -> tuple[tuple | None, dict | None]:
        """Busca la arista y devuelve (clave usada, arista).

        En un pathway bidireccional el orden from/to que guardó la base
        es el del conector que se trazó en Miró, y ese orden no es
        información: la misma escalera aparece como P-01->N-01 en una
        estación y como N-01->P-01 en su hermana. Por eso el par se
        busca también al revés. En los de un solo sentido el orden sí
        significa, así que ahí no se intenta el par invertido.
        """
        key = (from_key, to_key, mode, index)
        if key in self._index:
            return key, self._index[key]
        if bidirectional:
            key = (to_key, from_key, mode, index)
            if key in self._index:
                return key, self._index[key]
        return None, None

    def has_edge_between(self, a: str, b: str) -> bool:
        return any({k[0], k[1]} == {a, b} for k in self._index)

    def unused_edges(self, used: set) -> list[dict]:
        return [e for k, e in self._index.items() if k not in used]

    def spine_point(self, item: dict) -> tuple[float, float]:
        key = item.get("spine")
        if key not in self.spine_anchors:
            raise TemplateError(
                f"la geometría pide un punto sobre la senda de {key}, que "
                f"la plantilla {self.family} no dibuja como andén (o el "
                f"andén se dibuja después)")
        return (float(item["u"]),
                self.spine_anchors[key] + float(item.get("dv", 0.0)))

    def bank_junction(self, item: dict) -> tuple[float, float]:
        bank_id, end = item["bank"], item.get("end", "to")
        try:
            return self.bank_junctions[bank_id][end]
        except KeyError:
            raise TemplateError(
                f"la geometría pide el nodo de encuentro «{end}» del banco "
                f"{bank_id}, que la plantilla {self.family} no planea")

    def resolve_geometry(self, geometry, bow: float = 0.0):
        """Convierte la lista de la plantilla en puntos (u, v).

        Cada elemento es una clave de nodo («N-05»), un par [u, v] o un
        punto sobre la senda de un andén, `{"spine": "P-01", "u": 15,
        "dv": 1.5}`, cuya v no se puede escribir a mano porque sale de la
        franja del KML, o el nodo de encuentro de un banco, `{"bank":
        "cascada-oriente-1", "end": "to"}`, que sale de planearlo. Un
        `{"via": [[u, v], …], "cascade": "oriente"}` son los vértices de
        paso del trazo de referencia entre sus dos vecinos: valen tal
        cual mientras la cascada no se mueva, y si se movió se cambian por
        un codo en L dentro del área. `bow` desplaza el punto medio en
        perpendicular: es lo que separa en pantalla dos pathways
        paralelos que comparten sus dos extremos (escalera y escalera
        eléctrica del mismo tramo).
        """
        points = []
        vias = []
        for item in geometry:
            if isinstance(item, str):
                points.append(self.point(item))
            elif isinstance(item, dict) and "via" in item:
                vias.append((len(points), item))
                points.append(None)
            elif isinstance(item, dict) and "bank" in item:
                points.append(self.bank_junction(item))
            elif isinstance(item, dict):
                points.append(self.spine_point(item))
            else:
                points.append((float(item[0]), float(item[1])))
        for index, item in reversed(vias):
            points[index:index + 1] = self._via_points(points, index, item)
        if len(points) < 2:
            raise TemplateError(
                f"la plantilla {self.family} declara una geometría de "
                f"{len(points)} punto(s): {geometry}")
        if bow and len(points) == 2:
            points = [points[0], offset_midpoint(points[0], points[1], bow),
                      points[1]]
        return points

    def _via_points(self, points, index: int, item: dict):
        if not item.get("moved"):
            return [(float(p[0]), float(p[1])) for p in item["via"]]
        if index == 0 or index + 1 >= len(points):
            raise TemplateError(
                f"la plantilla {self.family} pone un via en una punta de "
                f"la geometría; tiene que ir entre dos puntos")
        prev, nxt = points[index - 1], points[index + 1]
        if self.area_ring is None:
            return []
        before = points[index - 2] if index >= 2 else None
        corner, outside = orthogonal_route(prev, nxt, self.area_ring, before)
        if outside > 0:
            self.route_warnings.append(
                f"el tramo de ({prev[0]:.1f}, {prev[1]:.1f}) a "
                f"({nxt[0]:.1f}, {nxt[1]:.1f}) no encontró un codo dentro "
                f"del área; se sale {outside:.1f} m")
        return [corner]
