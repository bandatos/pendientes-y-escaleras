# stop/management/commands/import_stops.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from stop.models import Route, Stop


class Command(BaseCommand):
    """
    Comando de Django para importar paradas (stops) y sus rutas desde un archivo CSV.

    Este script lee un archivo CSV ubicado en `media/gtfs_metro/stops_metro.csv`,
    extrae la información de cada parada y de su ruta correspondiente, y las
    inserta en la base de datos. Es idempotente, lo que significa que se puede
    ejecutar múltiples veces sin duplicar datos.
    """
    help = 'Importa paradas y rutas del Metro desde un archivo CSV.'

    def process_csv(self, reader):
        """
        :param reader:
        :return:
        """
        created_routes = { }

        for row in reader:
            route = None
            # --- 1. PROCESAR Y CREAR/OBTENER LA RUTA ---
            try:
                # Extraemos el ID de la ruta del stop_id. Ej: '020L12-TLAHUAC' -> '020L12'
                route_id_str = row['stop_id'].split('-')[0]

                # 020L12
                # 0200LB
                # Si no hemos procesado esta ruta en esta ejecución, la creamos o la obtenemos.
                if route_id_str not in created_routes:
                    # Extraemos un nombre corto. Ej: '020L12' -> '12'
                    route_short_name_str = route_id_str.split('020')[
                        -1] if '020' in route_id_str else route_id_str
                    final_route_name = f"CMX020{route_short_name_str}"

                    try:
                        route = Route.objects.get(route_id=final_route_name)
                        created_routes[route_id_str] = route
                    except Route.DoesNotExist:

                        self.stdout.write(
                            self.style.NOTICE(f"No se encontró la ruta '{final_route_name}'."))
                else:
                    route = created_routes[route_id_str]

            except IndexError:
                self.stdout.write(self.style.ERROR(f"Formato de stop_id inválido: '{row['stop_id']}'"))
                continue  # Saltar a la siguiente fila

            # --- 2. CREAR O ACTUALIZAR LA PARADA (STOP) ---
            Stop.objects.update_or_create(
                stop_id=row['stop_id'],
                route=route,
                defaults={
                    'stop_name': row['stop_name'].strip(),
                    'stop_lat': row['stop_lat'],
                    'stop_lon': row['stop_lon'],
                    'zone_id': row['zone_id'],
                    'wheelchair_boarding': int(row['wheelchair_boarding']),
                }
            )

            # action_text = "creada" if created else "actualizada"
            # self.stdout.write(f"  -> Parada {action_text}: {stop_obj.stop_name}")

    def handle(self, *args, **options):
        # Borra todas las paradas:
        Stop.objects.all().delete()
        # Construye la ruta completa al archivo CSV
        file_path = os.path.join(settings.BASE_DIR, 'media', 'gtfs_metro', 'stops_metro.csv')

        self.stdout.write(f"Iniciando la importación desde: {file_path}")

        # Verifica que el archivo exista antes de continuar
        if not os.path.exists(file_path):
            raise CommandError(f'El archivo "{file_path}" no fue encontrado.')

        try:
            # Usamos una transacción para asegurar que toda la operación sea atómica.
            # Si algo falla, se revierte toda la importación.
            with transaction.atomic():
                with open(file_path, mode='r', encoding='utf-8') as csv_file:
                    reader = csv.DictReader(csv_file)
                    self.process_csv(reader)



        except Exception as e:
            raise CommandError(f'Ocurrió un error inesperado durante la importación: {e}')

        self.stdout.write(self.style.SUCCESS('¡Importación completada exitosamente! ✅'))