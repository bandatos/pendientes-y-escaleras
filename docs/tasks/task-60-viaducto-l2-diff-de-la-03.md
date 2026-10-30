---
type: task
id: task-60
title: "Viaducto (L2): diff de la 03-rick contra la 02-claude"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Viaducto (L2): diff de la 03-rick contra la 02-claude

Carpeta `data/osm/l2-viaducto/`. Marco de la 01: rumbo 8,3°, ancla 19.4008868,-99.1368843, `0200L2-VIADUCTO`. Hechos en `.claude/skills/station-tuning/references/estaciones/viaducto.md`.

## Versiones

- `viaducto-01-claude.osm`: generada tal cual.
- `viaducto-02-claude.osm`: la nuestra para comparar; la reproduce el bloque `0200L2-VIADUCTO` de la plantilla sin diferencias (`diff_station_osm`).
- `viaducto-03-rick.osm`: la de Ricardo. Textual: «Viaducto solo tuvo cambios mínimos».

## Preguntas y respuestas de Ricardo

- Sin preguntas de fondo en la presentación. Dos dudas del trazador que el diff debe confirmar: las puntas norte y sur del área se dejaron en las esquinas viejas de OSM (2266139564, 2266139680, 2266139624, 2266139597) para no soltar las bardas 1322749521/22, con un quiebre de 0,4 m en el muro poniente en los últimos 12 m del norte; y E-02 sin conector porque los tres candidatos cruzaban la calzada o entraban al túnel 868793751.
- **P8, nombre del contorno** (way 217341597, «Metro Viaducto»). Respondida: pasa a «Viaducto». Pendiente de aplicar.

## Cómo arranca el turno

El primer entregable es el diff completo de la versión de Ricardo contra la nuestra, por `note:pathway_id`/`note:stop_id` y con el área vértice a vértice en el marco local de la 01 (skill `station-tuning`, «Herramientas del turno»), con hipótesis de intención para cada cambio, también lo que Ricardo no enlistó. Antes de comparar se establece de qué versión desciende la suya ([[task-52]], propuesta de linaje pendiente de Ricardo). De ese diff sale qué preguntas respondió con el mouse; lo que siga abierto se le pregunta con su explicación completa ([[global:fb-1100]]). El turno aplica además las reglas generales de [[adr-0018]] que el generador todavía no sabe: trazo para la vuelta tras el nodo donde se juntan las escaleras del banco (largo por confirmar con Ricardo; sus trazos en las versiones -rick rondan 1 m: entre 0,87 y 1,73 m), pasillo en la mitad opuesta del pabellón a la escalera, y contexto con jardines y estacionamientos.

## Criterios de aceptación

- [ ] Diff de la 03-rick contra la 02-claude presentado a Ricardo
- [ ] Nombre del contorno «Viaducto»
- [ ] Versión aprobada por Ricardo
