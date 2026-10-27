---
type: task
id: task-48
title: Command de validación de un archivo .osm editado, con el marco de la 01
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-38]]"]
---

# Command de validación de un archivo .osm editado, con el marco de la 01

Hoy la validación solo corre dentro de `export_station_osm`. Cada turno sobre una versión editada a mano copia un `validate_file.py` de scratch con el marco de otra estación fijo en el código (pasó en San Joaquín, San Pedro, San Antonio y Portales el 27 de octubre de 2026) y a veces con la reconstrucción incompleta (no asigna el tipo de entrada, así que no detecta accesos aislados: San Pedro 06 tenía el oriente desconectado y lo encontró otro script). Hace falta `validate_station_osm <archivo>` que lea el marco de la cabecera de la versión 01 de la carpeta, reconstruya el documento completo, corra `utils.osm.validate` y además el chequeo de segmentos contra el área (`segcheck`), los cruces sin nodo entre niveles adyacentes (`geomcheck.py` de `.claude/scratch/portales/`) y el alcance desde cada acceso a los dos andenes (`reach.py` de `.claude/scratch/san-pedro/`).

En el mismo movimiento: `compose_station_imagery` toma el marco de `general-anaya-02-claude.osm` y no de la 01 (coinciden hoy, pero contradice la regla «el marco es el de la 01»).

## Criterios de aceptación

- [ ] Existe el command y valida las seis versiones aprobadas del 27 de octubre con el resultado que dieron los scripts de scratch
- [ ] `compose_station_imagery` lee el marco de la 01
