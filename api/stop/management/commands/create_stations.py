import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from stop.models import Stop, Station


class Command(BaseCommand):
    help = 'Crea las estacions (Station) a partir de Stops'

    def handle(self, *args, **options):
        all_stops = Stop.objects.all()
        self.stdout.write(self.style.NOTICE(f'Procesando {all_stops.count()} paradas...'))
        # delete all Station entries
        Station.objects.all().delete()
        station_codes = {}
        created_count = 0

        for stop in all_stops:
            name = stop.stop_name
            if name in station_codes:
                station = station_codes[name]
            else:
                station, created = Station.objects.get_or_create(name=name)
                station_codes[name] = station
                created_count += 1
            stop.station = station
            stop.save()
        self.stdout.write(self.style.SUCCESS(f'Se crearon {created_count} estaciones únicas.'))


