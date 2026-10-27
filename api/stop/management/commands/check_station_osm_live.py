"""Management command: contrasta una versión de estación con OSM vivo.

Lee la API 0.6 con el User-Agent del proyecto (`overpass.USER_AGENT`),
nunca con datos personales. Sale con código 1 si hay conflictos de
versión o bajas que el servidor rechazaría.
"""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from utils.osm.live import LiveCheckError, check, http_get_json, read_file


class Command(BaseCommand):
    help = ("Compara los elementos de OSM con action de una versión .osm "
            "contra el servidor: versiones, bajas bloqueadas y relaciones "
            "que no viajan en el archivo.")

    def add_arguments(self, parser):
        parser.add_argument("version", help="Ruta del .osm de la estación.")

    def handle(self, *args, **opts):
        src = Path(opts["version"])
        if not src.is_file():
            raise CommandError(f"no existe {src}")
        try:
            report = check(read_file(src), http_get_json)
        except LiveCheckError as exc:
            raise CommandError(f"la API de OSM falló: {exc}")

        self.stdout.write(f"{src.name}: {report.checked} elementos de OSM "
                          f"con action contrastados")
        sections = (("conflictos de versión", report.conflicts),
                    ("borrados o inexistentes en OSM", report.gone),
                    ("bajas bloqueadas", report.blocked),
                    ("relaciones que no viajan en el archivo",
                     report.missing_relations))
        for title, lines in sections:
            self.stdout.write(f"{title}: {len(lines)}")
            for line in lines:
                self.stdout.write(f"  {line}")
        if report.failed:
            raise CommandError("la subida chocaría con el estado de OSM",
                               returncode=1)
        self.stdout.write("sin conflictos con OSM")
