"""Carga y resolución de las plantillas de familia arquitectónica."""
from __future__ import annotations

import json
from pathlib import Path

from .geometry import offset_midpoint


class TemplateError(Exception):
    pass


class FamilyTemplate:

    def __init__(self, data: dict, path: Path):
        self.path = path
        self.family = data.get("family") or path.stem
        self.description = data.get("description", "")
        self.nodes: dict[str, dict] = data.get("nodes", {})
        self.edges: list[dict] = data.get("edges", [])
        self.extra_ways: list[dict] = data.get("extra_ways", [])
        self.banks: dict[str, dict] = data.get("banks", {})
        self.station_area: str = data.get("station_area", "kml")
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
        self._bank_slots: dict[int, tuple[str, int, int]] = {}
        self._index_banks()

    def _index_banks(self) -> None:
        """Reparte las posiciones laterales de cada banco de escaleras.

        El `index` de los paralelos ordena por `miro_id` y puede repetirse
        entre modos distintos (una escalera fija y dos eléctricas del
        mismo tramo son 0, 0 y 1), así que cuando choca se cae al orden
        de declaración, que sí es único.
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
            slots = [int(e.get("slot", e.get("index", 0))) for e in members]
            if len(set(slots)) != len(slots):
                slots = list(range(len(members)))
                self.bank_warnings.append(
                    f"el banco «{bank_id}» tenía posiciones laterales "
                    f"repetidas; se repartieron por orden de declaración")
            for edge, slot in zip(members, slots):
                self._bank_slots[id(edge)] = (bank_id, slot, len(members))

    def bank_layout(self, edge: dict):
        """(clave del banco, posición lateral, cuántas escaleras) o None."""
        return self._bank_slots.get(id(edge))

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

    def resolve_geometry(self, geometry, bow: float = 0.0):
        """Convierte la lista de la plantilla en puntos (u, v).

        Cada elemento es una clave de nodo («N-05»), un par [u, v] o un
        punto sobre la senda de un andén, `{"spine": "P-01", "u": 15,
        "dv": 1.5}`, cuya v no se puede escribir a mano porque sale de la
        franja del KML. `bow` desplaza el punto medio en perpendicular:
        es lo que separa en pantalla dos pathways paralelos que comparten
        sus dos extremos (escalera y escalera eléctrica del mismo tramo).
        """
        points = []
        for item in geometry:
            if isinstance(item, str):
                points.append(self.point(item))
            elif isinstance(item, dict):
                points.append(self.spine_point(item))
            else:
                points.append((float(item[0]), float(item[1])))
        if len(points) < 2:
            raise TemplateError(
                f"la plantilla {self.family} declara una geometría de "
                f"{len(points)} punto(s): {geometry}")
        if bow and len(points) == 2:
            points = [points[0], offset_midpoint(points[0], points[1], bow),
                      points[1]]
        return points
