"""Catálogo único de etiquetas OSM del exportador.

Toda decisión de etiquetado vive aquí; el resto del paquete solo arma
geometría y XML. Una tarea posterior moverá esto a configuración, así
que ninguna otra parte del código debe escribir literales de tags.
"""
from __future__ import annotations

import re


class UnsupportedModeError(Exception):
    """Modo de pathway que este exportador todavía no sabe dibujar."""


# Ids de PathwayMode (id en BD == pathway_mode de GTFS).
MODE_WALKWAY = 1
MODE_STAIRS = 2
MODE_MOVING_WALKWAY = 3
MODE_ESCALATOR = 4
MODE_ELEVATOR = 5

# Nombres de terminal tal como se escriben en OSM, indexados por el
# fragmento que aparece en el stop_name del andén lateral.
TERMINAL_ALIASES = {
    "Rosario": "El Rosario",
}

_DESTINATION_RE = re.compile(r"^\s*L\d+\s*(<=>|=>|<=)\s*(.+?)\s*$")


def platform_destination(stop_name: str) -> str | None:
    """«L7 => Rosario» -> «El Rosario»; «L2 <=> …» (isla) -> None."""
    m = _DESTINATION_RE.match(stop_name or "")
    if not m or m.group(1) == "<=>":
        return None
    dest = m.group(2)
    return TERMINAL_ALIASES.get(dest, dest)


def level_value(*indexes: float) -> str:
    """level=* con los niveles ordenados ascendentemente y sin repetir."""
    vals = sorted({int(round(i)) for i in indexes})
    return ";".join(str(v) for v in vals)


def platform_tags(station_name: str, stop_name: str, level_index: float,
                  level_name: str | None, underground: bool) -> dict:
    tags = {
        "railway": "platform",
        "public_transport": "platform",
        "area": "yes",
        "subway": "yes",
        "level": level_value(level_index),
        "name": station_name,
    }
    if level_name:
        tags["level:ref"] = level_name
    dest = platform_destination(stop_name)
    if dest:
        tags["destination"] = dest
    if underground:
        # Sin `tunnel`: es una clave de vía lineal y el andén es un área;
        # `location=underground` ya dice lo que hay que decir.
        tags["layer"] = str(int(round(level_index)))
        tags["location"] = "underground"
    return tags


def platform_spine_tags(level_index: float) -> dict:
    """Línea de circulación interior del andén."""
    return {
        "highway": "footway",
        "indoor": "yes",
        "level": level_value(level_index),
    }


def footway_tags(levels: list[float], incline: str | None = None) -> dict:
    tags = {
        "highway": "footway",
        "indoor": "yes",
        "level": level_value(*levels),
    }
    if incline:
        tags["incline"] = incline
    return tags


def steps_tags(levels: list[float], incline: str,
               conveying: str | None = None) -> dict:
    """`step_count` se omite a propósito: el relevamiento no lo tiene."""
    tags = {
        "highway": "steps",
        "indoor": "yes",
        "level": level_value(*levels),
        "incline": incline,
    }
    if conveying:
        tags["conveying"] = conveying
    return tags


def entrance_tags(stop_name: str, entrance_value: str | None,
                  level_index: float) -> dict:
    return {
        "railway": "subway_entrance",
        "entrance": entrance_value or "yes",
        "name": stop_name,
        "level": level_value(level_index),
    }


def turnstile_tags(level_index: float) -> dict:
    return {
        "barrier": "turnstile",
        "amenity": "ticket_validator",
        "level": level_value(level_index),
    }


def trace_tags(stop_id: str | None = None, miro_id: str | None = None,
               pathway_id: str | None = None) -> dict:
    """Etiquetas de trazabilidad local; se quitan con --no-trace.

    No son etiquetas OSM: sirven para que la revisión en JOSM pueda
    volver del objeto dibujado al registro de la base. Nunca se suben.
    """
    tags = {}
    if stop_id:
        tags["note:stop_id"] = stop_id
    if pathway_id:
        tags["note:pathway_id"] = pathway_id
    if miro_id:
        tags["note:miro_id"] = miro_id
    return tags


TRACE_KEYS = ("note:stop_id", "note:pathway_id", "note:miro_id")


MODE_NAMES = {
    MODE_WALKWAY: "pasillo",
    MODE_STAIRS: "escalera",
    MODE_MOVING_WALKWAY: "banda móvil",
    MODE_ESCALATOR: "escalera eléctrica",
    MODE_ELEVATOR: "elevador",
}

# Modos que el exportador todavía no sabe etiquetar. El elevador es un
# nodo `highway=elevator` (ADR 0004), no un way, así que dibujarlo como
# pasillo produciría un archivo silenciosamente equivocado.
UNSUPPORTED_MODES = (MODE_MOVING_WALKWAY, MODE_ELEVATOR)


def way_tags_for_pathway(mode_id: int, is_bidirectional: bool,
                         level_from: float, level_to: float,
                         reversed_drawing: bool) -> dict:
    """Etiquetas del way según modo, sentido y desnivel.

    `level_from`/`level_to` son los niveles de los stops origen y destino
    del pathway; `reversed_drawing` indica que el way se dibuja al revés
    del pathway (caso bidireccional que se dibuja siempre de abajo hacia
    arriba).
    """
    if mode_id in UNSUPPORTED_MODES:
        raise UnsupportedModeError(
            f"modo {mode_id} ({MODE_NAMES[mode_id]}) sin regla de "
            f"etiquetado; hay que añadirla en utils/osm/tags.py antes "
            f"de exportar una estación que lo use")
    if mode_id not in MODE_NAMES:
        raise UnsupportedModeError(f"modo de pathway desconocido: {mode_id}")
    lo, hi = (level_to, level_from) if reversed_drawing else (
        level_from, level_to)
    levels = [level_from, level_to]
    if mode_id in (MODE_STAIRS, MODE_ESCALATOR):
        if hi > lo:
            incline = "up"
        elif hi < lo:
            incline = "down"
        else:
            incline = "up"
        conveying = None
        if mode_id == MODE_ESCALATOR:
            conveying = "reversible" if is_bidirectional else "forward"
        tags = steps_tags(levels, incline, conveying=conveying)
    else:
        incline = None
        if level_from != level_to:
            incline = "up" if hi > lo else "down"
        tags = footway_tags(levels, incline=incline)
    if not is_bidirectional:
        # También en las eléctricas de un solo sentido: `conveying=forward`
        # describe la máquina y ningún ruteador peatonal lo consume, así
        # que sin esto la restricción de paso no queda en el archivo.
        tags["oneway:foot"] = "yes"
    return tags
