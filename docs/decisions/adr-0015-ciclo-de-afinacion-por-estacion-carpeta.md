---
type: decision
id: adr-0015
title: "Ciclo de afinación por estación: carpeta por estación, versiones encadenadas sobre el .osm, imagen Esri y un skill con su agente"
state: accepted
date: 2026-10-22
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-10-22-sesion-ciclo-de-afinacion-y-san-joaquin]]", "[[task-36]]"]
affects: [".claude/skills/station-tuning/", ".claude/agents/station-tracer.md", "api/utils/osm/layout.py", "api/stop/management/commands/export_station_osm.py", "api/stop/management/commands/compose_station_imagery.py", "api/utils/osm/imagery.py", "data/osm/README.md", ".gitignore"]
related: ["[[adr-0014]]", "[[task-26]]", "[[task-29]]"]
---

# Ciclo de afinación por estación: carpeta por estación, versiones encadenadas sobre el .osm, imagen Esri y un skill con su agente

## Contexto y planteamiento del problema

Hasta el 21 de octubre de 2026 cada estación vivía como un archivo plano `data/osm/<slug>.osm` que el generador sobrescribía, las ediciones a mano de Ricardo quedaban en `~/Descargas` o en la carpeta de referencia de `data/osm/` (hoy versiones `-rick` en la carpeta de cada estación), y la lógica de los turnos de afinación estaba repartida entre el `CLAUDE.md`, dos feedback globales y varias tareas. Ricardo pidió el 22 de octubre una lógica de trabajo conjunta que oriente cada estación nueva:

> lo que quiero es algo que pueda orientar las sesiones, no pasos estrictos que quiten libertad e impidan soluciones creativas a los problemas

> Creo que lo ideal es que cada estación tenga su carpeta dentro de data/osm, el nombre de la carpeta debe tener la línea y luego la estación, cada archivo debe tener el nombre de la estación seguido de la versión de la que se trate

## Opciones consideradas

- **Dónde avanza cada turno.** (a) Cada turno edita el `.osm` y la plantilla aprende al cierre; (b) cada turno cambia la plantilla y regenera, con lo que las ediciones a mano de Ricardo se pierden salvo que se traduzcan a parámetros turno por turno. [[task-26]] pedía (b) en espíritu («afinar la plantilla, no el XML»).
- **Dónde vive la lógica.** Solo un skill; skill más agente de proyecto; agente global.
- **Dónde viven las tres capas de conocimiento** (general, componente, estación): todo el criterio en prosa en el skill y todo número del generador junto a los datos; o todo bajo `data/osm/`.
- **Imagen.** Esri World Imagery, Bing (pide llave), Mapbox (prohíbe descarga automatizada).

## Resultado

- **Carpeta por estación** `data/osm/<línea>-<slug>/` con versiones `<slug>-NN-<rick|claude>.osm`, contador corrido por archivo sin importar el autor, la generada siempre `01-claude`; dentro, `context.json`, `preview/` y `sat/` (ignorada). El generador escribe por defecto la siguiente versión libre. — Ricardo en la forma; sesión en la mecánica.
- **Opción (a):** las versiones se encadenan sobre el `.osm`; la plantilla aprende al cierre, y la prueba es regenerar fuera de la carpeta y comparar contra el archivo aprobado. — Ricardo.
- **Skill de proyecto `station-tuning` más agente de proyecto `station-tracer`**, ambos `status: provisional`; el agente estabiliza el brief para que no dependa de cada coordinador, y se afina después con la revisión de bitácoras. — Ricardo.
- **Capas:** criterio en prosa en `references/` del skill (general, componentes, estaciones); números en JSON; cada prosa nombra su JSON. La unidad es el componente (un tipo de andén, un tipo de cascada o entrada), no la familia, porque hay estaciones con el mismo andén y entradas distintas. — Ricardo.
- **Esri World Imagery** es la fuente de imagen: sin llave, zoom real 19, exactitud absoluta declarada de 8,47 m, así que sirve para leer la estación y no para medir. El command `compose_station_imagery` compone imagen, KML, contexto y trazo en `sat/`; los compuestos nunca se versionan. Ricardo comparó con Bing en JOSM: «nos quedamos con Esri, funciona bien y es suficiente».
- **Reglas de conducta del ciclo**, escritas en el skill: el criterio manda sobre la mecánica; una duda sin salida clara se lleva a Ricardo o se implementa algo provisional marcado como tal, nunca se fuerza; con salida clara y alternativas se implementa la clara y se avisan las otras; cada reporte separa lo general, lo del componente y lo de la estación; se lee el diff completo de cada versión de Ricardo y se le presenta lo que no enlistó, con hipótesis de intención; solo se reporta lo que aporta.

## Consecuencias

- **Bueno:** las ediciones a mano quedan versionadas y encadenadas; un agente con contrato estable corre los turnos; la imagen entra al ciclo sin violar la licencia.
- **Malo:** la plantilla queda atrás de las versiones hasta que el cierre la ponga al día (tarea de aprendizaje de la plantilla); la estructura de carpetas y los comandos viven solo en `data/osm/README.md`; el skill apunta ahí y conserva el criterio, así que un cambio de carpetas toca el README y, si cambia el criterio, el skill.
