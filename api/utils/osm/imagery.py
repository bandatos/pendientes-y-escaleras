"""Imagen satelital Esri World Imagery bajo el trazo de una estación.

Esri declara 8.47 m de precisión absoluta para la toma de la CDMX: el
compuesto sirve para leer qué hay en el terreno (edificios, explanadas,
accesos), nunca para mover coordenadas.
"""
from __future__ import annotations

import json
import math
import re
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw, ImageFont

SERVICE = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
           "World_Imagery/MapServer")
TILE = 256
EARTH_M = 2 * math.pi * 6378137
# Más allá de su zoom real el servicio no da 404: devuelve un mosaico
# gris «sin datos» con este ETag.
PLACEHOLDER_ETAG = "vvvvvvvvvvvvf"
# La licencia de World Imagery no admite exportar tiles para uso offline:
# la caché vive en el temporal de la máquina, nunca en el repo.
TILE_CACHE = Path(tempfile.gettempdir()) / "esri-tiles"
FRAME_RE = re.compile(r"frame anchor=([-\d.]+),([-\d.]+) "
                      r"bearing=([-\d.]+) mirror=(\w+)")
LEVEL_COLORS = {-4: (190, 0, 255), -3: (0, 110, 255), -2: (0, 220, 230),
                -1: (60, 230, 60), 0: (255, 40, 40)}
KML = (255, 230, 0)
PAVILION = (255, 150, 0)
PLAZA = (255, 0, 255)
BUILDING = (230, 230, 230)
# Blanco con halo negro: el amarillo del KML y los colores de nivel ya
# ocupan los tonos saturados, y nuestros accesos son puntos rojos llenos.
ENTRANCE = (255, 255, 255)
HALO = (0, 0, 0)
# La fuente por omisión de Pillow no trae acentos.
FONT_PATH = ("/usr/share/fonts/liberation-sans-fonts/"
             "LiberationSans-Regular.ttf")


def world_px(lat, lon, z):
    n = TILE * 2 ** z
    s = math.sin(math.radians(lat))
    return ((lon + 180) / 360 * n,
            (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n)


def world_latlon(x, y, z):
    n = TILE * 2 ** z
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, x / n * 360 - 180


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.headers.get("ETag", ""), resp.read()


def fetch_tile(cache: Path, z, x, y):
    path = cache / str(z) / f"{x}_{y}.jpg"
    empty = path.with_suffix(".empty")
    if path.exists() or empty.exists():
        return path if path.exists() else None
    etag, data = _get(f"{SERVICE}/tile/{z}/{y}/{x}")
    if PLACEHOLDER_ETAG in etag:
        empty.touch()
        return None
    path.write_bytes(data)
    return path


def mosaic(z, south, west, north, east, cache: Path = TILE_CACHE):
    """Mosaico de los tiles que cubren la caja; origen en px de mundo."""
    (cache / str(z)).mkdir(parents=True, exist_ok=True)
    x0, y1 = world_px(south, west, z)
    x1, y0 = world_px(north, east, z)
    tx0, tx1, ty0, ty1 = (int(x0 // TILE), int(x1 // TILE),
                          int(y0 // TILE), int(y1 // TILE))
    size = ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE)
    img = Image.new("RGB", size, (40, 40, 40))
    missing = 0
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            path = fetch_tile(cache, z, tx, ty)
            if path is None:
                missing += 1
                continue
            img.paste(Image.open(path), ((tx - tx0) * TILE,
                                         (ty - ty0) * TILE))
    return img, (tx0 * TILE, ty0 * TILE), missing


def capture_metadata(lat, lon, z):
    """Fecha, sensor y precisión de la toma bajo el punto, a ese zoom."""
    d = 0.003
    query = urllib.parse.urlencode({
        "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
        "sr": 4326, "layers": "all", "tolerance": 1,
        "mapExtent": f"{lon - d},{lat - d},{lon + d},{lat + d}",
        "imageDisplay": "400,400,96", "returnGeometry": "false",
        "f": "json"})
    meta = {"source": "Esri World Imagery", "service": SERVICE, "zoom": z,
            "copyright": json.loads(_get(f"{SERVICE}?f=json")[1])
            ["copyrightText"]}
    for res in json.loads(_get(f"{SERVICE}/identify?{query}")[1])[
            "results"]:
        a = res["attributes"]
        if ("SRC_ACC" in a and a["SRC_DATE"] != "Null"
                and int(a["MinMapLevel"]) <= z <= int(a["MaxMapLevel"])):
            day = a["SRC_DATE"]
            meta.update(capture_date=f"{day[:4]}-{day[4:6]}-{day[6:]}",
                        sensor=a["SRC_DESC"], provider=a["NICE_DESC"],
                        product=a["NICE_NAME"],
                        resolution_m=float(a["SRC_RES"]),
                        accuracy_m=float(a["SRC_ACC"]))
            break
    return meta


def osm_frame(path: Path):
    """(lat, lon, rumbo, mirror) del comentario que deja el generador."""
    m = FRAME_RE.search(path.read_text(encoding="utf-8")[:4000])
    if not m:
        return None
    return float(m[1]), float(m[2]), float(m[3]), m[4] == "true"


def load_osm(path: Path):
    """Nodos y ways propios (id negativo o modificados) de un .osm, y
    las áreas de estación.

    Los anillos del multipolígono del área no llevan etiquetas; entran
    en `ways` como cualquier way propio y además se arman en `areas`,
    una lista de {"outer": [anillos], "inner": [anillos]} en (lat, lon).
    Un área sin islas es un way propio etiquetado, sin relación, y entra
    en `areas` con su anillo como único outer.
    """
    root = ElementTree.parse(path).getroot()
    nodes = {}
    for n in root.iter("node"):
        tags = {t.get("k"): t.get("v") for t in n.iter("tag")}
        nodes[n.get("id")] = (float(n.get("lat")), float(n.get("lon")),
                              tags, _ours(n))
    ways = []
    every = {}
    for w in root.iter("way"):
        coords = [nodes[x.get("ref")][:2] for x in w.iter("nd")
                  if x.get("ref") in nodes]
        every[w.get("id")] = coords
        if _ours(w):
            ways.append((coords, {t.get("k"): t.get("v")
                                  for t in w.iter("tag")}))
    areas = [{"outer": [coords], "inner": []} for coords, tags in ways
             if tags.get("public_transport") == "station"
             and len(coords) > 3 and coords[0] == coords[-1]]
    for r in root.iter("relation"):
        tags = {t.get("k"): t.get("v") for t in r.iter("tag")}
        if (r.get("action") == "delete" or tags.get("type") != "multipolygon"
                or tags.get("public_transport") != "station"):
            continue
        parts = {"outer": [], "inner": []}
        for m in r.iter("member"):
            if m.get("type") == "way" and m.get("ref") in every:
                role = m.get("role") or "outer"
                parts.setdefault(role, []).append(every[m.get("ref")])
        areas.append({role: _join_rings(lines)
                      for role, lines in parts.items()})
    return [v for v in nodes.values() if v[3]], ways, areas


def _join_rings(lines):
    """Anillos cerrados a partir de ways que JOSM pudo haber partido."""
    pending = [list(line) for line in lines if len(line) >= 2]
    rings = []
    while pending:
        ring = pending.pop(0)
        while ring[0] != ring[-1]:
            for i, line in enumerate(pending):
                if line[0] == ring[-1]:
                    ring += line[1:]
                elif line[-1] == ring[-1]:
                    ring += line[-2::-1]
                else:
                    continue
                del pending[i]
                break
            else:
                break
        rings.append(ring)
    return rings


def _ours(el):
    action = el.get("action")
    return action != "delete" and (el.get("id").startswith("-")
                                   or action == "modify")


def load_context(path: Path):
    elements = json.loads(path.read_text(encoding="utf-8"))["elements"]
    nodes = {e["id"]: e for e in elements if e["type"] == "node"}
    ways = {e["id"]: e for e in elements if e["type"] == "way"}
    rels = [e for e in elements if e["type"] == "relation"]

    def coords(way):
        return [(nodes[n]["lat"], nodes[n]["lon"]) for n in way["nodes"]
                if n in nodes]
    return nodes, ways, rels, coords


class Composite:
    """Dibuja capas sobre una ventana del mosaico, en px del mosaico."""

    def __init__(self, base, origin, z, frame, ring, context, ours):
        self.base, self.origin, self.z = base, origin, z
        self.frame, self.ring = frame, ring
        self.context, self.ours = context, ours
        try:
            self.font = ImageFont.truetype(FONT_PATH, 13)
        except OSError:
            self.font = ImageFont.load_default(size=13)
        self.m_per_px = (EARTH_M * math.cos(math.radians(frame.lat))
                         / (TILE * 2 ** z))

    def local_window(self, u0, u1, v0, v1):
        corners = [world_px(*self.frame.to_wgs84(u, v), self.z)
                   for u in (u0, u1) for v in (v0, v1)]
        xs = [c[0] - self.origin[0] for c in corners]
        ys = [c[1] - self.origin[1] for c in corners]
        return (max(0, int(min(xs))), max(0, int(min(ys))),
                min(self.base.width, int(max(xs)) + 1),
                min(self.base.height, int(max(ys)) + 1))

    def render(self, window=None, scale=1, title="", footer=""):
        x0, y0, x1, y1 = window or (0, 0, *self.base.size)
        size = ((x1 - x0) * scale, (y1 - y0) * scale)
        img = self.base.crop((x0, y0, x1, y1)).resize(
            size, Image.LANCZOS).convert("RGBA")
        ov = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        def P(lat, lon):
            x, y = world_px(lat, lon, self.z)
            return ((x - self.origin[0] - x0) * scale,
                    (y - self.origin[1] - y0) * scale)
        # El relleno del área va primero: pegarlo después borraría la
        # rejilla y el contexto que caen dentro.
        self._area_fill(ov, P)
        self._grid(d, P, 10 if scale > 1 else 20)
        legend = self._context(d, P)
        legend.insert(0, self._area_outline(d, P))
        legend += self._ours(d, P)
        self._legend(d, legend, title)
        self._scale_bar(d, scale, size, footer)
        out = Image.alpha_composite(img, ov).convert("RGB")
        return out, (self.origin[0] + x0, self.origin[1] + y0)

    def _grid(self, d, P, every):
        local = [self.frame.to_local(*p) for p in self.ring]
        us = [p[0] for p in local]
        vs = [p[1] for p in local]
        u0, u1 = int(min(us) // 10 * 10) - 20, int(max(us) // 10 * 10) + 30
        v0, v1 = int(min(vs) // 10 * 10) - 20, int(max(vs) // 10 * 10) + 30
        fr, grey = self.frame.to_wgs84, (255, 255, 255, 60)
        for u in range(u0, u1 + 1, 10):
            d.line([P(*fr(u, v0)), P(*fr(u, v1))], fill=grey)
            if u % every == 0:
                d.text(P(*fr(u, v0 + 2)), f"u{u}", font=self.font)
        for v in range(v0, v1 + 1, 10):
            d.line([P(*fr(u0, v)), P(*fr(u1, v))], fill=grey)
            if v % every == 0:
                d.text(P(*fr(u0 + 2, v)), f"v{v}", font=self.font)

    def _areas(self):
        return self.ours[2] if self.ours else []

    def _area_fill(self, ov, P):
        """Velo sobre el área del trazo, con sus islas como huecos."""
        areas = self._areas()
        if not areas:
            return
        mask = Image.new("L", ov.size, 0)
        m = ImageDraw.Draw(mask)
        for area in areas:
            for ring in area.get("outer", []):
                m.polygon([P(*p) for p in ring], fill=50)
            for ring in area.get("inner", []):
                m.polygon([P(*p) for p in ring], fill=0)
        ov.paste(Image.new("RGBA", ov.size, KML + (255,)), mask=mask)

    def _area_outline(self, d, P):
        """Anillos del área del trazo; si el trazo no trae área, el del KML."""
        areas = self._areas()
        if not areas:
            ring = [P(*p) for p in self.ring]
            d.line(ring + ring[:1], fill=KML, width=3)
            return ("área KML", KML)
        for area in areas:
            for ring in area.get("outer", []) + area.get("inner", []):
                d.line([P(*p) for p in ring], fill=KML, width=3)
        return ("área del trazo (islas en hueco)", KML)

    def _context(self, d, P):
        if not self.context:
            return []
        nodes, ways, rels, coords = self.context
        for wid, way in ways.items():
            tags, pts = way.get("tags", {}), [P(*c) for c in coords(way)]
            if len(pts) < 2:
                continue
            if tags.get("building") == "transportation":
                d.line(pts, fill=PAVILION, width=2)
                d.text(pts[0], str(wid), fill=PAVILION, font=self.font)
            elif "building" in tags:
                d.line(pts, fill=BUILDING + (180,), width=2)
            elif tags.get("highway") in ("pedestrian", "footway"):
                d.line(pts, fill=(255, 255, 255, 140), width=1)
        for rel in rels:
            pts = []
            for m in rel.get("members", []):
                if m["type"] == "way" and m["ref"] in ways:
                    pts = [P(*c) for c in coords(ways[m["ref"]])]
                    d.line(pts, fill=PLAZA, width=2)
            if pts:
                d.text(pts[0], f"rel {rel['id']}", fill=PLAZA,
                       font=self.font)
        for nid, n in nodes.items():
            if n.get("tags", {}).get("railway") == "subway_entrance":
                x, y = P(n["lat"], n["lon"])
                d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=HALO,
                          width=4)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=ENTRANCE,
                          width=2)
                d.text((x + 7, y - 7), str(nid), fill=ENTRANCE,
                       font=self.font, stroke_width=2, stroke_fill=HALO)
        return [("pabellón OSM", PAVILION), ("explanada OSM (rel)", PLAZA),
                ("edificio OSM", BUILDING), ("acceso OSM", ENTRANCE, "ring")]

    def _ours(self, d, P):
        if not self.ours:
            return []
        nodes, ways, _ = self.ours
        levels = set()
        for coords, tags in ways:
            if "level" not in tags or tags.get("railway") == "subway":
                continue
            top = max(int(float(x)) for x in tags["level"].split(";"))
            levels.add(top)
            col = LEVEL_COLORS.get(top, (255, 255, 255))
            pts = [P(*c) for c in coords]
            if tags.get("railway") == "platform":
                d.polygon(pts, outline=col + (200,))
                continue
            steps = tags.get("highway") == "steps"
            d.line(pts, fill=col, width=4 if steps else 2)
            if steps and len(pts) >= 2:
                (ax, ay), (bx, by) = pts[-2], pts[-1]
                length = math.hypot(bx - ax, by - ay) or 1
                ux, uy = (bx - ax) / length * 7, (by - ay) / length * 7
                cx, cy = bx - ux, by - uy
                d.polygon([(bx, by), (cx + uy / 2, cy - ux / 2),
                           (cx - uy / 2, cy + ux / 2)], fill=col)
        for lat, lon, tags, _ in nodes:
            x, y = P(lat, lon)
            if tags.get("railway") == "subway_entrance":
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=LEVEL_COLORS[0])
            elif tags.get("barrier") == "turnstile":
                d.rectangle([x - 3, y - 3, x + 3, y + 3], fill="black",
                            outline="white")
        return [(f"trazo nivel {lv}", LEVEL_COLORS.get(lv, (255,) * 3))
                for lv in sorted(levels)]

    def _legend(self, d, items, title):
        d.rectangle([4, 4, 200, 30 + 16 * len(items)], fill=(0, 0, 0, 160))
        y = 8
        for label, col, *shape in items:
            if shape == ["ring"]:
                d.ellipse([14, y + 2, 26, y + 14], outline=HALO, width=4)
                d.ellipse([15, y + 3, 25, y + 13], outline=col, width=2)
            else:
                d.line([(10, y + 8), (30, y + 8)], fill=col, width=3)
            d.text((36, y), label, font=self.font)
            y += 16
        d.text((10, y + 4), title, font=self.font)

    def _scale_bar(self, d, scale, size, footer):
        px_per_m = scale / self.m_per_px
        meters = max(m for m in (5, 10, 20, 50, 100)
                     if m * px_per_m <= size[0] / 4)
        x, y = 12, size[1] - 40
        d.rectangle([x - 6, y - 8, x + meters * px_per_m + 50, y + 10],
                    fill=(0, 0, 0, 160))
        d.line([(x, y), (x + meters * px_per_m, y)], fill="white", width=4)
        d.text((x + meters * px_per_m + 6, y - 7), f"{meters} m",
               font=self.font)
        w = d.textlength(footer, font=self.font)
        d.rectangle([size[0] - w - 12, size[1] - 22, size[0], size[1]],
                    fill=(0, 0, 0, 160))
        d.text((size[0] - w - 6, size[1] - 18), footer, font=self.font)


def georef(top_left, z, scale, size):
    """Esquinas WGS84 de un PNG del compuesto (Web Mercator, lineal)."""
    nw = world_latlon(*top_left, z)
    se = world_latlon(top_left[0] + size[0] / scale,
                      top_left[1] + size[1] / scale, z)
    return {"size_px": list(size), "zoom": z, "upscale": scale,
            "projection": "EPSG:3857", "north": nw[0], "west": nw[1],
            "south": se[0], "east": se[1]}
