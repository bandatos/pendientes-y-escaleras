---
type: task
id: task-71
title: Elevadores de Xola (3) y Ermita L2 (1) en una edición aparte
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-59]]", "[[task-62]]"]
---

# Elevadores de Xola (3) y Ermita L2 (1) en una edición aparte

Decisión de Ricardo del 27 de octubre de 2026 («P4. De acuerdo, 1», [[adr-0018]]): las estaciones se publican sin los elevadores y se suman después, como las relaciones `stop_area` ([[task-51]]). `data/raw/elevadores_escaleras_v4.csv` registra tres elevadores en Xola (andén central y las dos salidas, filas 287–289) y uno en Ermita L2 (salida, fila 246); ninguno está en la base, y el generador rechaza el modo elevador (`api/utils/osm/tags.py`, `UNSUPPORTED_MODES`). [[adr-0004]] ya define `highway=elevator` como nodo. Hace falta cargar el dato (por command o por Miró, según la replicabilidad; es cambio de datos y se confirma con Ricardo), soportar el modo en `tags.py` y el generador, y una edición contra ids del servidor.

## Criterios de aceptación

- [ ] Los elevadores están en la base por un camino reproducible
- [ ] El generador los dibuja
- [ ] Edición aparte lista para que Ricardo la suba
