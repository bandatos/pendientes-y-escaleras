---
type: task
id: task-27
title: "Emitir etiquetas gtfs:* en el exportador OSM y decidir el sufijo de feed"
state: open
date: 2026-09-02
owner: ai
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
related: ["[[adr-0004]]", "[[adr-0010]]", "[[task-19]]"]
---

# Emitir etiquetas gtfs:* en el exportador OSM y decidir el sufijo de feed

[[adr-0004]] decidió identificar con `gtfs:stop_id:MX-CMX-<feed>` y el generador de [[adr-0010]] no emite ninguna etiqueta `gtfs:*`: las de traza son `note:*` y se retiran con `--no-trace`, así que un archivo listo para subir no llevaría ningún identificador GTFS. Falta decidir el sufijo de feed (el GTFS de la CDMX no lo declara) y qué objetos lo llevan: el `stop_id` oficial (`0200L2-PORTALES`) es de la estación, que el generador no crea; los ids de andén y acceso (`L2-PORTALES-P-01`) son nuestros, no del feed oficial. Ricardo decide el sufijo; el cambio va en `api/utils/osm/tags.py`.

Además: las etiquetas de traza `note:stop_id`, `note:pathway_id` y `note:miro_id` se emiten por defecto y solo se retiran con `--no-trace`, contra el «nunca suben» de [[adr-0003]]. Antes de que voluntarios toquen archivos hay que decidir si el valor seguro se invierte (traza opcional, `--trace`).

## Criterios de aceptación

- [ ] Sufijo de feed decidido y documentado en el ADR o en la referencia de alineación
- [ ] El exportador emite `gtfs:*` en los objetos acordados y `--no-trace` los conserva

## Notas de trabajo

- 2 de septiembre de 2026 (tarde, [[2026-09-02-sesion-integracion-osm-y-niveles]]): en el exportador el nombre del acceso pasó a `description`, se retiró `level:ref` y toda `highway=steps` lleva `wheelchair=no` ([[adr-0011]]). Siguen pendientes el sufijo de feed y si las `note:*` pasan a opcionales.
