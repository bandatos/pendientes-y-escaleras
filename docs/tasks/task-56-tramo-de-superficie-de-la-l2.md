---
type: task
id: task-56
title: "Tramo de superficie de la L2 (Nativitas a San Antonio Abad y Ermita L2): diff de las versiones de Ricardo y afinación hasta aprobar"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Tramo de superficie de la L2 (Nativitas a San Antonio Abad y Ermita L2): diff de las versiones de Ricardo y afinación hasta aprobar

Seis estaciones hermanas del componente `tlalpan-surface` generadas el 27 de octubre de 2026 y revisadas por Ricardo en JOSM el 30 ([[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]). Cinco tienen versión de Ricardo encima de la nuestra; Ermita no. Ricardo decidió cerrar la sesión antes de los turnos de diff, que son el arranque de la siguiente: un `station-tracer` por estación, en paralelo, cada uno con el diff de la versión de Ricardo contra la nuestra como primer entregable.

Estado de cada una en su task hija. Lo común:

- Reglas del componente vigentes en [[adr-0017]]; reglas generales nuevas en [[adr-0018]] (las tres de trazo se aplican a mano en estos turnos hasta que el generador las aprenda).
- Ninguna tiene copia `-pub`. Con estas seis llegan a doce las estaciones de mapeo manual, el tope que fijó Ricardo en [[task-11]] antes de pasar a política de import: avisarle antes de publicar.
- Se publican sin elevadores ([[task-71]]) y sin tocar las relaciones `stop_area` ([[task-51]]).
- Cada estación tiene sus hechos en `.claude/skills/station-tuning/references/estaciones/<slug>.md`.
- Concurrencia: en la sesión del 27 seis trazadores escribieron a la vez en `data/osm/templates/tlalpan-surface.json`; no se perdió nada, pero la siguiente ronda en paralelo debe dar a cada trazador una copia privada de la plantilla y que el coordinador fusione los bloques ([[global:fb-1103]]).

## Criterios de aceptación

- [ ] Las seis estaciones tienen versión aprobada por Ricardo o un motivo explícito para no publicarse todavía (Villa de Cortés espera visita)
- [ ] Lo que enseñaron quedó en la plantilla, el generador o las referencias del skill

## Notas de trabajo

- 30 de octubre de 2026: los scripts que armaron Nativitas 02, San Antonio Abad 02, Ermita 02 y Villa de Cortés 01 están en `.claude/scratch/l2-2026-10-27/`, ignorado por git. Ricardo decide si se versionan junto a cada estación o quedan en scratch sin reproducibilidad.
