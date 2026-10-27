---
type: task
id: task-54
title: "San Pedro (L7): corregir en OSM el jardín poniente publicado sin forma"
state: open
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
- La corrección ya está lista, con los ids del servidor, en `data/osm/l7-san-pedro-de-los-pinos/correcciones/2026-10-27-jardin-poniente.osm`; `check_station_osm_live` no encuentra conflictos de versión. La instrucción para subirla y el comentario de changeset están en `data/osm/publicacion-2026-10-27.md`.
- La explanada oriente (way 1572119589) tiene la misma pérdida, y no es que Pablo la retocara después: Ricardo la tenía con 7 vértices y unos 2430 m² en la 03-rick; la 04 regenerada la redujo a unos 1100 m²; Pablo trabajó en la 06 sobre esa base degradada (6 vértices, unos 1300 m²) y así se publicó. Las coordenadas de la forma de la 03 con los ids del servidor están versionadas en `data/osm/l7-san-pedro-de-los-pinos/correcciones/2026-10-27-explanada-oriente.md`; devolverla es decisión de Ricardo.

La causa de fondo (que una explanada afinada a mano no sobreviva a una regeneración) va en su propia task, [[task-55]].

## Criterios de aceptación

- [ ] Ricardo sube la corrección del jardín poniente (way 1572119592) desde `correcciones/2026-10-27-jardin-poniente.osm`
- [ ] Ricardo decide si la explanada oriente (way 1572119589) también vuelve a su forma de la 03-rick, y si sí, se sube
