"""Lista los pathways cuyos dos extremos caen en el mismo `level_index`.

Una escalera o una escalera eléctrica que no cambia de nivel es un error
del relevamiento —o un nivel mal asignado—, y el exportador a OSM no
sabe qué `incline` ponerle. Este comando es la revisión periódica de esa
inconsistencia; el CSV que produce se versiona en `data/analysis/`.

Solo lectura: no escribe nada en la base.
"""
from __future__ import annotations

import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from stair.models import Pathway

REPO_ROOT = Path(settings.BASE_DIR).resolve().parent
DEFAULT_OUT = REPO_ROOT / "data" / "analysis" / "escaleras-mismo-nivel.csv"

# Solo los modos que por definición salvan un desnivel; un pasillo plano
# con los dos extremos en el mismo nivel es lo normal.
MODES = [2, 4]

FIELDS = ["modo", "estacion", "pathway_id", "from_stop_id", "from_nombre",
          "to_stop_id", "to_nombre", "nivel", "bidireccional"]


def station_of(stop) -> str:
    parent = stop.parent_station
    return (parent.short_name or parent.stop_name) if parent else "?"


def same_level_rows() -> list[dict]:
    qs = (Pathway.objects
          .filter(pathway_mode_id__in=MODES)
          .select_related("from_stop__level", "to_stop__level",
                          "from_stop__parent_station",
                          "to_stop__parent_station", "pathway_mode"))
    out = []
    for pathway in qs:
        from_level = pathway.from_stop.level
        to_level = pathway.to_stop.level
        if not from_level or not to_level:
            continue
        if from_level.level_index != to_level.level_index:
            continue
        out.append({
            "modo": str(pathway.pathway_mode),
            "estacion": station_of(pathway.from_stop),
            "pathway_id": pathway.pathway_id,
            "from_stop_id": pathway.from_stop.stop_id,
            "from_nombre": pathway.from_stop.stop_name,
            "to_stop_id": pathway.to_stop.stop_id,
            "to_nombre": pathway.to_stop.stop_name,
            "nivel": from_level.level_index,
            "bidireccional": int(bool(pathway.is_bidirectional)),
        })
    return out


class Command(BaseCommand):
    help = ("Lista escaleras y escaleras eléctricas cuyos dos extremos "
            "están en el mismo nivel, y escribe el CSV de revisión.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--out", default=str(DEFAULT_OUT),
            help="Ruta del CSV de salida (por omisión el canónico)")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo cuenta, sin escribir el CSV")

    def handle(self, *args, **options):
        rows = same_level_rows()
        if not options["dry_run"]:
            path = Path(options["out"])
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            self.stdout.write(self.style.SUCCESS(f"escrito {path}"))
        by_station = {}
        for row in rows:
            by_station[row["estacion"]] = by_station.get(
                row["estacion"], 0) + 1
        self.stdout.write(f"pathways en el mismo nivel: {len(rows)} "
                          f"en {len(by_station)} estaciones")
        for station in sorted(by_station):
            self.stdout.write(f"  {station:<32} {by_station[station]}")
