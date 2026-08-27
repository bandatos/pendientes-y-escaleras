---
type: task
id: task-17
title: "Migración: campo osm_id (enlace blando) en Stop y Pathway"
state: open
date: 2026-08-26
owner: ricardo
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
related: ["[[adr-0003]]"]
---

# Migración: campo osm_id (enlace blando) en Stop y Pathway

Decisión de [[adr-0003]]: la unión entre nuestra base y OpenStreetMap es por identificador, con un campo `osm_id` en `Stop` y `Pathway` que guarde el id del nodo/way de OSM como enlace blando (OSM no garantiza ids permanentes; cuando se rompa, se re-empareja por `ref` + estación + geometría). Es migración de esquema: la confirma Ricardo antes de escribirla. Campo nullable, indexado; considerar `osm_type` (node/way) junto al id.

## Criterios de aceptación

- [ ] Migración aplicada en `stop` y `stair` con `osm_id` (y tipo) nullable e indexado
- [ ] Los serializers del módulo de mapeo exponen el campo
- [ ] Existe un command o flujo documentado para volcar el `osm_id` tras subir a OSM
