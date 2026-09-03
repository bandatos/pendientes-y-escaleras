"""Carga los enlaces blandos a OSM declarados en data/osm/osm-links.csv.

El CSV es la fuente: la base se reconstruye desde el repo, así que un
enlace escrito a mano en la base se pierde en la siguiente importación.
"""
import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from stair.models import Pathway
from stop.models import OSM_TYPE_CHOICES, Stop

REPO_ROOT = Path(settings.BASE_DIR).resolve().parent
LINKS_CSV = REPO_ROOT / "data" / "osm" / "osm-links.csv"

VALID_TYPES = {value for value, _ in OSM_TYPE_CHOICES}
REQUIRED_COLUMNS = {"object", "key", "osm_type", "osm_id"}

# Cada clase de objeto enlazable, con el campo por el que se busca.
TARGETS = {
    "stop": (Stop, "stop_id"),
    "pathway": (Pathway, "pathway_id"),
}


class Command(BaseCommand):
    help = (
        "Carga en osm_type/osm_id de Stop y Pathway los enlaces blandos a "
        "OSM declarados en data/osm/osm-links.csv."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv", default=str(LINKS_CSV),
            help="Ruta del CSV de enlaces (por omisión el canónico)")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo reporta lo que haría, sin escribir en la base")
        parser.add_argument(
            "--quiet-unknown", action="store_true",
            help="No avisa de las claves que la base todavía no tiene; "
                 "lo usa import_stops, que corre antes que los pathways")

    def handle(self, *args, **options):
        path = Path(options["csv"])
        if not path.exists():
            raise CommandError(f"No existe el CSV: {path}")

        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        if rows and not REQUIRED_COLUMNS.issubset(rows[0].keys()):
            missing = sorted(REQUIRED_COLUMNS - set(rows[0].keys()))
            raise CommandError(f"Faltan columnas en el CSV: {missing}")

        linked, unchanged, unknown, invalid = 0, 0, [], []
        with transaction.atomic():
            for number, row in enumerate(rows, start=2):
                kind = (row.get("object") or "").strip().lower()
                key = (row.get("key") or "").strip()
                osm_type = (row.get("osm_type") or "").strip().lower()
                raw_id = (row.get("osm_id") or "").strip()
                if not key:
                    continue
                if (kind not in TARGETS or osm_type not in VALID_TYPES
                        or not raw_id.isdigit()):
                    invalid.append((number, key))
                    continue

                model, lookup = TARGETS[kind]
                obj = model.objects.filter(**{lookup: key}).first()
                if obj is None:
                    unknown.append(f"{kind} {key}")
                    continue

                osm_id = int(raw_id)
                if (obj.osm_type, obj.osm_id) == (osm_type, osm_id):
                    unchanged += 1
                    continue
                obj.osm_type = osm_type
                obj.osm_id = osm_id
                if not options["dry_run"]:
                    obj.save(update_fields=["osm_type", "osm_id"])
                linked += 1

            if options["dry_run"]:
                transaction.set_rollback(True)

        prefix = "[dry-run] " if options["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}{linked} enlazados, {unchanged} sin cambio, "
            f"{len(unknown)} claves desconocidas, "
            f"{len(invalid)} filas inválidas"))
        if not options["quiet_unknown"]:
            for label in unknown:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ no existe en la base: {label}"))
        for number, key in invalid:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ línea {number} ({key}): object, osm_type u osm_id "
                f"inválidos"))
