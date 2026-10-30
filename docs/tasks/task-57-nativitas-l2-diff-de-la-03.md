---
type: task
id: task-57
title: "Nativitas (L2): diff de la 03-rick contra la 02-claude y afinación"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Nativitas (L2): diff de la 03-rick contra la 02-claude y afinación

Carpeta `data/osm/l2-nativitas/`. Marco de la 01: rumbo 8,5°, ancla 19.3795464,-99.1401985, `0200L2-NATIVITAS --family tlalpan-surface`. Hechos en `.claude/skills/station-tuning/references/estaciones/nativitas.md`.

## Versiones

- `nativitas-01-claude.osm`: generada tal cual; falla la validación (la entrada de OSM 5156348346 queda suelta a 1,06 m de la puerta).
- `nativitas-02-claude.osm`: la nuestra para comparar. Valida y pasa `check_station_osm_live`. Lleva a mano, con script (`.claude/scratch/l2-2026-10-27/nativitas-post.py`, fuera del versionado), el borrado del puente peatonal de OSM 43763069 y la conservación de los nodos 5156348365/66 que usa el jardín 1275816500: regenerar los pierde ([[task-66]], [[task-65]]).
- `nativitas-03-rick.osm`: la de Ricardo, 30 de octubre.

## Preguntas y respuestas de Ricardo

- **P1, fondo del pabellón poniente** (el KML lo mete unos 7 m en el jardín `landuse=grass` 1275816500). Respondida: «hay un árbol en ese jardín muy grande que desde la vista satelital parece que el jardín abarca más de lo que realmente abarca, aún así acorté un poco el área, no pude hacer más chico el jardín porque no aparece». El jardín es más chico de lo que parece; el recorte que hizo está en la 03 y el diff lo mide. El jardín no venía en el archivo porque el contexto no trae `landuse` ([[task-65]]). Ricardo quiso achicar el jardín 1275816500 y no pudo porque no venía en el archivo; con el contexto ampliado se decide si se edita.
- **P2, `layer=2` del contorno** (way 531159102). Respondida: «Sí quitar». Pendiente de aplicar en el turno.
- Observación de Ricardo sobre esta estación (oriente y poniente): falta el «trazo para la vuelta» tras el nodo donde se juntan las escaleras del banco ([[adr-0018]]).
- Abierta, sin respuesta: el connector de E-01 va 6,5 m a la punta 554206757 de la banqueta 864674193; la alternativa es uno perpendicular de unos 2 m soldado a mitad de banqueta ([[task-70]]).

## Cómo arranca el turno

El primer entregable es el diff completo de la versión de Ricardo contra la nuestra, por `note:pathway_id`/`note:stop_id` y con el área vértice a vértice en el marco local de la 01 (skill `station-tuning`, «Herramientas del turno»), con hipótesis de intención para cada cambio, también lo que Ricardo no enlistó. Antes de comparar se establece de qué versión desciende la suya ([[task-52]], propuesta de linaje pendiente de Ricardo). De ese diff sale qué preguntas respondió con el mouse; lo que siga abierto se le pregunta con su explicación completa ([[global:fb-1100]]). El turno aplica además las reglas generales de [[adr-0018]] que el generador todavía no sabe: trazo para la vuelta tras el nodo donde se juntan las escaleras del banco (largo por confirmar con Ricardo; sus trazos en las versiones -rick rondan 1 m: entre 0,87 y 1,73 m), pasillo en la mitad opuesta del pabellón a la escalera, y contexto con jardines y estacionamientos.

## Criterios de aceptación

- [ ] Diff de la 03-rick contra la 02-claude presentado a Ricardo
- [ ] `layer=2` quitado del contorno 531159102
- [ ] Versión aprobada por Ricardo
