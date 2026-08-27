import csv
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from stop.models import Station, Route, Stop
from utils.normalizer import text_normalizer


class Command(BaseCommand):
    help = 'Import station visualization data from CSV'
    remain_rows = []

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file'
        )

    def _build_indexes(self) -> tuple[dict, dict]:
        """Índices stop_id → Station y nombre normalizado → [Station]."""
        by_stop_id = {
            stop.stop_id: stop.station
            for stop in Stop.objects.exclude(
                station__isnull=True).select_related('station')
        }
        by_name: dict[str, list[Station]] = { }
        for station in Station.objects.all():
            by_name.setdefault(
                text_normalizer(station.name), []).append(station)
        return by_stop_id, by_name

    def resolve_station(
            self, row: dict, by_stop_id: dict, by_name: dict
    ) -> Station | None:
        """Resuelve a qué Station corresponde una fila del CSV.

        La columna `stops` es la referencia autoritativa: el nombre del
        placemark del SVG arrastra erratas ('Itzapalapa' por 'Iztapalapa',
        'Periferico Oeste' por 'Periférico Oriente') y formas cortas
        ('Garibaldi' por 'Garibaldi y Lagunilla'), así que solo sirve de
        respaldo cuando la fila no trae stop_ids utilizables.
        """
        stop_ids = re.findall(r"'([^']+)'", row.get('stops') or '')
        candidates = {
            by_stop_id[stop_id] for stop_id in stop_ids
            if stop_id in by_stop_id
        }
        if len(candidates) == 1:
            return candidates.pop()
        if len(candidates) > 1:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ Row '{row['name']}': stops span several stations "
                f"{sorted(s.name for s in candidates)}"
            ))
            return None

        std_row_name = text_normalizer(row['name'])
        if not std_row_name:
            return None
        exact = by_name.get(std_row_name, [])
        if len(exact) == 1:
            return exact[0]
        partial = [
            station
            for std_name, group in by_name.items() if
            std_row_name in std_name or std_name in std_row_name
            for station in group
        ]
        return partial[0] if len(partial) == 1 else None

    def process_row(self, row, station):

        # Mapear campos directos
        station.x_position = Decimal(row['x']) if row['x'] else None
        station.y_position = Decimal(row['y']) if row['y'] else None

        # Extraer main_route del campo "class" (ej: "linea2" -> "2")
        if row['class']:
            route_match = re.search(
                r'linea([0-9A-Z]+)', row.get('class', ''))
            if route_match:
                route_number = route_match.group(1)
                try:
                    route = Route.objects.get(
                        route_short_name=route_number)
                    station.main_route = route
                    # self.stdout.write(
                    #     self.style.SUCCESS(
                    #         f"  ✓ Route {route_number} assigned")
                    # )
                except Route.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Route {route_number} not found")
                    )

        # name_anchor: "end" -> True
        station.end_anchor = (
                row.get('name_anchor', '').strip() == 'end')

        # Extraer rotation del campo "transform"
        # (ej: "rotate(-45)" -> -45)
        # Se limpia primero para que el comando sea idempotente: si la fila
        # ya no trae transform, la rotación anterior no debe sobrevivir.
        station.rotation = None
        if row.get('transform'):
            rotation_match = re.search(
                r'rotate\((-?\d+)\)', row['transform'])
            if rotation_match:
                station.rotation = int(rotation_match.group(1))

        # Construir viz_params con los campos restantes
        viz_params = { }

        # Campos que van a viz_params
        viz_fields = ['href', 'x_name', 'y_name', 'transform']

        for field in viz_fields:
            if field in row and row[field]:
                # Limpiar el nombre del campo (la columna vacía ""
                # se guarda como "index" o similar)
                viz_params[field] = row[field].strip()

        station.viz_params = viz_params

        # Guardar
        station.save()
        # self.stdout.write(
        #     self.style.SUCCESS(f"  ✓ Updated: {station.name}")
        # )

    def handle(self, *args, **options) -> None:
        csv_file = options['csv_file']
        self.remain_rows = []

        with open(csv_file, 'r', encoding='utf-8') as file:
            rows = list(csv.DictReader(file))

        by_stop_id, by_name = self._build_indexes()
        matched_ids: set[int] = set()

        with transaction.atomic():
            for row in rows:
                station = self.resolve_station(row, by_stop_id, by_name)
                if station is None:
                    self.remain_rows.append(row)
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠ Unresolved row: '{row['name']}'"))
                    continue
                if station.id in matched_ids:
                    self.remain_rows.append(row)
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠ Row '{row['name']}' matches "
                        f"'{station.name}', already taken"))
                    continue
                matched_ids.add(station.id)
                self.process_row(row, station)

        orphans = list(Station.objects.exclude(
            id__in=matched_ids).values_list('name', flat=True))
        for name in orphans:
            self.stdout.write(self.style.WARNING(
                f"  ⚠ Station without CSV row: '{name}'"))

        self.stdout.write(self.style.SUCCESS(
            f'Updated {len(matched_ids)} stations | '
            f'{len(self.remain_rows)} unresolved rows | '
            f'{len(orphans)} stations without row'
        ))