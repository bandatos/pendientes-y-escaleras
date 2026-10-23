"""Carga y resolución de las plantillas de familia arquitectónica."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from .fit import orthogonal_route
from .geometry import offset_midpoint, unit


class TemplateError(Exception):
    pass


PATCH_DICT_SECTIONS = ("nodes", "banks", "fit", "station_node")


def _merge(base, patch):
    """Mezcla profunda: un dict entra clave por clave, `null` borra la
    clave y cualquier otro valor (listas incluidas) sustituye."""
    if not isinstance(base, dict) or not isinstance(patch, dict):
        return copy.deepcopy(patch)
    out = dict(base)
    for key, value in patch.items():
        if key == "comment" and key in out:
            # El comentario del bloque explica el cambio; el de la pieza
            # de la familia sigue valiendo para las demás estaciones.
            out[key] = f"{out[key]} [{value}]"
        elif value is None:
            out.pop(key, None)
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def edge_key(edge: dict) -> str:
    """«from>to:modo:índice», el nombre de una arista en un bloque."""
    return (f"{edge['from']}>{edge['to']}:{edge['mode']}:"
            f"{edge.get('index', 0)}")


def _parse_edge_key(key: str, where: str) -> dict:
    try:
        ends, mode, *rest = key.split(":")
        a, b = ends.split(">")
        return {"from": a, "to": b, "mode": int(mode),
                "index": int(rest[0]) if rest else 0}
    except ValueError:
        raise TemplateError(
            f"el bloque de {where} nombra la arista «{key}»; el formato es "
            f"«N-01>N-02:modo:índice»")


def patch_template_data(data: dict, block: dict, where: str) -> dict:
    """Copia de la plantilla con las piezas del bloque por estación.

    Cada sección del bloque es un dict de piezas por nombre: nodos y
    bancos por su clave, aristas por «from>to:modo:índice», extra_ways
    por su `id`. Un valor `null` quita la pieza, un dict la mezcla sobre
    la de la plantilla y una pieza que la plantilla no tiene se añade.
    """
    out = copy.deepcopy(data)
    for section in PATCH_DICT_SECTIONS:
        if section not in block:
            continue
        patch = block[section]
        if patch is None:
            out.pop(section, None)
        elif section in ("fit", "station_node"):
            out[section] = _merge(out.get(section) or {}, patch)
        else:
            pieces = out.setdefault(section, {})
            for key, value in patch.items():
                if value is None:
                    pieces.pop(key, None)
                else:
                    pieces[key] = _merge(pieces.get(key, {}), value)
    if "edges" in block:
        edges = out.setdefault("edges", [])
        for key, value in block["edges"].items():
            ident = _parse_edge_key(key, where)
            found = [i for i, e in enumerate(edges)
                     if (e["from"], e["to"], e["mode"], e.get("index", 0))
                     == (ident["from"], ident["to"], ident["mode"],
                         ident["index"])]
            if value is None:
                for i in reversed(found):
                    edges.pop(i)
            elif found:
                edges[found[0]] = _merge(edges[found[0]], value)
            else:
                edges.append(_merge(ident, value))
    if "extra_ways" in block:
        extras = out.setdefault("extra_ways", [])
        for key, value in block["extra_ways"].items():
            found = [i for i, e in enumerate(extras) if e.get("id") == key]
            if value is None:
                for i in reversed(found):
                    extras.pop(i)
            elif found:
                extras[found[0]] = _merge(extras[found[0]], value)
            elif "geometry" not in value:
                raise TemplateError(
                    f"el bloque de {where} modifica el extra_way «{key}», "
                    f"que la plantilla no tiene, y no trae geometry para "
                    f"añadirlo")
            else:
                extras.append(_merge({"id": key}, value))
    unknown = set(block) - set(PATCH_DICT_SECTIONS) - {
        "edges", "extra_ways", "comment"}
    if unknown:
        raise TemplateError(
            f"el bloque de {where} trae secciones que no se aplican: "
            f"{', '.join(sorted(unknown))}")
    return out


class FamilyTemplate:

    def __init__(self, data: dict, path: Path):
        self.path = path
        self.station: str | None = None
        self.local_patch: dict | None = None
        self.area_override: dict | None = None
        # El encaje en una hermana reescribe la plantilla a partir de los
        # datos crudos, así que se conservan tal como vinieron.
        self.data = data
        self.fit: dict | None = data.get("fit")
        self.station_node: dict | None = data.get("station_node")
        # Anillos del área en metros locales —exterior e islas—, para
        # trazar los codos de un `via` cuando la cascada se movió y sus
        # puntos ya no valen.
        self.area_rings: list[list[tuple[float, float]]] | None = None
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
    def load(cls, path: Path, station: str | None = None
             ) -> "FamilyTemplate":
        """Carga la plantilla con el bloque de `station` ya aplicado.

        Las piezas de la raíz del bloque se aplican aquí, en el marco de
        la estación de referencia y antes del encaje; las de `local`, en
        el marco de la propia estación y después del encaje
        (`apply_local_patch`); `area` sustituye el polígono del KML.
        """
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        stations = data.pop("stations", None) or {}
        block = stations.get(station) if station else None
        local, area = None, None
        if block:
            block = dict(block)
            local = block.pop("local", None)
            area = block.pop("area", None)
            data = patch_template_data(data, block, station)
        template = cls(data, path)
        template.station = station if block else None
        template.local_patch = local
        template.area_override = area
        return template

    def apply_local_patch(self, data: dict) -> dict:
        """Datos ya encajados con las piezas `local` del bloque encima."""
        if not getattr(self, "local_patch", None):
            return data
        return patch_template_data(data, self.local_patch,
                                   f"{self.station} (local)")

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
        elbows = []
        for item in geometry:
            if isinstance(item, str):
                points.append(self.point(item))
            elif isinstance(item, dict) and "via" in item:
                vias.append((len(points), item))
                points.append(None)
            elif isinstance(item, dict) and "elbow" in item:
                elbows.append((len(points), item))
                points.append(None)
            elif isinstance(item, dict) and "bank" in item:
                points.append(self.bank_junction(item))
            elif isinstance(item, dict):
                points.append(self.spine_point(item))
            else:
                points.append((float(item[0]), float(item[1])))
        for index, item in reversed(elbows):
            points[index:index + 1] = self._elbow_points(points, index, item)
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

    def _elbow_points(self, points, index: int, item: dict):
        """Codo en cuarto de círculo de radio fijo en la esquina dada.

        La esquina es el cruce de las dos piernas rectas, la que llega del
        punto anterior y la que sigue al siguiente; el arco es tangente a
        las dos, a `radius` metros de la esquina. Se declara así, y no con
        sus vértices, para que el radio sobreviva a la deformación de los
        corredores en una estación hermana: la esquina se deforma, el arco
        se rehace.
        """
        if index == 0 or index + 1 >= len(points):
            raise TemplateError(
                f"la plantilla {self.family} pone un elbow en una punta de "
                f"la geometría; tiene que ir entre dos puntos")
        corner = (float(item["elbow"][0]), float(item["elbow"][1]))
        radius = float(item["radius"])
        segments = int(item.get("segments", 4))
        prev, nxt = points[index - 1], points[index + 1]
        if prev is None or nxt is None:
            raise TemplateError(
                f"la plantilla {self.family} pone un elbow junto a un via; "
                f"necesita dos puntos fijos a los lados")
        d_in = unit(corner, prev)
        d_out = unit(corner, nxt)
        if abs(d_in[0] * d_out[0] + d_in[1] * d_out[1]) > 0.05:
            raise TemplateError(
                f"la plantilla {self.family} pone un elbow en ({corner[0]:g}"
                f", {corner[1]:g}) entre dos piernas que no son "
                f"perpendiculares; el codo es un cuarto de círculo")
        start = (corner[0] + d_in[0] * radius, corner[1] + d_in[1] * radius)
        centre = (start[0] + d_out[0] * radius,
                  start[1] + d_out[1] * radius)
        a0 = math.atan2(start[1] - centre[1], start[0] - centre[0])
        end = (corner[0] + d_out[0] * radius,
               corner[1] + d_out[1] * radius)
        a1 = math.atan2(end[1] - centre[1], end[0] - centre[0])
        sweep = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        return [(centre[0] + radius * math.cos(a0 + sweep * k / segments),
                 centre[1] + radius * math.sin(a0 + sweep * k / segments))
                for k in range(segments + 1)]

    def _via_points(self, points, index: int, item: dict):
        if not item.get("moved"):
            return [(float(p[0]), float(p[1])) for p in item["via"]]
        if index == 0 or index + 1 >= len(points):
            raise TemplateError(
                f"la plantilla {self.family} pone un via en una punta de "
                f"la geometría; tiene que ir entre dos puntos")
        prev, nxt = points[index - 1], points[index + 1]
        if self.area_rings is None:
            return []
        before = points[index - 2] if index >= 2 else None
        corner, outside = orthogonal_route(prev, nxt, self.area_rings,
                                           before)
        if outside > 0:
            self.route_warnings.append(
                f"el tramo de ({prev[0]:.1f}, {prev[1]:.1f}) a "
                f"({nxt[0]:.1f}, {nxt[1]:.1f}) no encontró un codo dentro "
                f"del área; se sale {outside:.1f} m")
        return [corner]
