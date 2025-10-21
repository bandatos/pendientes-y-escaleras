import csv
from django.core.management.base import BaseCommand
from django.db.models import Max
from stair.models import Stair
from stop.models import Stop, Route
from utils.normalizer import text_normalizer


class Command(BaseCommand):
    help = 'Importa escaleras eléctricas desde CSV del metro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todas las escaleras antes de importar',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='media/escaleras_electricas.csv',
            help='Ruta al archivo CSV',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Stair.objects.count()
            Stair.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Se eliminaron {count} escaleras existentes\n')
            )

        csv_path = options['file']
        created_count = 0
        error_count = 0

        # Cache para stops ya encontrados
        stops_cache = { }

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    linea = row['linea'].strip()
                    estacion = row['estacion'].strip()
                    direccion = row['direccion'].strip()
                    ubicacion = row['ubicacion'].strip()

                    # Normalizar nombre de estación del CSV
                    estacion_normalizada = text_normalizer(estacion)

                    # Clave para cache
                    cache_key = f"{linea}_{estacion_normalizada}"

                    # Buscar stop en cache o en BD
                    if cache_key in stops_cache:
                        stop = stops_cache[cache_key]
                    else:
                        # Buscar la ruta
                        try:
                            route = Route.objects.get(route_short_name=linea)
                        except Route.DoesNotExist:
                            self.stdout.write(
                                self.style.ERROR(f'✗ Ruta no encontrada: Línea {linea}')
                            )
                            error_count += 1
                            continue

                        # Buscar el stop comparando nombres normalizados
                        stop = None
                        stops = Stop.objects.filter(route=route).select_related('route')

                        for s in stops:
                            if s.stop_name and text_normalizer(s.stop_name) == estacion_normalizada:
                                stop = s
                                break

                        if not stop:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'✗ Stop no encontrado: {estacion} en Línea {linea}'
                                )
                            )
                            error_count += 1
                            continue

                        # Guardar en cache
                        stops_cache[cache_key] = stop

                    # Obtener el siguiente número para esta estación
                    max_number = Stair.objects.filter(stop=stop).aggregate(
                        Max('number')
                    )['number__max']
                    next_number = (max_number + 1) if max_number else 1

                    # Crear la escalera
                    Stair.objects.create(
                        number=next_number,
                        stop=stop,
                        original_direction=direccion,
                        original_location=ubicacion,
                        validated=False
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Escalera #{next_number}: {stop.stop_name} '
                            f'(L{linea}) - {direccion} - {ubicacion}'
                        )
                    )
                    created_count += 1

            # Resumen final
            self.stdout.write('\n' + '=' * 60)
            if error_count == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Importación exitosa: {created_count} escaleras creadas'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Importación completada con errores:\n'
                        f'  • {created_count} escaleras creadas\n'
                        f'  • {error_count} errores'
                    )
                )
            self.stdout.write('=' * 60)

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'✗ Archivo no encontrado: {csv_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error inesperado: {str(e)}')
            )