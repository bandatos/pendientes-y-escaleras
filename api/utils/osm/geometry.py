"""Marco local métrico (u, v) anclado a un centroide y un rumbo."""
from __future__ import annotations

import math


def meters_per_degree(lat_deg: float) -> tuple[float, float]:
    """Metros por grado de latitud y de longitud a esa latitud (WGS84)."""
    lat = math.radians(lat_deg)
    m_lat = (111132.92 - 559.82 * math.cos(2 * lat)
             + 1.175 * math.cos(4 * lat))
    m_lon = (111412.84 * math.cos(lat) - 93.5 * math.cos(3 * lat)
             + 0.118 * math.cos(5 * lat))
    return m_lat, m_lon


class LocalFrame:
    """u = metros sobre el eje del rumbo; v = metros a la derecha del eje.

    `mirror` invierte v: las familias son simétricas respecto de su eje,
    así que la estación espejo se genera con la misma plantilla.
    """

    def __init__(self, lat: float, lon: float, bearing_deg: float,
                 mirror: bool = False):
        self.lat = lat
        self.lon = lon
        self.bearing_deg = bearing_deg
        self.mirror = mirror
        self.m_lat, self.m_lon = meters_per_degree(lat)
        b = math.radians(bearing_deg)
        self._sin = math.sin(b)
        self._cos = math.cos(b)

    def to_wgs84(self, u: float, v: float) -> tuple[float, float]:
        if self.mirror:
            v = -v
        east = u * self._sin + v * self._cos
        north = u * self._cos - v * self._sin
        return (self.lat + north / self.m_lat,
                self.lon + east / self.m_lon)

    def to_local(self, lat: float, lon: float) -> tuple[float, float]:
        east = (lon - self.lon) * self.m_lon
        north = (lat - self.lat) * self.m_lat
        u = east * self._sin + north * self._cos
        v = east * self._cos - north * self._sin
        return (u, -v if self.mirror else v)


def point_segment_distance(p, a, b) -> tuple[float, float]:
    """Distancia de p al segmento ab y parámetro t del pie de la normal."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    den = dx * dx + dy * dy
    if den == 0:
        return math.hypot(px - ax, py - ay), 0.0
    t = ((px - ax) * dx + (py - ay) * dy) / den
    t = max(0.0, min(1.0, t))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy), t


def offset_midpoint(a, b, bow: float):
    """Punto medio de ab desplazado `bow` metros en perpendicular."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return (ax, ay)
    nx, ny = -dy / length, dx / length
    return (ax + dx / 2 + nx * bow, ay + dy / 2 + ny * bow)


def point_along(a, b, distance: float):
    """Punto sobre ab a `distance` metros de a."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return (ax, ay)
    f = max(0.0, min(1.0, distance / length))
    return (ax + dx * f, ay + dy * f)


def segment_intersection(p, q, r, s):
    """Punto donde se cruzan los segmentos pq y rs, o None."""
    px, py = p
    qx, qy = q
    rx, ry = r
    sx, sy = s
    d1x, d1y = qx - px, qy - py
    d2x, d2y = sx - rx, sy - ry
    den = d1x * d2y - d1y * d2x
    if abs(den) < 1e-12:
        return None
    t = ((rx - px) * d2y - (ry - py) * d2x) / den
    u = ((rx - px) * d1y - (ry - py) * d1x) / den
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None
    return (px + t * d1x, py + t * d1y)


# Lados de un cuadrado en el marco local, con su normal hacia afuera.
SIDE_NORMALS = {"+u": (1.0, 0.0), "-u": (-1.0, 0.0),
                "+v": (0.0, 1.0), "-v": (0.0, -1.0)}


def square_corners(cu: float, cv: float, half: float):
    """Vértices de un cuadrado centrado en (cu, cv), en sentido fijo."""
    return [(cu - half, cv - half), (cu + half, cv - half),
            (cu + half, cv + half), (cu - half, cv + half)]


def side_segment(cu: float, cv: float, half: float, side: str):
    """Extremos del lado `side` del cuadrado, de menor a mayor eje."""
    if side == "+u":
        return (cu + half, cv - half), (cu + half, cv + half)
    if side == "-u":
        return (cu - half, cv - half), (cu - half, cv + half)
    if side == "+v":
        return (cu - half, cv + half), (cu + half, cv + half)
    if side == "-v":
        return (cu - half, cv - half), (cu + half, cv - half)
    raise ValueError(f"lado desconocido: {side!r}; usa +u, -u, +v o -v")


def opposite_side(side: str) -> str:
    return side[0].replace("+", "@").replace("-", "+").replace("@", "-") \
        + side[1]


def facing_side(cu: float, cv: float, target) -> str:
    """Lado del cuadrado que mira hacia `target` (el de mayor proyección)."""
    du, dv = target[0] - cu, target[1] - cv
    best, best_dot = None, None
    for side, (nu, nv) in SIDE_NORMALS.items():
        dot = du * nu + dv * nv
        if best_dot is None or dot > best_dot:
            best, best_dot = side, dot
    return best


def point_along_polyline(points, distance: float):
    """Punto a `distance` metros del primer vértice, siguiendo la línea.

    Se mide sobre la polilínea y no sobre la cuerda porque un pathway
    con `bow` es un arco: sobre la cuerda el punto caería fuera del way.
    """
    if not points:
        raise ValueError("polilínea vacía")
    if distance <= 0:
        return points[0]
    remaining = distance
    for a, b in zip(points, points[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg >= remaining:
            return point_along(a, b, remaining)
        remaining -= seg
    return points[-1]
