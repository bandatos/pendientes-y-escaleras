import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from stop.models import Route  # Asegúrate que 'stair' es el nombre correcto de tu app


class Command(BaseCommand):
    help = ('Importa rutas de transporte desde el archivo '
            'media/gtfs_metro/routes_metro.csv')

    def handle(self, *args, **options):
        # Construye la ruta al archivo CSV
        # Usamos BASE_DIR para tener una ruta absoluta al proyecto
        file_path = os.path.join(
            settings.BASE_DIR, 'media', 'gtfs_metro', 'routes_metro.csv'
        )

        if not os.path.exists(file_path):
            raise CommandError(f"El archivo no se encuentra en: {file_path}")

        self.stdout.write(
            self.style.NOTICE(f"Iniciando importación desde {file_path}..."))

        created_count = 0
        updated_count = 0

        try:
            # Usamos transaction.atomic() para que, si algo falla,
            # no se guarde nada en la base de datos.
            with transaction.atomic():
                with open(file_path, mode='r', encoding='utf-8') as f:
                    # DictReader es perfecto porque usa la primera fila
                    # (cabeceras) como claves del diccionario para cada fila.
                    reader = csv.DictReader(f)

                    for row in reader:
                        # Usamos update_or_create para la idempotencia.
                        # Si el script se corre de nuevo, no creará duplicados.
                        # Buscará por 'route_id' y si existe, actualizará
                        # los campos en 'defaults'. Si no, creará un nuevo objeto.
                        obj, created = Route.objects.update_or_create(
                            route_id=row['route_id'],
                            defaults={
                                'route_short_name': row['route_short_name'],
                                'route_long_name': row['route_long_name'],
                                'route_type': int(row['route_type']),
                                'route_color': row['route_color'],
                                'route_text_color': row['route_text_color'],
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

        except Exception as e:
            raise CommandError(f"Error durante la importación: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Importación completada con éxito. "
            f"Rutas creadas: {created_count}. Rutas actualizadas: {updated_count}."
        ))