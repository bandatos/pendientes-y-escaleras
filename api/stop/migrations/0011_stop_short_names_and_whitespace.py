"""Rellena short_name y normaliza espacios repetidos en stop_name."""
import re

from django.db import migrations

# Importar código de la app desde una migración es riesgoso cuando ese
# código puede cambiar, pero `short_names` es una tabla de constantes sin
# dependencias: duplicarla aquí garantizaría que las dos copias se
# separaran, que es justo lo que hay que evitar (`import_stops` reaplica
# la misma tabla después de recrear las paradas).
from utils.miro.short_names import SHORT_NAMES, apply_short_names


def set_short_names(apps, schema_editor) -> None:
    apply_short_names(apps.get_model("stop", "Stop"))


def unset_short_names(apps, schema_editor) -> None:
    Stop = apps.get_model("stop", "Stop")
    Stop.objects.filter(short_name__in=SHORT_NAMES.values()).update(
        short_name=None)


def collapse_whitespace(apps, schema_editor) -> None:
    Stop = apps.get_model("stop", "Stop")
    for stop in Stop.objects.exclude(stop_name__isnull=True).iterator():
        clean = re.sub(r"\s+", " ", stop.stop_name).strip()
        if clean != stop.stop_name:
            Stop.objects.filter(pk=stop.pk).update(stop_name=clean)


def noop(apps, schema_editor) -> None:
    """Los espacios repetidos eran un defecto: no se restauran."""


class Migration(migrations.Migration):

    dependencies = [
        ("stop", "0010_stop_entrance_short_name"),
    ]

    operations = [
        migrations.RunPython(set_short_names, unset_short_names),
        migrations.RunPython(collapse_whitespace, noop),
    ]
