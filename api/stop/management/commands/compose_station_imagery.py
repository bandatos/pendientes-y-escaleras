"""Management command: compuestos satelitales de una estación para leerla.

No toca la base: el nombre sale del GTFS, el área del KML y el marco
local del comentario de cabecera de algún .osm generado de la estación.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from stop.management.commands.export_station_osm import (
    KML_PATH, OSM_DIR, REPO_ROOT, slugify)
from utils.osm import imagery
from utils.osm.geometry import LocalFrame, meters_per_degree
from utils.osm.kml import KmlError, station_polygon
from utils.osm.layout import latest_version_path

ORIENTATION_CSV = REPO_ROOT / "data/analysis/kml-estaciones-orientacion.csv"
COMPASS = ["norte", "oriente", "sur", "poniente"]
END_MARGIN_M = 30


class Command(BaseCommand):
    help = ("Baja Esri World Imagery alrededor de una estación y escribe "
            "overview.png y un recorte por extremo, con el área del KML, "
            "el contexto de OSM y nuestro trazo encima. La "
            "imagen tiene 8.47 m de exactitud absoluta declarada: sirve "
            "para leer edificios, explanadas y accesos, nunca para "
            "corregir coordenadas. Los tiles se guardan en caché en el "
            "temporal del sistema, nunca en el repo.")

    def add_arguments(self, parser):
        parser.add_argument("stop_id")
        parser.add_argument(
            "--osm", help="Trazo propio a dibujar encima. Por omisión, la "
                          "versión de NN más alto en la carpeta de la "
                          "estación; --osm la sustituye.")
        parser.add_argument("--zoom", type=int, default=19,
                            help="19 es el máximo real en la CDMX.")
        parser.add_argument("--radius-m", type=float, default=150.0)
        parser.add_argument("--ends", choices=("v", "u"), default="v",
                            help="Eje de los recortes por extremo: v "
                                 "(lados de las vías, por omisión) o u.")
        parser.add_argument("--out-dir")

    def handle(self, *args, **opts):
        name, row = self._station(opts["stop_id"])
        slug = slugify(name)
        dirs = [p for p in OSM_DIR.iterdir()
                if p.is_dir() and p.name.split("-", 1)[-1] == slug]
        station_dir = dirs[0] if dirs else None
        try:
            ring = station_polygon(KML_PATH, name)
        except KmlError as exc:
            raise CommandError(str(exc))
        osm_path = (Path(opts["osm"]) if opts["osm"]
                    else latest_version_path(station_dir, slug))
        frame, frame_src = self._frame(osm_path, station_dir, slug, row)
        out = Path(opts["out_dir"]) if opts["out_dir"] else (
            station_dir / "sat" if station_dir else OSM_DIR / "sat" / slug)
        out.mkdir(parents=True, exist_ok=True)

        context_path = station_dir and station_dir / "context.json"
        if not (context_path and context_path.exists()):
            context_path = None
        context = imagery.load_context(context_path) if context_path else None
        ours = imagery.load_osm(osm_path) if osm_path else None

        z, r = opts["zoom"], opts["radius_m"]
        m_lat, m_lon = meters_per_degree(frame.lat)
        lats, lons = [p[0] for p in ring], [p[1] for p in ring]
        base, origin, missing = imagery.mosaic(
            z, min(lats) - r / m_lat, min(lons) - r / m_lon,
            max(lats) + r / m_lat, max(lons) + r / m_lon)
        meta = imagery.capture_metadata(frame.lat, frame.lon, z)
        meta.update(stop_id=opts["stop_id"], station=name,
                    frame=dict(lat=frame.lat, lon=frame.lon,
                               bearing=frame.bearing_deg,
                               mirror=frame.mirror, source=frame_src),
                    osm=str(osm_path) if osm_path else None,
                    context=str(context_path) if context_path else None,
                    missing_tiles=missing)
        footer = (f"{meta['copyright']} · toma "
                  f"{meta.get('capture_date', '?')} · ±"
                  f"{meta.get('accuracy_m', '?')} m: leer, no medir")

        comp = imagery.Composite(base, origin, z, frame, ring, context, ours)
        shots = [("overview", None, 1, name)]
        local = [frame.to_local(*p) for p in ring]
        axis = 1 if opts["ends"] == "v" else 0
        for sign in (1, -1):
            # El extremo es la mitad lejana del área sobre ese eje: en
            # las estaciones con salidas laterales, el ramal y su pabellón.
            far = max(sign * p[axis] for p in local)
            near = [p for p in local if sign * p[axis] >= far / 2]
            lo = [min(p[i] for p in near) - END_MARGIN_M for i in (0, 1)]
            hi = [max(p[i] for p in near) + END_MARGIN_M for i in (0, 1)]
            if axis:
                turn = sign * (-90 if frame.mirror else 90)
            else:
                turn = 0 if sign > 0 else 180
            end = COMPASS[round((frame.bearing_deg + turn) / 90) % 4]
            window = comp.local_window(lo[0], hi[0], lo[1], hi[1])
            shots.append((end, window, 3, f"{name} {end}"))

        bounds = {}
        for key, window, scale, title in shots:
            img, top_left = comp.render(window, scale, title, footer)
            img.save(out / f"{key}.png")
            bounds[f"{key}.png"] = imagery.georef(top_left, z, scale,
                                                  img.size)
            self.stdout.write(f"escrito {out / key}.png {img.size[0]}x"
                              f"{img.size[1]}")
        (out / "bounds.json").write_text(json.dumps(bounds, indent=2))
        (out / "metadata.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False))
        self.stdout.write(f"marco: {frame_src}; contexto: {context_path}")
        self.stdout.write(f"imagen: {meta['source']}, toma "
                          f"{meta.get('capture_date')}, "
                          f"{meta.get('sensor')} "
                          f"{meta.get('resolution_m')} m, exactitud "
                          f"{meta.get('accuracy_m')} m — "
                          f"{meta['copyright']}")
        if missing:
            self.stdout.write(self.style.WARNING(
                f"aviso: {missing} tiles sin datos a zoom {z}"))

    def _station(self, stop_id):
        with open(REPO_ROOT / "data/gtfs/stops.txt", encoding="utf-8") as f:
            name = next((r["stop_name"] for r in csv.DictReader(f)
                         if r["stop_id"] == stop_id), None)
        if name is None:
            raise CommandError(f"no hay stop_id «{stop_id}» en el GTFS")
        with open(ORIENTATION_CSV, encoding="utf-8") as f:
            row = next((r for r in csv.DictReader(f)
                        if r["gtfs_stop_id"] == stop_id), None)
        return name, row

    def _frame(self, osm_path, station_dir, slug, row):
        # JOSM borra el comentario del marco al guardar: se busca en el
        # resto de versiones de la estación, de la más nueva a la vieja.
        candidates = [osm_path] if osm_path else []
        if station_dir:
            candidates += sorted(station_dir.glob("*.osm"), reverse=True)
        candidates.append(OSM_DIR / f"{slug}.osm")
        for path in candidates:
            if path.exists() and (found := imagery.osm_frame(path)):
                return LocalFrame(*found), str(path)
        if row is None:
            raise CommandError("sin marco: ni .osm generado ni fila en "
                               f"{ORIENTATION_CSV.name}")
        bearing = (row["line_bearing_shape_proj_deg"]
                   or row["bearing_pca_area_deg"])
        frame = LocalFrame(float(row["centroid_lat"]),
                           float(row["centroid_lon"]), float(bearing))
        return frame, f"{ORIENTATION_CSV.name} (centroide, rumbo {bearing})"
