"""Brazos del puente y lóbulos de acceso, medidos en el área del KML.

En la superficie de la Calzada de Tlalpan el área es una franja de
andenes de la que sale, por cada lado, un brazo (el pasillo del puente)
que desemboca en un lóbulo (el pabellón de acceso). Los brazos no son
colineales ni los lóbulos simétricos —en General Anaya los ejes quedan
corridos 19,6 m—, así que la plantilla no puede escribir sus u a mano:
las nombra con una referencia que el generador resuelve aquí, con lo que
mide en el área de la estación.

Una referencia es un dict con `arm` («+v», «-v» o «mid»):

- sin `at`, un número: la u del eje del brazo de ese lado, o la media de
  los dos ejes con «mid»; `du` le suma metros;
- `"at": "door"`, el punto [u, v] de la puerta: el medio del tramo más
  largo de la cara del lóbulo que da a la franja, fuera del brazo;
- `"at": "wall"`, el punto [u, v] sobre el muro del fondo del lóbulo,
  corrido `inset` metros hacia la franja; su u es la del eje del brazo, o
  la de la puerta con `"u": "door"`.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from .geometry import ring_crossings, ring_spans_at_u

DEFAULT_ARM_PROBE_M = 2.0
# Cuánto más ancho que el brazo tiene que ser un corte para contar como
# lóbulo: por debajo es el ruido del trazo del KML en el pasillo.
LOBE_EXTRA_WIDTH_M = 1.0
LOBE_SCAN_STEP_M = 0.05


class ArmError(ValueError):
    pass


@dataclass
class Arm:
    side: str
    span: tuple[float, float]
    wall_v: float
    face_v: float
    lobe: tuple[float, float]
    door: tuple[float, float]

    @property
    def axis_u(self) -> float:
        return (self.span[0] + self.span[1]) / 2


def _span_containing(cuts: list[float], u: float):
    for a, b in zip(cuts[::2], cuts[1::2]):
        if a - 1e-6 <= u <= b + 1e-6:
            return a, b
    return None


def measure_arm(ring, band, side: str,
                probe: float = DEFAULT_ARM_PROBE_M) -> Arm:
    """Brazo y lóbulo de un lado de la franja de andenes."""
    sign = 1.0 if side == "+v" else -1.0
    edge = band[1] if side == "+v" else band[0]
    v_probe = edge + sign * probe
    cuts = ring_crossings(ring, v_probe)
    spans = list(zip(cuts[::2], cuts[1::2]))
    if len(spans) != 1:
        raise ArmError(
            f"a {probe:g} m de la franja por el lado {side} el área tiene "
            f"{len(spans)} brazos; la referencia `arm` pide exactamente uno")
    span = spans[0]
    axis = (span[0] + span[1]) / 2
    along = ring_spans_at_u(ring, axis)
    if side == "+v":
        wall_v = max(b for _, b in along)
    else:
        wall_v = min(a for a, _ in along)
    # El lóbulo empieza donde el corte a lo ancho deja de ser el brazo.
    arm_width = span[1] - span[0]
    v = v_probe
    face_v = None
    previous = span
    while (wall_v - v) * sign > LOBE_SCAN_STEP_M:
        v += sign * LOBE_SCAN_STEP_M
        current = _span_containing(ring_crossings(ring, v), axis)
        if current is None:
            break
        if current[1] - current[0] > arm_width + LOBE_EXTRA_WIDTH_M:
            face_v = v - sign * LOBE_SCAN_STEP_M / 2
            break
        previous = current
    if face_v is None:
        raise ArmError(
            f"el brazo del lado {side} (eje en u={axis:.2f}) llega al muro "
            f"del fondo sin abrirse en un lóbulo")
    # El ancho del lóbulo se lee a media profundidad: junto a la cara, un
    # muro del KML apenas inclinado da cortes de cualquier ancho.
    lobe = _span_containing(ring_crossings(ring, (face_v + wall_v) / 2),
                            axis)
    if lobe is None:
        raise ArmError(
            f"el lóbulo del lado {side} no contiene el eje de su brazo "
            f"(u={axis:.2f}) a media profundidad")
    pieces = [(lobe[0], previous[0]), (previous[1], lobe[1])]
    lo, hi = max(pieces, key=lambda p: p[1] - p[0])
    door_u = (lo + hi) / 2
    # La v de la puerta es la del muro en esa u, no la del barrido: el
    # nodo tiene que caer sobre el anillo para hacerse vértice suyo.
    walls = [a if side == "+v" else b
             for a, b in ring_spans_at_u(ring, door_u)]
    door_v = min(walls, key=lambda w: abs(w - face_v))
    return Arm(side, span, wall_v, face_v, lobe, (door_u, door_v))


def measure_arms(ring, band, probe: float = DEFAULT_ARM_PROBE_M) -> dict:
    return {side: measure_arm(ring, band, side, probe)
            for side in ("+v", "-v")}


def _resolve(ref: dict, arms: dict):
    side = ref["arm"]
    if side == "mid":
        if "at" in ref:
            raise ArmError("la referencia «mid» es una u, no lleva `at`")
        return (arms["+v"].axis_u + arms["-v"].axis_u) / 2 + float(
            ref.get("du", 0.0))
    if side not in arms:
        raise ArmError(f"referencia a un brazo desconocido: «{side}»")
    arm = arms[side]
    at = ref.get("at")
    if at is None:
        return arm.axis_u + float(ref.get("du", 0.0))
    if at == "door":
        return [arm.door[0], arm.door[1]]
    if at == "wall":
        toward_band = -1.0 if side == "+v" else 1.0
        u = arm.door[0] if ref.get("u") == "door" else arm.axis_u
        return [u, arm.wall_v + toward_band * float(ref.get("inset", 0.0))]
    raise ArmError(f"la referencia `arm` no conoce «at»: «{at}»")


def resolve_arm_refs(data: dict, arms: dict) -> tuple[dict, list[str]]:
    """Copia de la plantilla con las referencias `arm` resueltas.

    Devuelve también las claves de los nodos ubicados en una puerta
    (`locate` con `"at": "door"`), que el área tiene que tomar como
    vértices suyos.
    """
    doors = []

    def walk(value):
        if isinstance(value, dict):
            if "arm" in value:
                return _resolve(value, arms)
            return {k: walk(v) for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v) for v in value]
        return value

    out = copy.deepcopy(data)
    for key, spec in out.get("nodes", {}).items():
        locate = spec.pop("locate", None)
        if locate is None:
            continue
        if locate.get("at") == "door":
            doors.append(key)
        point = _resolve(locate, arms)
        if not isinstance(point, list):
            raise ArmError(
                f"el nodo {key} se ubica con una referencia que da una u, "
                f"no un punto; usa `at`")
        spec["u"], spec["v"] = point
    out = walk(out)
    return out, doors
