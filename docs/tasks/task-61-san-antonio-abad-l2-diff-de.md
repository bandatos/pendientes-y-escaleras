---
type: task
id: task-61
title: "San Antonio Abad (L2): diff de la 03-rick contra la 02-claude, sin el andador de la Calzada Flotante"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-64]]", "[[task-21]]"]
---

# San Antonio Abad (L2): diff de la 03-rick contra la 02-claude, sin el andador de la Calzada Flotante

Carpeta `data/osm/l2-san-antonio-abad/`. Marco de la 01: rumbo 8,5°, ancla 19.4160322,-99.1345485, `0200L2-SANANTONIO`. Hechos en `.claude/skills/station-tuning/references/estaciones/san-antonio-abad.md`. La estación no tiene bloque en la plantilla: la 02 se armó con script desde la 01 (`.claude/scratch/l2-2026-10-27/san-antonio-abad-make02.py`, fuera del versionado).

## Versiones

- `san-antonio-abad-01-claude.osm`: generada; da de baja el nodo 13389920428, que usa el estacionamiento 1429237668 (la consulta en vivo lo bloquea; el contexto no trae estacionamientos, [[task-65]]).
- `san-antonio-abad-02-claude.osm`: la nuestra para comparar. Valida y pasa la consulta en vivo.
- `san-antonio-abad-03-rick.osm`: la de Ricardo, 30 de octubre.

## Lo propio de la estación

- Tres accesos: E-01, E-02 y E-03 «Acceso Calzada Flotante» de nivel 1, que llega directo al vestíbulo. La referencia de familias dice cuatro; la base, el tablero y la imagen sostienen tres (corregir la referencia en [[task-8]]).
- Las dos eléctricas de acceso quedaron de un solo sentido tras la corrección en Miró del 27 de octubre ([[adr-0017]]).
- El brief del trazador ponía E-03 al norte; Chabacano está unos 760 m al sur y el trazador lo puso al sur ([[global:fb-1101]]).

## Preguntas y respuestas de Ricardo

- **P9, la Calzada Flotante.** Respondida en parte y movida a sesión aparte ([[task-64]]). En esta estación Ricardo «moví el acceso hasta el sur del área de la estación» en la 03.
- **P10, pabellón oriente tomado del edificio del catastro** (way 1429237676, SIGCDMX, desfase menor a 1 m con el KML, con la puerta E-02 insertada en su muro). Respondida: «P10. Lo veo bien».

**Pregunta a Ricardo, que no le llegó:** ¿hay un cuarto acceso? La referencia de familias dice cuatro; la base, el tablero y la imagen Esri de febrero de 2025 sostienen tres, pero el pabellón oriente está tapado por la sombra de un edificio alto y el trazador no lo descarta del todo de ese lado.

## Cómo arranca el turno

El primer entregable es el diff completo de la versión de Ricardo contra la nuestra, por `note:pathway_id`/`note:stop_id` y con el área vértice a vértice en el marco local de la 01 (skill `station-tuning`, «Herramientas del turno»), con hipótesis de intención para cada cambio, también lo que Ricardo no enlistó. Antes de comparar se establece de qué versión desciende la suya ([[task-52]], propuesta de linaje pendiente de Ricardo). De ese diff sale qué preguntas respondió con el mouse; lo que siga abierto se le pregunta con su explicación completa ([[global:fb-1100]]). El turno aplica además las reglas generales de [[adr-0018]] que el generador todavía no sabe: trazo para la vuelta tras el nodo donde se juntan las escaleras del banco (largo por confirmar con Ricardo; sus trazos en las versiones -rick rondan 1 m: entre 0,87 y 1,73 m), pasillo en la mitad opuesta del pabellón a la escalera, y contexto con jardines y estacionamientos.

## Criterios de aceptación

- [ ] Diff de la 03-rick contra la 02-claude presentado a Ricardo
- [ ] La estación tiene bloque en la plantilla que reproduce lo aprobado, o queda dicho por qué no
- [ ] Versión aprobada por Ricardo, con el andador de la Calzada Flotante resuelto en task-64 o explícitamente fuera
