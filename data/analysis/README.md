# Análisis de la sesión del 2026-08-26

- `kml-estaciones-orientacion.csv`: 187 polígonos de `../StatioArea-and-lines.kml` con centroide, área, elongación, orientación (eje principal) y diferencia contra el rumbo de la línea en `../gtfs/shapes.txt`. Sustenta `docs/decisions/adr-0005` y viene de `docs/reference/2026-08-26-herramientas-mapeo-kml-plantillas`.
- `osm-accesos-cruce.csv`: por estación, nuestros accesos (`Stop` con `location_type=2`) contra los nodos `railway=subway_entrance` de OSM (447 al 2026-08-27), con cuántos se emparejan por rumbo. Insumo de `docs/tasks/task-16` y `task-18`; viene del record `docs/records/2026-08-26-sesion-mapeo-osm`.
