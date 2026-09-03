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


def unit(a, b) -> tuple[float, float]:
    """Vector unitario de a hacia b; (1, 0) si coinciden."""
    du, dv = b[0] - a[0], b[1] - a[1]
    length = math.hypot(du, dv)
    if length == 0:
        return (1.0, 0.0)
    return (du / length, dv / length)


def right_of(direction) -> tuple[float, float]:
    """Normal a la derecha de `direction` en el marco local (u, v).

    Con u hacia el rumbo y v a la derecha del eje, quien camina en la
    dirección (du, dv) tiene a su derecha (-dv, du).
    """
    return (-direction[1], direction[0])


def polygon_signed_area(ring) -> float:
    total = 0.0
    for (au, av), (bu, bv) in zip(ring, list(ring[1:]) + [ring[0]]):
        total += au * bv - bu * av
    return total / 2.0


def polygon_centroid(ring) -> tuple[float, float]:
    area = polygon_signed_area(ring)
    if abs(area) < 1e-9:
        return (sum(p[0] for p in ring) / len(ring),
                sum(p[1] for p in ring) / len(ring))
    cu = cv = 0.0
    for (au, av), (bu, bv) in zip(ring, list(ring[1:]) + [ring[0]]):
        cross = au * bv - bu * av
        cu += (au + bu) * cross
        cv += (av + bv) * cross
    return (cu / (6 * area), cv / (6 * area))


def point_in_polygon(ring, p) -> bool:
    """Lanzamiento de rayo; el borde queda indefinido a propósito.

    Quien necesita tolerancia usa `point_in_polygon_tol`, que además
    admite el punto que cae justo sobre el anillo.
    """
    pu, pv = p
    inside = False
    n = len(ring)
    for i in range(n):
        au, av = ring[i]
        bu, bv = ring[(i + 1) % n]
        if (av > pv) != (bv > pv):
            cut = au + (pv - av) / (bv - av) * (bu - au)
            if cut > pu:
                inside = not inside
    return inside


def distance_to_ring(ring, p) -> float:
    best = None
    n = len(ring)
    for i in range(n):
        d, _ = point_segment_distance(p, ring[i], ring[(i + 1) % n])
        if best is None or d < best:
            best = d
    return best if best is not None else 0.0


def point_in_polygon_tol(ring, p, tol: float) -> tuple[bool, float]:
    """(¿dentro?, cuánto se sale). Dentro incluye el borde ± `tol`."""
    if point_in_polygon(ring, p):
        return True, 0.0
    out = distance_to_ring(ring, p)
    return (out <= tol), out


def ring_crossings(ring, v_line: float) -> list[float]:
    """Valores de u donde el anillo cruza la recta v = v_line.

    Los polígonos del KML son figuras ramificadas (andén más pasillos y
    salidas), así que una recta puede cortarlos más de dos veces; quien
    llama decide con cuáles se queda.
    """
    out = []
    n = len(ring)
    for i in range(n):
        au, av = ring[i]
        bu, bv = ring[(i + 1) % n]
        if (av > v_line) == (bv > v_line):
            continue
        t = (v_line - av) / (bv - av)
        out.append(au + t * (bu - au))
    return sorted(out)


def ring_spans_at_u(ring, u_line: float):
    """Intervalos de v que caen dentro del anillo en la recta u = u_line."""
    vs = []
    n = len(ring)
    for i in range(n):
        au, av = ring[i]
        bu, bv = ring[(i + 1) % n]
        if (au > u_line) == (bu > u_line):
            continue
        t = (u_line - au) / (bu - au)
        vs.append(av + t * (bv - av))
    vs.sort()
    return [(vs[i], vs[i + 1]) for i in range(0, len(vs) - 1, 2)]


def band_edges(ring, core=(0.1, 0.9), samples: int = 121):
    """Los dos bordes largos de la franja de andenes del polígono.

    El KML es una figura ramificada: la franja es lo único que está
    presente en toda la longitud de la estación, así que se identifica
    intersecando los cortes transversales y después se toma la mediana de
    sus bordes —no la intersección— para que los ramales, que ensanchan
    el corte donde arrancan, no la angosten. Se muestrea el 10–90 % del
    largo para no entrar en el afilado de las puntas.
    """
    us = [p[0] for p in ring]
    span = max(us) - min(us)
    if span <= 0:
        return None
    first = min(us) + span * core[0]
    last = min(us) + span * core[1]
    cuts = []
    for k in range(samples):
        u = first + (last - first) * k / (samples - 1)
        spans = ring_spans_at_u(ring, u)
        if spans:
            cuts.append(spans)
    if not cuts:
        return None
    common = list(cuts[0])
    for spans in cuts[1:]:
        merged = []
        for lo1, hi1 in common:
            for lo2, hi2 in spans:
                lo, hi = max(lo1, lo2), min(hi1, hi2)
                if hi > lo:
                    merged.append((lo, hi))
        common = merged
        if not common:
            return None
    seed_lo, seed_hi = max(common, key=lambda s: s[1] - s[0])
    seed = (seed_lo + seed_hi) / 2
    los, his = [], []
    for spans in cuts:
        for lo, hi in spans:
            if lo <= seed <= hi:
                los.append(lo)
                his.append(hi)
                break
    if not los:
        return None
    return (_median(los), _median(his))


def _median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def closest_point_on_ring(ring, p):
    """(distancia, índice de segmento, t, punto) más cercano del anillo."""
    best = None
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        d, t = point_segment_distance(p, a, b)
        if best is None or d < best[0]:
            point = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            best = (d, i, t, point)
    return best


def insert_points_into_ring(ring, items):
    """Anillo con los puntos dados metidos como vértices, en orden.

    `items` son tríos (índice de segmento, t, punto) tal como los
    devuelve `closest_point_on_ring`. Un punto que cae sobre un vértice
    que ya existe no se duplica.
    """
    by_segment: dict[int, list] = {}
    for index, t, point in items:
        by_segment.setdefault(index, []).append((t, point))
    out = []
    for i, vertex in enumerate(ring):
        out.append(vertex)
        for t, point in sorted(by_segment.get(i, []), key=lambda x: x[0]):
            if t <= 1e-6 or t >= 1 - 1e-6:
                continue
            out.append(point)
    return out


def overlap_ratio(a, b, step: float = 2.0) -> float:
    """IoU aproximada de dos polígonos, por muestreo en rejilla.

    Los contornos de estación tienen veintitantos vértices y son cóncavos,
    así que recortar uno contra otro exige un algoritmo general; para
    elegir cuál de dos contornos se parece más al polígono del KML basta
    con contar puntos de una rejilla métrica.
    """
    us = [p[0] for p in a] + [p[0] for p in b]
    vs = [p[1] for p in a] + [p[1] for p in b]
    inter = union = 0
    u = min(us)
    while u <= max(us):
        v = min(vs)
        while v <= max(vs):
            in_a = point_in_polygon(a, (u, v))
            in_b = point_in_polygon(b, (u, v))
            if in_a and in_b:
                inter += 1
            if in_a or in_b:
                union += 1
            v += step
        u += step
    return inter / union if union else 0.0


def simplify_ring(ring, tol: float = 0.5):
    """Quita vértices casi colineales, del menos desviado al más.

    Un edificio de OSM mapeado con vértices de más sigue siendo un
    cuadrilátero; sin esta poda no habría cuatro lados donde poner las
    puertas.
    """
    out = []
    for point in ring:
        if not out or math.hypot(point[0] - out[-1][0],
                                 point[1] - out[-1][1]) > 1e-6:
            out.append(point)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0],
                                   out[0][1] - out[-1][1]) <= 1e-6:
        out.pop()
    while len(out) > 3:
        worst = None
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            d, _ = point_segment_distance(b, a, c)
            if worst is None or d < worst[0]:
                worst = (d, i)
        if worst is None or worst[0] > tol:
            break
        del out[worst[1]]
    return out


def ring_ccw(ring):
    return list(ring) if polygon_signed_area(ring) > 0 else list(
        reversed(ring))


def ring_sides(ring):
    """(anillo en sentido antihorario, lados con normal exterior y medio)."""
    ccw = ring_ccw(ring)
    sides = []
    n = len(ccw)
    for i in range(n):
        a, b = ccw[i], ccw[(i + 1) % n]
        du, dv = b[0] - a[0], b[1] - a[1]
        length = math.hypot(du, dv) or 1.0
        sides.append({
            "a": a, "b": b,
            "normal": (dv / length, -du / length),
            "mid": ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
            "length": length,
        })
    return ccw, sides


def side_index_facing(sides, centre, target) -> int:
    """Lado cuya normal exterior apunta más hacia `target`."""
    du, dv = target[0] - centre[0], target[1] - centre[1]
    length = math.hypot(du, dv) or 1.0
    du, dv = du / length, dv / length
    best, best_dot = 0, None
    for i, side in enumerate(sides):
        dot = side["normal"][0] * du + side["normal"][1] * dv
        if best_dot is None or dot > best_dot:
            best, best_dot = i, dot
    return best


def side_index_for_name(sides, name: str) -> int:
    """Lado más parecido a un `+u`/`-u`/`+v`/`-v` de la plantilla."""
    try:
        want = SIDE_NORMALS[name]
    except KeyError:
        raise ValueError(
            f"lado desconocido: {name!r}; usa +u, -u, +v o -v")
    best, best_dot = 0, None
    for i, side in enumerate(sides):
        dot = side["normal"][0] * want[0] + side["normal"][1] * want[1]
        if best_dot is None or dot > best_dot:
            best, best_dot = i, dot
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
