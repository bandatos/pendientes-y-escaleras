"""Lectura del polígono de área de estación del KML del relevamiento.

`data/StatioArea-and-lines.kml` trae un Placemark por estación con el
polígono que el equipo dibujó sobre imagen satelital. Es la única huella
de superficie que tenemos para las estaciones sin contorno en OSM.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path
from xml.etree import ElementTree

KML_NS = "{http://www.opengis.net/kml/2.2}"


class KmlError(Exception):
    pass


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.lower().split())


def station_polygon(path: Path, station_name: str
                    ) -> list[tuple[float, float]]:
    """Anillo exterior del Placemark de la estación, como (lat, lon)."""
    if not path.exists():
        raise KmlError(f"no existe el KML de áreas de estación: {path}")
    root = ElementTree.parse(path).getroot()
    wanted = _fold(station_name)
    names = []
    for placemark in root.iter(f"{KML_NS}Placemark"):
        name_el = placemark.find(f"{KML_NS}name")
        name = name_el.text if name_el is not None else ""
        names.append(name)
        if _fold(name) != wanted:
            continue
        ring = placemark.find(
            f"{KML_NS}Polygon/{KML_NS}outerBoundaryIs/"
            f"{KML_NS}LinearRing/{KML_NS}coordinates")
        if ring is None or not (ring.text or "").strip():
            raise KmlError(
                f"el Placemark «{name}» del KML no trae un polígono con "
                f"anillo exterior")
        return _parse_coordinates(ring.text)
    raise KmlError(
        f"el KML no tiene ningún Placemark llamado «{station_name}»; "
        f"hay {len(names)} placemarks")


def _parse_coordinates(text: str) -> list[tuple[float, float]]:
    points = []
    for chunk in text.split():
        parts = chunk.split(",")
        if len(parts) < 2:
            continue
        points.append((float(parts[1]), float(parts[0])))
    # El anillo KML repite el primer punto al final; el way cerrado lo
    # vuelve a añadir por su cuenta.
    if len(points) > 2 and points[0] == points[-1]:
        points.pop()
    if len(points) < 3:
        raise KmlError("el anillo del KML tiene menos de tres vértices")
    return points
