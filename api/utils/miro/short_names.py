"""Nombres cortos de estación: los títulos con que el tablero de Miró las
llama cuando el nombre GTFS trae añadidos.

Vive fuera de los comandos y de las migraciones porque las dos cosas
necesitan la misma tabla: `import_stops` borra y recrea todos los Stop, así
que sin volver a aplicarla una base recién sembrada perdería el enlace con
los frames de Miró de estas cinco estaciones.
"""

SHORT_NAMES: dict[str, str] = {
    "UAM Azcapotzalco": "Azcapotzalco",
    "Etiopía y Plaza de la Transparencia": "Etiopía",
    "Ferrería y Arena Ciudad de México": "Ferrería",
    "Miguel Ángel de Quevedo": "M.A. de Quevedo",
    "Viveros y Derechos Humanos": "Viveros",
}

STATION_LOCATION_TYPE = 1


def apply_short_names(model) -> int:
    """Escribe `short_name` en las estaciones de la tabla. Idempotente.

    Args:
        model: el modelo `Stop` — real o el histórico de una migración.

    Returns:
        Cuántas filas quedaron con `short_name`.
    """
    total = 0
    for stop_name, short_name in SHORT_NAMES.items():
        total += model.objects.filter(
            location_type_id=STATION_LOCATION_TYPE, stop_name=stop_name
        ).update(short_name=short_name)
    return total
