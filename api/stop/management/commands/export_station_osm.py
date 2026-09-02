"""Management command: genera el .osm de una estación para editar en JOSM.

El grafo de la estación vive en la base; la geometría no. La plantilla
de familia arquitectónica aporta las coordenadas locales (u, v) y el
comando las proyecta a WGS84 con un ancla y un rumbo. Todas las
estaciones hermanas de una familia comparten plantilla: solo cambian
ancla, rumbo y, si la estación es la imagen espejo, --mirror.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from stop.models import Stop
from utils.osm import preview as preview_mod
from utils.osm.builder import StationBuilder
from utils.osm.geometry import LocalFrame
from utils.osm.graph import load_station_graph
from utils.osm.tags import UnsupportedModeError
from utils.osm.template import FamilyTemplate, TemplateError
from utils.osm.validate import validate

REPO_ROOT = Path(settings.BASE_DIR).resolve().parent
OSM_DIR = REPO_ROOT / "data" / "osm"


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    out = [c.lower() if c.isalnum() else "-" for c in text]
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


class Command(BaseCommand):
    help = "Exporta una estación a .osm a partir del grafo y una plantilla."

    def add_arguments(self, parser):
        parser.add_argument("stop_id")
        parser.add_argument("--family", required=True)
        parser.add_argument("--bearing", type=float, required=True,
                            help="Rumbo del eje del andén en grados.")
        parser.add_argument("--anchor", required=True,
                            help="LAT,LON del origen del marco local.")
        parser.add_argument("--out")
        parser.add_argument("--no-trace", action="store_true",
                            help="Omite las note:* de trazabilidad.")
        parser.add_argument("--mirror", action="store_true",
                            help="Invierte v (familia simétrica).")
        parser.add_argument("--preview", action="store_true",
                            help="Escribe también los SVG por nivel.")

    def handle(self, *args, **opts):
        try:
            lat_s, lon_s = opts["anchor"].split(",")
            anchor = (float(lat_s), float(lon_s))
        except ValueError:
            raise CommandError("--anchor debe ser LAT,LON")

        templates_dir = OSM_DIR / "templates"
        template_path = templates_dir / f"{opts['family']}.json"
        if not template_path.exists():
            available = sorted(p.stem for p in templates_dir.glob("*.json"))
            raise CommandError(
                f"no existe la familia «{opts['family']}» en "
                f"{templates_dir}; hay: {', '.join(available) or 'ninguna'}")

        try:
            graph = load_station_graph(opts["stop_id"])
        except Stop.DoesNotExist:
            raise CommandError(
                f"no hay ninguna estación con stop_id «{opts['stop_id']}»")
        except Exception as exc:
            raise CommandError(f"no se pudo leer el grafo: {exc}")

        template = FamilyTemplate.load(template_path)
        frame = LocalFrame(anchor[0], anchor[1], opts["bearing"],
                           mirror=opts["mirror"])
        builder = StationBuilder(graph, template, frame,
                                 trace=not opts["no_trace"])
        try:
            doc = builder.build()
        except (TemplateError, UnsupportedModeError) as exc:
            raise CommandError(str(exc))

        slug = slugify(graph.station_name)
        out_path = Path(opts["out"]) if opts["out"] else (
            OSM_DIR / f"{slug}.osm")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Se escribe antes de validar a propósito: si la validación
        # encuentra errores conviene poder abrir el archivo y verlos.
        out_path.write_text(doc.to_xml(), encoding="utf-8")

        errors, warnings, summary = validate(doc)
        self.stdout.write(self.style.SUCCESS(f"escrito {out_path}"))
        self.stdout.write(f"estación: {graph.station_name} "
                          f"({graph.stop_id}) — familia {template.family}")
        self.stdout.write(f"ancla {anchor[0]},{anchor[1]}  rumbo "
                          f"{opts['bearing']}°  mirror={opts['mirror']}")
        self.stdout.write("")
        self.stdout.write("resumen por etiqueta")
        for key in sorted(summary):
            self.stdout.write(f"  {key:<40} {summary[key]}")

        for msg in builder.warnings + warnings:
            self.stdout.write(self.style.WARNING(f"aviso: {msg}"))
        for msg in errors:
            self.stdout.write(self.style.ERROR(f"error: {msg}"))
        if not errors:
            self.stdout.write(self.style.SUCCESS(
                "validación: sin errores"))

        if opts["preview"]:
            out_dir = OSM_DIR / "preview"
            out_dir.mkdir(parents=True, exist_ok=True)
            for level, svg in preview_mod.render_all(
                    doc, graph.station_name).items():
                path = out_dir / f"{slug}-level{level}.svg"
                path.write_text(svg, encoding="utf-8")
                self.stdout.write(f"vista previa: {path}")

        if errors:
            raise CommandError(f"{len(errors)} errores de validación")
