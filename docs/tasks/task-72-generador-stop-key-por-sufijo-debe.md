---
type: task
id: task-72
title: "Generador: stop_key por sufijo debe fallar si dos stops de la estación chocan"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Generador: stop_key por sufijo debe fallar si dos stops de la estación chocan

`stop_key` (`api/utils/osm/graph.py`) indexa los stops por su sufijo (`N-01`). Sin el filtro `--line`, Ermita (21 stops de L2 y L12 bajo un mismo padre) colapsa en 13 claves y 40 pathways se pegan al stop equivocado sin ningún error. Con `--line` no hay choque, pero el silencio sigue siendo posible en cualquier padre con stops de dos líneas. Propuesta del ejecutor del 27 de octubre de 2026: que `load_station_graph` falle con mensaje claro cuando dos stops comparten clave.

## Criterios de aceptación

- [ ] load_station_graph falla si dos stops comparten clave
- [ ] Prueba en api/utils/osm
