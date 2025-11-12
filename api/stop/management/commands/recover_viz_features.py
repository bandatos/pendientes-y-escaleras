import csv
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from stop.models import Station, Route
from utils.normalizer import text_normalizer


class Command(BaseCommand):
    help = 'Import station visualization data from CSV'
    remain_rows = []
    remain_stations = []

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file'
        )

    def process_row(self, row, station):

        std_row_name = text_normalizer(row['name'])
        std_station_name = text_normalizer(station.name)
        is_match = False

        if std_row_name == std_station_name:
            is_match = True
        elif std_row_name in std_station_name or std_station_name in std_row_name:
            is_match = True

        if not is_match:
            self.remain_rows.append(row)
            self.remain_stations.append(station)
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠ Name mismatch: CSV "
                    f"'{row['name']}' != Station '{station.name}'"
                )
            )
            # return

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

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        self.remain_rows = []
        self.remain_stations = []

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            sorted_csv_data = sorted(reader, key=lambda x: x['name'])

            # Obtener todas las estaciones ordenadas por name
            stations = Station.objects.all().order_by('name')

            with transaction.atomic():
                for row, station in zip(sorted_csv_data, stations):
                    self.process_row(row, station)


        self.stdout.write(
            self.style.SUCCESS('Successfully imported station visualization data')
        )