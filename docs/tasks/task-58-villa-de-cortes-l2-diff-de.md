---
type: task
id: task-58
title: "Villa de Cortés (L2): diff de la 03-rick, reglas del poniente y visita física antes de publicar"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Villa de Cortés (L2): diff de la 03-rick, reglas del poniente y visita física antes de publicar

Carpeta `data/osm/l2-villa-de-cortes/`. Marco de la 01: rumbo 8,3°, ancla 19.3875836,-99.1389625, sin `--mirror`, `0200L2-VILLADECORT`. Hechos en `.claude/skills/station-tuning/references/estaciones/villa-de-cortes.md`.

## Versiones

- `villa-de-cortes-01-claude.osm`: no sale del command; salió de un envoltorio fuera del repo (`.claude/scratch/l2-2026-10-27/villa-de-cortes-gen_nolobe.py`, fuera del versionado) que parchea `measure_arm` en memoria, porque cada brazo es un solo rectángulo sin lóbulo ([[task-68]]).
- `villa-de-cortes-02-claude.osm`: la nuestra para comparar. La 01 más bajas a mano: el puente peatonal 221926316 y su nodo 2309054744, y el edificio 1488931042 (`building:levels=8`, de un mapeador de marzo de 2026 sobre Bing) con sus nodos 13648121863–67.
- `villa-de-cortes-03-rick.osm`: la de Ricardo, con «muchos cambios», textual: «De Villa de cortés hice muchos algunos cambios, revisémoslos juntos».

## Lo propio de la estación

- **Brazo sin lóbulo.** Puente y pabellón son un solo rectángulo del mismo ancho de cada lado; el generador falla en el lado +v y en el −v encuentra un lóbulo falso.
- **Lado poniente, lectura de Ricardo** (30 de octubre), textual: «En villa de cortés hay una excepción de lado poniente y las escaleras son "paralelas a las vías", luego hay una ampliación rara que hicieron donde supongo (tengo que comprobarlo y hasta que no lo comprobemos no podemos subir el pub de esta estación) están los torniqutes en el pasillo por encima de la avenida». Contradice la propuesta de «brazo sin lóbulo con banco sobre el eje» al menos para ese lado.
- **No se publica sin visita física** ([[task-63]]). Ricardo: «hicieron remodelación reciente y es una estación a la que requerimos ir físicamente para poder publicar en OSM». Sin `-pub` hasta entonces.
- La huella de OSM (contorno 217340069 y entradas) la redibujó otro mapeador en marzo de 2026 sobre Bing y está corrida 3 a 12 m respecto de Esri y del KML.
- La franja del KML mide 13,98 m; el techo en Esri y la huella de OSM dan 11–11,5 m (dato, sin tocar).

## Preguntas y respuestas de Ricardo

- **P3, regla «brazo sin lóbulo» para el generador.** Sin respuesta en texto; su lectura del poniente la contradice. Confirmar con el diff qué hizo en cada lado antes de escribir la regla ([[task-68]]).
- **P4, lado de la puerta poniente.** Respondida: «P4. está bien colocada la salida». Confirmar con el diff si se refiere a la posición de la 02 (muro norte, donde el otro mapeador puso su entrada) o a la que él dejó en la 03. La peatonal de 2013, 232080737, quedó como cabo suelto dentro del pabellón.
- **P5, borrar el edificio 1488931042 y adoptar las entradas 13653654624 y 13648121868 movidas 14,4 y 12,2 m** (más que el tope de unos 10 m). Sin respuesta en texto; el diff dice si lo conservó o lo dejó borrado.
- **P8, nombre del contorno.** Respondida: «Villa de Cortés», sin «Metro» ([[adr-0018]]). Pendiente de aplicar.

## Cómo arranca el turno

El primer entregable es el diff completo de la versión de Ricardo contra la nuestra, por `note:pathway_id`/`note:stop_id` y con el área vértice a vértice en el marco local de la 01 (skill `station-tuning`, «Herramientas del turno»), con hipótesis de intención para cada cambio, también lo que Ricardo no enlistó. Antes de comparar se establece de qué versión desciende la suya ([[task-52]], propuesta de linaje pendiente de Ricardo). De ese diff sale qué preguntas respondió con el mouse; lo que siga abierto se le pregunta con su explicación completa ([[global:fb-1100]]). El turno aplica además las reglas generales de [[adr-0018]] que el generador todavía no sabe: trazo para la vuelta tras el nodo donde se juntan las escaleras del banco (largo por confirmar con Ricardo; sus trazos en las versiones -rick rondan 1 m: entre 0,87 y 1,73 m), pasillo en la mitad opuesta del pabellón a la escalera, y contexto con jardines y estacionamientos.

## Criterios de aceptación

- [ ] Diff de la 03-rick contra la 02-claude presentado a Ricardo
- [ ] P3 y P5 resueltas, con lo que contestó en su edición
- [ ] Nombre del contorno «Villa de Cortés»
- [ ] Versión aprobada por Ricardo después de la visita física (task-63)
