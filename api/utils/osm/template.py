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
        self._index = {}
        for edge in self.edges:
            key = (edge["from"], edge["to"], edge["mode"],
                   edge.get("index", 0))
            if key in self._index:
                raise TemplateError(f"arista duplicada en plantilla: {key}")
            self._index[key] = edge

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

    def unused_edges(self, used: set) -> list[dict]:
        return [e for k, e in self._index.items() if k not in used]

    def resolve_geometry(self, geometry, bow: float = 0.0):
        """Convierte la lista de la plantilla en puntos (u, v).

        Cada elemento es una clave de nodo («N-05») o un par [u, v].
        `bow` desplaza el punto medio en perpendicular: es lo que
        separa en pantalla dos pathways paralelos que comparten sus dos
        extremos (escalera y escalera eléctrica del mismo tramo).
        """
        points = []
        for item in geometry:
            if isinstance(item, str):
                points.append(self.point(item))
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
