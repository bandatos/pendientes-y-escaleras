---
type: task
id: task-17
title: "Migración: campo osm_id (enlace blando) en Stop y Pathway"
state: closed
date: 2026-08-26
owner: ricardo
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
related: ["[[adr-0003]]"]
---

# Migración: campo osm_id (enlace blando) en Stop y Pathway

Decisión de [[adr-0003]]: la unión entre nuestra base y OpenStreetMap es por identificador, con un campo `osm_id` en `Stop` y `Pathway` que guarde el id del nodo/way de OSM como enlace blando (OSM no garantiza ids permanentes; cuando se rompa, se re-empareja por `ref` + estación + geometría). Es migración de esquema: la confirma Ricardo antes de escribirla. Campo nullable, indexado; considerar `osm_type` (node/way) junto al id.

## Criterios de aceptación

- [x] Migración aplicada en `stop` y `stair` con `osm_id` (y tipo) nullable e indexado
- [x] Los serializers del módulo de mapeo exponen el campo
- [ ] Existe un command o flujo documentado para volcar el `osm_id` tras subir a OSM

## Notas de trabajo

- 2 de septiembre de 2026 ([[2026-09-02-sesion-integracion-osm-y-niveles]]): Ricardo confirmó la migración y se aplicó: `osm_type` (node/way/relation) y `osm_id` nulos e indexados en `Stop` (`stop/migrations/0012`) y `Pathway` (`stair/migrations/0006`); `StopCatSerializer` y `PathwaySerializer` exponen ambos campos. El enlace se carga desde `data/osm/osm-links.csv` (columnas `object,key,osm_type,osm_id,note`, `object` en stop o pathway) con el command `link_osm_ids`, idempotente y con `--dry-run`; `import_stops` lo llama al final porque recrea todas las paradas. Semilla: los tres accesos de Portales y San Pedro cuyo nodo de OSM coincide a menos de 10 cm. El tercer criterio, capturar el `osm_id` después de subir a OSM, no se cumple: hoy el CSV se mantiene a mano y nada lee ids de vuelta tras una subida; queda anotado en [[task-11]], que gobierna la subida. La escritura desde Vue depende de [[task-22]]. La task se cierra con lo hecho.
