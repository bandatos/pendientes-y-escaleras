"""Encaje de una plantilla en el área del KML de una estación hermana.

La plantilla de una familia es el trazo de su estación de referencia
(San Pedro de los Pinos en L7), escrito en metros de ese marco local. En
una hermana el polígono del KML tiene la misma topología pero no las
mismas medidas: los ramales salen en otra u, el vestíbulo transversal
queda a otra distancia de la franja, y el rectángulo de salida puede ir
girado respecto de las vías. Ricardo: «todos los trazos deberían caber
dentro del área de la estación».

Dos piezas, cada una con su regla:

- **Corredores** (pasillos de andén, vestíbulo transversal, paso bajo
  las vías): se deforman a lo largo de u por tramos, llevando los ramales
  de la referencia a los ramales medidos, y a lo largo de v llevando el
  borde de la franja y el eje del vestíbulo transversal a los medidos.
- **Cascadas** (los bancos de escaleras hasta el pabellón, con sus
  pasillos y vestíbulos): se mueven en bloque, sin deformarse, con uno de
  los ocho giros y reflejos del cuadrado, anclados al pabellón de OSM.
  Se prueban todos y se queda el que cabe íntegro en el área.
"""
from __future__ import annotations

import copy
import math

from .geometry import (point_in_polygon, point_in_polygon_tol, ring_crossings,
                       ring_spans_at_u)

# Las ocho simetrías del cuadrado como matrices (a, b, c, d) que llevan
# (du, dv) a (a·du + b·dv, c·du + d·dv). La primera es la identidad.
DIHEDRAL = (
    ((1, 0, 0, 1), "paralela a las vías, como la plantilla"),
    ((-1, 0, 0, -1), "paralela a las vías, girada 180°"),
    ((1, 0, 0, -1), "paralela a las vías, reflejada a lo ancho"),
    ((-1, 0, 0, 1), "paralela a las vías, reflejada a lo largo"),
    ((0, -1, 1, 0), "perpendicular a las vías, girada 90°"),
    ((0, 1, -1, 0), "perpendicular a las vías, girada -90°"),
    ((0, 1, 1, 0), "perpendicular a las vías, reflejada (u→+v)"),
    ((0, -1, -1, 0), "perpendicular a las vías, reflejada (u→-v)"),
)

SIDE_VECTORS = {"+u": (1.0, 0.0), "-u": (-1.0, 0.0),
                "+v": (0.0, 1.0), "-v": (0.0, -1.0)}

# Cuánto pueden discrepar ramales, franja y vestíbulo de la referencia
# antes de que valga la pena deformar: por debajo es ruido del trazo del
# KML y la plantilla se deja tal cual.
DEFAULT_WARP_TOLERANCE_M = 1.5
# Distancia, más allá del borde de la franja, a la que se cortan los
# ramales: lo bastante cerca para no llegar al vestíbulo transversal.
DEFAULT_BRANCH_PROBE_M = 2.0


def apply_matrix(matrix, vector):
    a, b, c, d = matrix
    return (a * vector[0] + b * vector[1], c * vector[0] + d * vector[1])


def matrix_det(matrix) -> int:
    a, b, c, d = matrix
    return a * d - b * c


def side_name(vector) -> str:
    du, dv = vector
    if abs(du) >= abs(dv):
        return "+u" if du >= 0 else "-u"
    return "+v" if dv >= 0 else "-v"


def direction_label(vector) -> str:
    """Rumbo de un eje en palabras del marco local, para el reporte."""
    name = side_name(vector)
    along = "paralela a las vías" if name in ("+u", "-u") else (
        "perpendicular a las vías")
    return f"{name} ({along})"


# ---------------- medidas del KML ----------------

def branch_centres(ring, band, side: str,
                   probe: float = DEFAULT_BRANCH_PROBE_M) -> list[float]:
    """u del eje de cada ramal que sale de la franja por un lado.

    Se corta el anillo con una recta paralela a la franja, `probe` metros
    afuera de su borde; cada tramo dentro del polígono es un ramal.
    """
    v = band[1] + probe if side == "+v" else band[0] - probe
    cuts = ring_crossings(ring, v)
    return [(cuts[i] + cuts[i + 1]) / 2 for i in range(0, len(cuts) - 1, 2)]


def transversal_centre(ring, band, side: str, branches) -> float | None:
    """v del eje del vestíbulo transversal de un lado.

    Entre dos ramales vecinos, el primer tramo de polígono fuera de la
    franja es el vestíbulo que los une; su eje es el promedio de esos
    cortes.
    """
    found = []
    for left, right in zip(branches, branches[1:]):
        u = (left + right) / 2
        spans = ring_spans_at_u(ring, u)
        if side == "+v":
            outside = [s for s in spans if s[0] > band[1] - 0.5]
            span = min(outside, key=lambda s: s[0]) if outside else None
        else:
            outside = [s for s in spans if s[1] < band[0] + 0.5]
            span = max(outside, key=lambda s: s[1]) if outside else None
        if span is not None:
            found.append((span[0] + span[1]) / 2)
    if not found:
        return None
    return sum(found) / len(found)


def measure(ring, band, probe: float = DEFAULT_BRANCH_PROBE_M) -> dict:
    """Ramales y vestíbulos transversales de los dos lados de la franja."""
    out = {"band": list(band), "branches": {}, "transversal": {}}
    for side in ("+v", "-v"):
        centres = branch_centres(ring, band, side, probe)
        out["branches"][side] = centres
        out["transversal"][side] = transversal_centre(
            ring, band, side, centres)
    return out


# ---------------- deformación de corredores ----------------

class CorridorWarp:
    """Deformación por tramos de la referencia a la estación hermana.

    En u, una función lineal por tramos que lleva cada ramal de la
    referencia a su ramal medido, con pendiente 1 más allá de los
    extremos. En v, por lado: el borde de la franja va a su borde y el eje
    del vestíbulo transversal a su eje; más allá del vestíbulo, una
    traslación. Dentro de la franja no se toca nada: ahí mandan la senda
    y el ancho del andén, que ya salen del KML.
    """

    def __init__(self, ref_branches, target_branches, ref_band,
                 target_band, ref_trans: dict, target_trans: dict):
        self.u_pairs = list(zip(ref_branches, target_branches))
        self.ref_band = ref_band
        self.target_band = target_band
        self.ref_trans = ref_trans
        self.target_trans = target_trans

    def u(self, u: float) -> float:
        pairs = self.u_pairs
        if not pairs:
            return u
        if u <= pairs[0][0]:
            return u - pairs[0][0] + pairs[0][1]
        if u >= pairs[-1][0]:
            return u - pairs[-1][0] + pairs[-1][1]
        for (r0, t0), (r1, t1) in zip(pairs, pairs[1:]):
            if r0 <= u <= r1:
                return t0 + (u - r0) * (t1 - t0) / (r1 - r0)
        return u

    def v(self, v: float) -> float:
        if self.ref_band[0] <= v <= self.ref_band[1]:
            return v
        side = "+v" if v > self.ref_band[1] else "-v"
        edge_r = self.ref_band[1] if side == "+v" else self.ref_band[0]
        edge_t = self.target_band[1] if side == "+v" else (
            self.target_band[0])
        trans_r, trans_t = self.ref_trans[side], self.target_trans[side]
        if (v - edge_r) * (v - trans_r) <= 0:
            return edge_t + (v - edge_r) * (trans_t - edge_t) / (
                trans_r - edge_r)
        return v - trans_r + trans_t

    def point(self, p) -> list[float]:
        return [self.u(float(p[0])), self.v(float(p[1]))]


def compare_measures(reference: dict, target: dict) -> tuple[float, str]:
    """(mayor discrepancia en metros, descripción), o (inf, motivo)."""
    worst = 0.0
    for side in ("+v", "-v"):
        ref_b = reference["branches"].get(side) or []
        tgt_b = target["branches"].get(side) or []
        if len(ref_b) != len(tgt_b):
            return math.inf, (
                f"el lado {side} tiene {len(tgt_b)} ramales y la "
                f"referencia {len(ref_b)}")
        worst = max([worst] + [abs(a - b) for a, b in zip(ref_b, tgt_b)])
        ref_t = reference["transversal"].get(side)
        tgt_t = target["transversal"].get(side)
        if ref_t is None or tgt_t is None:
            return math.inf, f"no se encontró el vestíbulo del lado {side}"
        worst = max(worst, abs(ref_t - tgt_t))
    return worst, ""


def mean_branches(target: dict) -> list[float]:
    """Ramales de los dos lados promediados: una sola deformación en u.

    El paso bajo las vías y el nodo de estación cruzan la franja; con una
    deformación por lado quedarían chuecos.
    """
    east = target["branches"]["+v"]
    west = target["branches"]["-v"]
    return [(a + b) / 2 for a, b in zip(east, west)]


def warp_template_data(data: dict, warp: CorridorWarp,
                       cascade_of) -> dict:
    """Copia de la plantilla con los corredores deformados.

    `cascade_of(kind, key_or_index)` dice si una pieza es de una cascada,
    que no se deforma: se moverá en bloque después.
    """
    out = copy.deepcopy(data)

    def warp_items(geometry):
        new = []
        for item in geometry:
            if isinstance(item, list) and len(item) == 2:
                new.append(warp.point(item))
            elif isinstance(item, dict) and "spine" in item:
                moved = dict(item)
                moved["u"] = warp.u(float(item["u"]))
                new.append(moved)
            elif isinstance(item, dict) and "elbow" in item:
                moved = dict(item)
                moved["elbow"] = warp.point(item["elbow"])
                new.append(moved)
            elif isinstance(item, dict) and "via" in item:
                # Los vértices de paso son del trazo de referencia: con
                # los corredores deformados ya no caen donde deben.
                moved = dict(item)
                moved["moved"] = True
                new.append(moved)
            else:
                new.append(item)
        return new

    for key, spec in out.get("nodes", {}).items():
        if cascade_of("node", key) or "u" not in spec:
            continue
        spec["u"] = warp.u(float(spec["u"]))
        if "v" in spec:
            spec["v"] = warp.v(float(spec["v"]))
    for edge in out.get("edges", []):
        if "geometry" in edge and not cascade_of("edge", edge):
            edge["geometry"] = warp_items(edge["geometry"])
    for extra in out.get("extra_ways", []):
        if extra.get("cascade"):
            continue
        extra["geometry"] = warp_items(extra["geometry"])
        turn = extra.get("turnstile")
        if turn and isinstance(turn.get("from"), list):
            turn["from"] = warp.point(turn["from"])
    station = out.get("station_node")
    if station and "u" in station:
        station["u"] = warp.u(float(station["u"]))
    return out


# ---------------- cascadas en bloque ----------------

class RigidMove:
    """Giro o reflejo alrededor del ancla de referencia, más traslado.

    `scale` acorta a lo largo del eje de la cascada (el de sus bancos en
    la referencia) cuando ninguna orientación cabe con los largos de la
    referencia; el ancho no se toca.
    """

    def __init__(self, matrix, ref_anchor, target_anchor, axis,
                 scale: float = 1.0):
        self.matrix = matrix
        self.ref_anchor = ref_anchor
        self.target_anchor = target_anchor
        self.axis = axis
        self.scale = scale

    @property
    def identity(self) -> bool:
        return (self.matrix == DIHEDRAL[0][0] and self.scale == 1.0
                and math.hypot(self.target_anchor[0] - self.ref_anchor[0],
                               self.target_anchor[1] - self.ref_anchor[1])
                < 1e-9)

    def _scaled(self, du: float, dv: float):
        if self.scale == 1.0:
            return du, dv
        au, av = self.axis
        along = du * au + dv * av
        cross_u, cross_v = du - along * au, dv - along * av
        along *= self.scale
        return cross_u + along * au, cross_v + along * av

    def point(self, p) -> list[float]:
        du, dv = self._scaled(float(p[0]) - self.ref_anchor[0],
                              float(p[1]) - self.ref_anchor[1])
        ru, rv = apply_matrix(self.matrix, (du, dv))
        return [self.target_anchor[0] + ru, self.target_anchor[1] + rv]

    def vector(self, vector):
        return apply_matrix(self.matrix, vector)

    def side(self, name: str) -> str:
        return side_name(apply_matrix(self.matrix, SIDE_VECTORS[name]))


def direction_vector(raw):
    if isinstance(raw, str):
        return SIDE_VECTORS[raw]
    angle = math.radians(float(raw))
    return (math.cos(angle), math.sin(angle))


def move_cascade(data: dict, group: dict, move: RigidMove) -> dict:
    """Copia de la plantilla con una cascada movida en bloque."""
    if move.identity:
        return data
    out = copy.deepcopy(data)
    det = matrix_det(move.matrix)
    banks = out.get("banks", {})
    for bank_id in group["banks"]:
        spec = banks[bank_id]
        if "junction" in spec:
            spec["junction"] = move.point(spec["junction"])
        if "axis" in spec:
            spec["axis"] = [move.point(p) for p in spec["axis"]]
        if "direction" in spec:
            du, dv = move.vector(direction_vector(spec["direction"]))
            spec["direction"] = math.degrees(math.atan2(dv, du))
        if move.scale != 1.0:
            if "length" in spec:
                spec["length"] = float(spec["length"]) * move.scale
            lead = spec.get("lead")
            if isinstance(lead, list):
                spec["lead"] = [float(x) * move.scale for x in lead]
            elif lead is not None:
                spec["lead"] = float(lead) * move.scale
        # El corrimiento lateral se mide a la derecha de quien sube: en
        # un reflejo la cascada entera se ve en espejo, y el corrimiento
        # tiene que reflejarse con ella para no caer sobre otra escalera.
        if det < 0 and "stack_offset" in spec:
            spec["stack_offset"] = -float(spec["stack_offset"])
    for key in group["nodes"]:
        spec = out["nodes"].get(key)
        if spec is None or "u" not in spec or "v" not in spec:
            continue
        spec["u"], spec["v"] = move.point((spec["u"], spec["v"]))
        building = spec.get("building")
        if building:
            if building.get("stair_side"):
                building["stair_side"] = move.side(building["stair_side"])
            building["closed_doors"] = [
                move.side(item) if isinstance(item, str) else item
                for item in building.get("closed_doors", [])]
    for extra in out.get("extra_ways", []):
        if extra.get("cascade") != group["name"]:
            continue
        extra["geometry"] = [
            move.point(item) if isinstance(item, list) else item
            for item in extra["geometry"]]
        turn = extra.get("turnstile")
        if turn and isinstance(turn.get("from"), list):
            turn["from"] = move.point(turn["from"])
    for extra in out.get("extra_ways", []):
        for item in extra["geometry"]:
            if isinstance(item, dict) and item.get("cascade") == (
                    group["name"]):
                item["moved"] = True
    return out


# ---------------- comprobaciones ----------------

def outside_points(ring, points, tol: float):
    """[(distancia fuera, punto)] de los que no caben en el anillo."""
    out = []
    for p in points:
        inside, distance = point_in_polygon_tol(ring, p, tol)
        if not inside:
            out.append((distance, p))
    return out


def sample_segment(a, b, step: float = 1.0):
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    count = max(1, int(length / step))
    return [(a[0] + (b[0] - a[0]) * k / count,
             a[1] + (b[1] - a[1]) * k / count) for k in range(count + 1)]


def orthogonal_route(prev, nxt, ring, before=None, tol: float = 0.3):
    """Codo en L de `prev` a `nxt` que quede dentro del área.

    Se prueba primero el codo que sigue la dirección con la que se llegó
    a `prev`, para que el pasillo no dé media vuelta. Devuelve
    (vértice del codo o None, metros fuera del área).
    """
    corners = [(prev[0], nxt[1]), (nxt[0], prev[1])]
    if before is not None:
        du, dv = prev[0] - before[0], prev[1] - before[1]
        # Si se llegaba a lo largo de v, conviene seguir en v primero.
        if abs(du) > abs(dv):
            corners.reverse()
    best = None
    for corner in corners:
        pts = sample_segment(prev, corner) + sample_segment(corner, nxt)
        worst = max((d for d, _ in outside_points(ring, pts, tol)),
                    default=0.0)
        if worst == 0.0:
            return corner, 0.0
        if best is None or worst < best[1]:
            best = (corner, worst)
    return best


def inside_fraction(shape, ring, step: float = 1.0) -> float:
    """Fracción de la superficie de `shape` que cae dentro de `ring`."""
    us = [p[0] for p in shape]
    vs = [p[1] for p in shape]
    total = inside = 0
    u = min(us) + step / 2
    while u < max(us):
        v = min(vs) + step / 2
        while v < max(vs):
            if point_in_polygon(shape, (u, v)):
                total += 1
                if point_in_polygon(ring, (u, v)):
                    inside += 1
            v += step
        u += step
    return inside / total if total else 0.0
