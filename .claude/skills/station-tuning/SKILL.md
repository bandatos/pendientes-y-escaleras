---
name: station-tuning
description: Ciclo de afinación de una estación del Metro en JOSM: versiones .osm entre analista, coordinador y Ricardo, tres capas de conocimiento (general, componente, estación) y la imagen Esri. Actívalo al generar, revisar o afinar el trazo de una estación.
status: provisional
metadata:
  rules: 2026-09-05
  type: domain
  reader: both
---

# Afinación de estaciones

Este skill dice cómo se trabaja una estación desde su primer trazo generado hasta el archivo que Ricardo aprueba, y dónde vive lo que cada estación enseña. El código es la fuente de cómo se genera y se dibuja: el generador (`api/stop/management/commands/export_station_osm.py` y `api/utils/osm/`) y las plantillas de `data/osm/templates/`. El criterio vive en este skill y sus referencias, y manda: si choca con el código, no conviven; se corrige uno, se pregunta a Ricardo o se abre una tarea. Los comandos exactos, la estructura de carpetas y el esquema de plantilla están en `data/osm/README.md`; el catálogo de etiquetas, en `api/utils/osm/tags.py`; el porqué del catálogo y de la geometría, en los ADR de convenciones de `docs/decisions/`.

Es provisional porque el ciclo se ha corrido completo en una sola estación. Se gradúa cuando dos o tres estaciones más hayan cerrado con él y cuando la revisión de bitácoras que Ricardo planea haya mostrado qué briefs funcionaron; lo que ahí se vea entra al agente `station-tracer`, que es quien ejecuta los turnos.

## Libertad primero

Las reglas de este skill y de sus referencias orientan; no son pasos cerrados. Quien ejecuta un turno piensa y aplica las reglas a la vez, con libertad para cambiar lo que haga falta cuando lo que hay en OpenStreetMap, en la imagen satelital o en la geometría de la estación contradice una regla: se respeta lo que hay, se reporta el cambio y se propone adaptar la regla, no al revés. Lo único fijo es la regla del área (`references/general.md`).

No hay «pausa». Una duda importante sin salida clara se deja escrita como duda para el coordinador, que la lleva a Ricardo; mientras tanto se implementa algo provisional marcado como provisional, o no se implementa, pero nunca se fuerza una solución sabiendo que no tendrá sentido. Cuando hay una salida clara y además otras alternativas viables, se implementa la clara y se avisan las otras para que Ricardo valide o cambie. Lo que es de Ricardo siempre le llega.

## El ciclo

La versión 01 la produce el generador desde la plantilla. A partir de ahí, las versiones se encadenan sobre el archivo `.osm`, no sobre la plantilla: cada turno parte de la versión anterior y produce la siguiente. La plantilla aprende al cierre, no turno a turno; la prueba de que aprendió es regenerar la estación con `--out` fuera de su carpeta, para no meter un archivo en la cadena de versiones, y comparar contra el archivo aprobado.

El primer turno es de análisis y trazo: un agente lee la estación completa (su área, el contexto de OSM alrededor, la imagen satelital, las estaciones hermanas y cómo se resolvieron), intenta identificar de qué componentes está hecha y qué tiene de peculiar o de faltante (el trazo del área, un edificio que ya existe en OSM, entradas que hay que alinear), traza lo que alcanza a entender y reporta lo hecho y lo dudoso. El coordinador filtra ese reporte, corrige lo que puede, y le explica a Ricardo en lenguaje claro qué encontró raro, qué decisiones hay y qué debe revisar en JOSM. Ricardo responde con texto y a veces editando el `.osm` en JOSM y subiendo una versión nueva; a partir de su segundo turno edita sobre todo detalles: ubicación exacta de accesos, trazos mínimos, cosas que a veces son de esa estación y a veces se generalizan. Con eso, un agente nuevo hace la versión siguiente y vuelve a reportar. El ciclo se repite hasta que Ricardo queda satisfecho. Antes de presentarle cada versión, el coordinador itera con turnos de `station-tracer` hasta que el resultado quede y haga sentido: Ricardo revisa el resultado, no los intentos.

El cierre es aprender: lo que la estación enseñó se escribe en las referencias de este skill, en la plantilla o en el generador, para que la siguiente estación salga mejor desde el primer saque. Si la sesión cambió reglas que alcanzan a otras estaciones, el coordinador pregunta a Ricardo si quiere aplicarlas a la última versión de las que correspondan (las del mismo componente o todas) y genera para cada una un turno nuevo que él revisa.

Cuando la ventana de contexto se acerca a 250 mil tokens, el coordinador se lo dice a Ricardo y él decide si la revisión sigue en una sesión nueva; el estado queda escrito para el relevo en la tarea de la estación, enlazada desde su archivo en `references/estaciones/`.

## Lo que siempre le llega a Ricardo

Solo lo que aporta: lo que Ricardo no sabe y le sirve para decidir o revisar. Lo que se revisó y no produjo cambio, o lo que él ya sabe porque lo hizo o lo dijo («no tocaste elementos de OSM», «el orden de las escaleras estaba bien»), no se reporta; el silencio sobre un rubro significa que no hubo nada.

- **Todo el diff, no solo lo que él enlistó.** Cuando Ricardo sube una versión, su mensaje cuenta parte de lo que hizo. El turno compara la versión completa contra la anterior y le presenta también lo que no mencionó, con una hipótesis de si fue intencional. Ricardo valida o corrige cada caso; a él le interesa justamente encontrar lo que no vio.
- **Cada cambio a un elemento que viene de OSM**, con la hipótesis de intención: algunos son obvios, otros no, y adivinar está bien, pero él confirma uno por uno.
- **La capa de cada hallazgo.** Cada cosa que un turno cambia o propone se clasifica como general (todas las estaciones), de componente (las que comparten ese andén o esa entrada) o de la estación. El coordinador intuye la capa; Ricardo la valida.
- **Lo que se revirtió de oficio**: la circulación por la derecha y el orden de las escaleras en un conjunto de escaleras paralelas, que el turno restaura sin preguntar (`references/general.md`, «Escaleras y circulación»).
- **Las dudas sin salida clara, las implementaciones provisionales y las alternativas** a lo que se resolvió por la vía clara, cada una en su lugar del reporte.

## Las tres capas y dónde viven

Un número que el generador consume vive en JSON; un criterio vive en prosa; cada prosa nombra su JSON. Con esa regla, las tres capas quedan así:

- **General** (toda estación): `references/general.md`. Los ADR de convenciones son la historia del porqué; la referencia es el estado vigente en prosa.
- **Componente**: `references/componentes/`, un archivo por componente, cada uno apuntando a su bloque de `data/osm/templates/`. La unidad es el componente (un tipo de andén, un tipo de entrada o cascada), no la «familia»: en la Línea 7 hay estaciones con el mismo andén y entradas distintas, y una estación se arma eligiendo componentes más sus hechos propios. Hoy las plantillas todavía son una pieza por familia; la partición real del JSON en componentes está pendiente en task-38.
- **Estación**: `references/estaciones/<slug>.md` para lo que un lector necesita saber de esa estación, y la carpeta `data/osm/<línea>-<slug>/` para sus archivos. Los hechos por estación que el generador consume van en un bloque por estación dentro de la plantilla.

Al abrir una estación se leen `general.md`, los componentes que la forman y su archivo de estación si existe; los de las hermanas, cuando haga falta ver cómo se resolvió algo.

## Carpetas y versiones

La carpeta de cada estación (`data/osm/<línea>-<slug>/`), la numeración de versiones `<slug>-NN-<autor>.osm` y lo demás que vive ahí están en `data/osm/README.md`, «Archivos». Para el criterio importa que ninguna versión se sobrescribe y que las medidas se toman en el marco local de la versión 01, porque JOSM borra la cabecera que lo declara.

## Imagen satelital

Esri World Imagery es la fuente permitida y es la misma capa que JOSM muestra por defecto. La escena es de 0,5 m nativos resampleada y su exactitud absoluta declarada es de 8,47 m: la imagen sirve para leer la estación (qué edificio existe, dónde está la explanada, por dónde salen las escaleras), no para fijar coordenadas; la alineación métrica sigue siendo contra OSM y el KML. Los compuestos con KML, OSM y nuestros trazos encima los produce `compose_station_imagery` (uso en `data/osm/README.md`) en la carpeta `sat/` de la estación, y nunca se versionan: la licencia permite calcar, no redistribuir. Cuando algo se suba a OSM, el changeset lleva `imagery_used=Esri World Imagery`. Bing y Mapbox piden llave; si una estación deja duda en Esri, Ricardo compara con Bing dentro de JOSM.

## Herramientas de cada turno

El primer entregable de un turno que recibe una versión de Ricardo es la comparación contra la anterior por etiquetas de traza (`note:pathway_id`, `note:stop_id`) y por tipo de elemento, con el área comparada vértice a vértice en el marco local. `diff_station_osm` sirve para los trazos del grafo, no para el área ni para los objetos de OSM (su límite, en `data/osm/README.md`). Las medidas se toman en el marco local de la estación (rumbo y ancla de la versión 01), nunca en grados. Los ajustes finos con herramienta son bienvenidos y son la ventaja del agente sobre la edición a ojo: ortogonalizar, igualar anchos, centrar un pasillo entre sus muros; lo que no se hace es agregar cientos de nodos donde Ricardo dejó una curva de pocos.
