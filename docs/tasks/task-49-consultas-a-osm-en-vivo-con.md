---
type: task
id: task-49
title: Consultas a OSM en vivo con un User-Agent fijo del proyecto
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
---

# Consultas a OSM en vivo con un User-Agent fijo del proyecto

`references/general.md` pide confirmar las bajas de nodos contra OSM en vivo. Cada turno del 27 de octubre de 2026 improvisó su consulta (Overpass o la API 0.6), y uno puso el correo de Ricardo en la cabecera User-Agent de una petición a overpass-api.de; Ricardo quedó avisado ese día. Hay que dejar un script o módulo en `api/utils/osm/` con un User-Agent fijo del proyecto (`api/utils/osm/overpass.py` ya tiene uno), que reciba una lista de ids y devuelva versión, visibilidad y ways o relaciones que los usan, con espejo de respaldo (overpass.kumi.systems respondió cuando overpass-api.de dio 502), y que los agentes lo usen en vez de curl a mano.

## Criterios de aceptación

- [ ] Existe la utilidad y el skill `station-tuning` la nombra como la forma de consultar OSM en vivo
- [ ] Ningún script de scratch de un turno nuevo lleva su propio User-Agent

## Notas de trabajo

- 27 de octubre de 2026 ([[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]): existe el command `check_station_osm_live <archivo.osm>` (`api/utils/osm/live.py`), que con el `USER_AGENT` de `overpass.py` contrasta contra la API 0.6 las versiones de los elementos de OSM con `action`, las bajas bloqueadas por ways o relaciones del servidor, y las relaciones madre que no viajan en el archivo; sale con código 1 si la subida chocaría. Sin espejo de Overpass: usa la API directa. Falta nombrarlo en el skill `station-tuning` (edición de harness del proyecto, pendiente del ok de Ricardo) y que los turnos lo usen en vez de curl.
