---
type: task
id: task-22
title: Servir `is_closed` y `entrance` de los accesos al frontend
state: open
date: 2026-09-01
owner: ricardo
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
related: ["[[adr-0008]]", "[[adr-0009]]"]
---

# Servir `is_closed` y `entrance` de los accesos al frontend


`GET /api/catalogs/` filtra `Stop.objects.filter(location_type_id=1)`: solo estaciones. Los accesos (`location_type` 2) nunca llegan al frontend, así que `is_closed` (clausurados) y `entrance` (solo entrada / solo salida, [[adr-0009]]) existen en la base pero ningún consumidor los ve. El consumidor natural es el módulo de mapeo OSM en Vue ([[adr-0008]]), que necesita accesos y pathways para generar los nodos `railway=subway_entrance` con `entrance=*` de [[adr-0004]].

Decidir si se amplía el queryset de `/api/catalogs/` o si el módulo OSM usa otro endpoint (`StopCatSerializer` ya expone ambos campos).

## Criterios de aceptación

- [ ] Está decidido por qué endpoint llegan los accesos al módulo de mapeo OSM
- [ ] El frontend recibe `is_closed` y `entrance` de cada acceso
