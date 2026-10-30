---
type: task
id: task-59
title: "Xola (L2): diff de la 02-rick contra la 01-claude y lógica de conexión a la banqueta"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-29]]"]
---

# Xola (L2): diff de la 02-rick contra la 01-claude y lógica de conexión a la banqueta

Carpeta `data/osm/l2-xola/`. Marco de la 01: rumbo 8,7°, ancla 19.395197,-99.137804, `0200L2-XOLA`. Hechos en `.claude/skills/station-tuning/references/estaciones/xola.md`. Sucede a la parte de Xola de [[task-29]], cerrada.

## Versiones

- `xola-01-claude.osm`: generada; valida y pasa la consulta en vivo. No hubo 02 nuestra.
- `xola-02-rick.osm`: la de Ricardo, 30 de octubre.

## Lo propio de la estación

- Es la única de las seis con un lóbulo ancho (el poniente, 20,9 × 13,7 m con el área corregida): banco a lo largo de la calzada con 3,43 m entre ejes (fondo/4), acortado a 9,51 m para dejar el pie a 3 m del muro de la punta.
- El anillo del KML se cruzaba a sí mismo por dos vértices invertidos; el bloque de la estación los cambia por el punto de cruce (4,35, −28,44), 0,7 m².
- Entradas de OSM 5160032503 (poniente, `wheelchair=yes`, movida 9,6 m por la regla del lóbulo ancho) y 5160032504 (oriente, 0,6 m), enlazadas con `osm_node` + `relocate: true`.
- Índice de las escaleras del andén asignado por la convención de Portales sin comparar `note:miro_id` contra el tablero de Miró (pendiente heredado de [[task-29]]).
- Tres elevadores en el CSV crudo, fuera de esta edición ([[task-71]]).

## Preguntas y respuestas de Ricardo

- **P6, puerta poniente.** Ricardo la recolocó en la 02-rick y pregunta: «P6. ya la recoloqué, es más o menos lo que se esperaba?». El diff lo contesta (posición contra la de OSM, u 7,95, y contra la de la regla, u 17,54).
- **P7, banco poniente de 9,5 m o 12,2 m** (cabecera hasta el eje del brazo). Sin respuesta en texto; el diff dice qué hizo.
- **P8, nombre del contorno** (way 217340068, «Metro Xola»). Respondida: «P8. Sí»: pasa a «Xola». Pendiente de aplicar.
- **Pasillo que agregó Ricardo**, textual: «Xola solo requirió un pasillo, ya que casi siempre antes de cualquier escalera desde la entrada (al menos en la L2) existe un pasillo en la mitad opuesta a donde está la escalera». Regla general en [[adr-0018]].
- **Conexión a la banqueta**, textual: «Hay algo que no estoy entendiendo bien de Xola y en general es la regla para conectar la banqueta (solo cuando exista), siento que no se está usando una buena lógica, por ejemplo en el lado poniente, revisemos eso a la luz de los cambios en mi versión». La 01 dejó E-01 → nodo 5580858041 (4,1 m) y E-02 → 8319476398 (5,0 m). Se revisa en el diff y alimenta [[task-70]].

**Lectura preliminar del coordinador, a confirmar en el diff:** en `xola-02-rick.osm` E-01 (5160032503) quedó en u ≈ 5,7, es decir donde OSM la tenía (u 7,95) corrida unos 2 m hacia el brazo: en la práctica, la opción 2 de P6.

## Cómo arranca el turno

El primer entregable es el diff completo de la versión de Ricardo contra la nuestra, por `note:pathway_id`/`note:stop_id` y con el área vértice a vértice en el marco local de la 01 (skill `station-tuning`, «Herramientas del turno»), con hipótesis de intención para cada cambio, también lo que Ricardo no enlistó. Antes de comparar se establece de qué versión desciende la suya ([[task-52]], propuesta de linaje pendiente de Ricardo). De ese diff sale qué preguntas respondió con el mouse; lo que siga abierto se le pregunta con su explicación completa ([[global:fb-1100]]). El turno aplica además las reglas generales de [[adr-0018]] que el generador todavía no sabe: trazo para la vuelta tras el nodo donde se juntan las escaleras del banco (largo por confirmar con Ricardo; sus trazos en las versiones -rick rondan 1 m: entre 0,87 y 1,73 m), pasillo en la mitad opuesta del pabellón a la escalera, y contexto con jardines y estacionamientos.

## Criterios de aceptación

- [ ] Diff de la 02-rick contra la 01-claude presentado a Ricardo, con P6 y P7 resueltas
- [ ] Lógica de conexión a la banqueta revisada con Ricardo sobre su versión
- [ ] Nombre del contorno «Xola»
- [ ] Índice ↔ posición de las escaleras del andén comprobado con `note:miro_id` contra Miró
- [ ] Versión aprobada por Ricardo
