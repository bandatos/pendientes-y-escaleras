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
  la de la puerta con `"u": "door"`;
- `"at": "foot"`, el nodo de encuentro del pie del banco de acceso de ese
  lado (ver abajo); con `"u": "door"`, el punto de esa v en la u de la
  puerta: la esquina de la circulación en U.

Un banco con `lobe` (`{"arm": "+v", "inset": 3}`)
es el banco de acceso del lóbulo, y su orientación la da el lado largo
del lóbulo. En un lóbulo hondo (más profundo en v que ancho en u) el
banco va sobre el eje del brazo, con el pie a `inset` metros del muro del
fondo, y sube hacia la franja. En un lóbulo ancho va a lo largo de u, en
el centro de la mitad del fondo del lóbulo, con un cuarto del fondo entre
ejes (`wide_spacing` lo fija a mano); sube hacia el brazo, con su nodo de encuentro de arriba
en el borde del brazo y el pie al menos a `inset` metros del muro de la
punta, y la puerta pasa al medio del tramo de la cara que queda entre ese
muro y el arranque de las escaleras. Resolver un banco así cambia el
brazo (puerta, pie): las referencias se resuelven después.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from .geometry import ring_crossings, ring_spans_at_u

DEFAULT_ARM_PROBE_M = 2.0
# Cuánto más ancho que el brazo tiene que ser un corte para contar como
# lóbulo: por debajo es el ruido del trazo del KML en el pasillo.
LOBE_EXTRA_WIDTH_M = 1.0
LOBE_SCAN_STEP_M = 0.05
# Por debajo, un banco de acceso acortado ya no es una escalera de un piso:
# el lóbulo no lo aloja y se avisa como error.
MIN_LOBE_BANK_M = 6.0


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
    ring: list = field(default=None, repr=False)
    # Lo pone el banco de acceso del lóbulo al resolverse: "deep" o "wide",
    # y el nodo de encuentro de su pie.
    orientation: str | None = None
    foot: tuple[float, float] | None = None
    notes: list = field(default_factory=list)

    @property
    def axis_u(self) -> float:
        return (self.span[0] + self.span[1]) / 2

    @property
    def width(self) -> float:
        return self.lobe[1] - self.lobe[0]

    @property
    def depth(self) -> float:
        return abs(self.wall_v - self.face_v)

    def face_point(self, u: float) -> tuple[float, float]:
        """El punto de la cara del lóbulo en esa u, sobre el anillo."""
        walls = [a if self.side == "+v" else b
                 for a, b in ring_spans_at_u(self.ring, u)]
        return (u, min(walls, key=lambda w: abs(w - self.face_v)))


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
    return Arm(side, span, wall_v, face_v, lobe, (door_u, door_v),
               ring=ring)


def measure_arms(ring, band, probe: float = DEFAULT_ARM_PROBE_M) -> dict:
    return {side: measure_arm(ring, band, side, probe)
            for side in ("+v", "-v")}


def _lobe_bank(key: str, bank: dict, arms: dict):
    """El banco de acceso de un lóbulo, orientado por su lado largo.

    Devuelve el banco con `junction`, `direction` y `spacing` escritos y
    sus dos nodos de encuentro, y deja en el brazo la orientación, el pie
    y, en un lóbulo ancho, la puerta nueva.
    """
    ref = bank.pop("lobe")
    side = ref.get("arm")
    if side not in ("+v", "-v"):
        raise ArmError(f"el banco {key} pide el lóbulo de un brazo "
                       f"desconocido: «{side}»")
    arm = arms[side]
    toward_band = -1.0 if side == "+v" else 1.0
    length = float(bank["length"])
    raw_lead = bank.get("lead", 1.5)
    lead_from, lead_to = ((float(raw_lead[0]), float(raw_lead[1]))
                          if isinstance(raw_lead, (list, tuple))
                          else (float(raw_lead), float(raw_lead)))
    if arm.depth >= arm.width:
        arm.orientation = "deep"
        foot = (arm.axis_u,
                arm.wall_v + toward_band * float(ref.get("inset", 3.0)))
        bank["direction"] = "-v" if side == "+v" else "+v"
        head = (foot[0], foot[1] + toward_band * (lead_from + length
                                                  + lead_to))
    else:
        # El banco ocupa la mitad del fondo del lóbulo, la que no recorre
        # quien entra por la cara, y sube hacia el brazo desde el lado
        # más largo del lóbulo; arriba lo espera el pasillo del puente en
        # el borde del brazo.
        arm.orientation = "wide"
        bank_v = arm.wall_v + toward_band * arm.depth / 4
        below = arm.span[0] - arm.lobe[0]
        above = arm.lobe[1] - arm.span[1]
        sign = 1.0 if below >= above else -1.0
        head_u = arm.span[0] if sign > 0 else arm.span[1]
        far_end = arm.lobe[0] if sign > 0 else arm.lobe[1]
        # El pie queda a `inset` metros del muro de la punta, como en el
        # lóbulo hondo queda del muro del fondo; si no cabe, se acorta la
        # escalera, como las del andén.
        inset = float(ref.get("inset", 3.0))
        room = (head_u - far_end) * sign - inset - lead_from - lead_to
        if room < length:
            if room < MIN_LOBE_BANK_M:
                raise ArmError(
                    f"el banco {key} no cabe a lo largo del lóbulo {side}: "
                    f"entre el brazo y el muro de la punta quedan "
                    f"{room:.1f} m de escalera")
            bank["length"] = length = room
            arm.notes.append(
                f"banco {key}: acortado a {room:.2f} m para dejar el pie "
                f"a {inset:g} m del muro de la punta del lóbulo {side}")
        foot_u = head_u - sign * (lead_to + length + lead_from)
        stair_start = foot_u + sign * lead_from
        foot = (foot_u, bank_v)
        head = (head_u, bank_v)
        bank["direction"] = "+u" if sign > 0 else "-u"
        # Una escalera al centro de cada cuarto del fondo: separación =
        # fondo / 4 (decisión de Ricardo, 2026-10-27). `wide_spacing` la
        # fija a mano si una estación lo pide.
        bank["spacing"] = float(ref.get("wide_spacing", arm.depth / 4))
        arm.door = arm.face_point((far_end + stair_start) / 2)
    bank["junction"] = [foot[0], foot[1]]
    arm.foot = foot
    return bank, foot, head


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
    if at == "foot":
        if arm.foot is None:
            raise ArmError(
                f"la referencia al pie del banco del lado {side} no tiene "
                f"banco: ningún banco declara `lobe` de ese brazo")
        u = arm.door[0] if ref.get("u") == "door" else arm.foot[0]
        return [u, arm.foot[1]]
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
    # Los bancos de lóbulo van primero: en un lóbulo ancho mueven la
    # puerta, y el pie es un punto que otras piezas nombran.
    nodes = out.setdefault("nodes", {})
    for key, bank in out.get("banks", {}).items():
        if not isinstance(bank, dict) or "lobe" not in bank:
            continue
        bank, foot, head = _lobe_bank(key, bank, arms)
        for end, point in ((bank["from"], foot), (bank["to"], head)):
            if end in nodes:
                nodes[end]["u"], nodes[end]["v"] = point
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
