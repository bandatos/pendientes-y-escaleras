---
type: task
id: task-32
title: Respaldo de la base original de pathways y reconciliación de los ids de producción que Miró conserva
state: open
date: 2026-09-02
owner: ricardo
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
related: ["[[task-17]]", "[[task-14]]", "[[task-12]]"]
---

# Respaldo de la base original de pathways y reconciliación de los ids de producción que Miró conserva

Ricardo, 2 de septiembre: falta un respaldo de la base real y original de pathways, y muchos conectores de Miró (sobre todo escaleras eléctricas) llevan el id de `Pathway` de la base de datos de producción. Hoy `Pathway.osm_type`/`osm_id` ([[task-17]]) enlazan con OSM pero nada enlaza con producción, y una reimportación desde Miró recrea los pathways con el id del conector. Hay que: hacer el respaldo (los dumps van a `~/databases/`), inventariar qué conectores llevan id de producción y decidir cómo se reconcilian con los pathways actuales.

## Criterios de aceptación

- [ ] Existe el dump de la base original de pathways en `~/databases/` con fecha
- [ ] Está inventariado qué conectores de Miró llevan id de producción y a qué pathway actual corresponden
- [ ] Decidido cómo se conserva el id de producción (campo, CSV o mapa)
