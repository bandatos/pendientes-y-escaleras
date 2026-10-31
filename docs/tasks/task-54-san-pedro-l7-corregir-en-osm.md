---
type: task
id: task-54
title: "San Pedro (L7): corregir en OSM el jardín poniente publicado sin forma"
state: closed
date: 2026-10-27
owner: ricardo
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-26]]", "[[task-11]]"]
---

# San Pedro (L7): corregir en OSM el jardín poniente publicado sin forma

Al final de la madrugada del 27 de octubre de 2026 Ricardo reportó que el jardín poniente de San Pedro de los Pinos «quedó sin forma» en lo publicado. El tracer que lo investigó encontró esto:

- La explanada poniente se publicó en el changeset 191086111 como el rectángulo de la versión 01; en el servidor es la way 1572119592.
- Ricardo le había dado su forma real a mano en `san-pedro-de-los-pinos-02-rick.osm` y `03-rick.osm`. La 04, regenerada desde la plantilla, la perdió: el generador solo sabe dibujar un cuadro (`plaza_half`) y ningún bloque de estación guarda esa geometría. De la 04 a la 08 nadie lo vio, porque `compose_station_imagery` solo dibuja las explanadas del contexto de OSM y no las del `.osm` que recibe.
- El rectángulo invade la escuela (way 790807303), cruza la banqueta 1275346680 sin nodo compartido y entra al arroyo de la avenida Revolución.
- La corrección ya está lista, con los ids del servidor, en el archivo «2026-10-27-jardin-poniente.osm» de la entonces carpeta `correcciones/` de San Pedro (borrado el 30 de octubre de 2026, vive en el commit 270df85); `check_station_osm_live` no encuentra conflictos de versión. La instrucción para subirla y el comentario de changeset están en `data/osm/publicacion-2026-10-27.md`.
- La explanada oriente (way 1572119589) tiene la misma pérdida, y no es que Pablo la retocara después: Ricardo la tenía con 7 vértices y unos 2430 m² en la 03-rick; la 04 regenerada la redujo a unos 1100 m²; Pablo trabajó en la 06 sobre esa base degradada (6 vértices, unos 1300 m²) y así se publicó. Las coordenadas de la forma de la 03 con los ids del servidor están versionadas en el archivo «2026-10-27-explanada-oriente.md» de esa misma carpeta (borrado el 30 de octubre de 2026, vive en el commit 270df85); devolverla es decisión de Ricardo.

La causa de fondo (que una explanada afinada a mano no sobreviva a una regeneración) va en su propia task, [[task-55]].

## Criterios de aceptación

- [x] Ricardo sube la corrección del jardín poniente (way 1572119592) desde `correcciones/2026-10-27-jardin-poniente.osm` (no desde el archivo: la resolvió directo en iD, changeset 191252788, sin el vértice del chaflán)
- [x] Ricardo decide si la explanada oriente (way 1572119589) también vuelve a su forma de la 03-rick, y si sí, se sube

## Notas de trabajo

- 30 de octubre de 2026 ([[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]): Ricardo decidió devolver también la oriente y resolvió las dos directamente en iD, changeset 191252788: la oriente (way 1572119589) en v2 con cinco vértices, sin el nodo compartido con la banqueta; la poniente (way 1572119592) con sus cuatro nodos movidos a v2, sin el quinto vértice del chaflán. Los dos archivos de `correcciones/` del 27 se borraron (viven en `270df85`) y la carpeta desapareció por convención ([[adr-0021]]). Los dos criterios quedan cubiertos por esa edición.
