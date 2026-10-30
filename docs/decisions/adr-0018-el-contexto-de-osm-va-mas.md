---
type: decision
id: adr-0018
title: El contexto de OSM va más allá del área con jardines y estacionamientos, el banco lleva trazo para la vuelta, y en una estación de correspondencia el nodo de estación no se mueve y las áreas de las dos líneas colindan sin hueco
state: accepted
date: 2026-10-30
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
affects: ["api/stop/management/commands/export_station_osm.py", "api/utils/osm/graph.py", "api/utils/osm/overpass.py", "api/utils/osm/builder.py", "data/osm/templates/tlalpan-surface.json", ".claude/skills/station-tuning/references/general.md"]
related: ["[[adr-0011]]", "[[adr-0016]]", "[[task-51]]"]
---

# El contexto de OSM va más allá del área con jardines y estacionamientos, el banco lleva trazo para la vuelta, y en una estación de correspondencia el nodo de estación no se mueve y las áreas de las dos líneas colindan sin hueco

## Contexto y planteamiento del problema

Revisar en JOSM las seis estaciones de la L2 de superficie generadas el 27 de octubre ([[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]) le hizo ver a Ricardo cosas que no son de una estación sino de todas, y Ermita, la primera estación de correspondencia que se traza, obligó a decidir cómo convive el trazo de una línea con la otra. Además, dos estaciones propusieron bajas de nodos que OSM rechazaba porque el contexto descargado no traía los jardines ni los estacionamientos que comparten esos nodos.

## Criterios de decisión

- Que el archivo muestre lo que hay alrededor de la estación, para ver los choques antes de subir.
- Que la circulación dibujada se parezca a la que se camina.
- En una estación de correspondencia, no editar en OSM lo que es de la otra línea o de la estación entera, y no dejar huecos entre las dos.
- Adoptar lo que OSM ya tiene antes de dibujar algo paralelo ([[adr-0011]]).

## Opciones consideradas

Salvo donde se dice, no se evaluaron alternativas: son reglas que Ricardo dictó al revisar.

- **Hueco entre las áreas de L2 y L12 en Ermita:** (a) dejar el hueco de 6 m que sale del KML y resolverlo al trazar L12 (recomendación del coordinador); (b) estirar el área para que las dos colinden.
- **El trasbordo que OSM ya tiene en Ermita** (way 536525798, dibujado como túnel a nivel de calle): (1) dejarlo y agregar el nuestro encima; (2) adoptarlo como nuestro pasillo; (3) no tocarlo hasta trazar L12.
- **Exportar Ermita L2:** (1) filtro por línea en el generador; (2) reasignar el `parent_station` de los ocho stops de L2 por command; (3) sacar Ermita de la sesión.
- **Elevadores que el CSV crudo registra y la base no tiene:** (1) publicar sin ellos y sumarlos en una edición aparte; (2) cargarlos antes.

## Resultado

**Reglas generales del trazo** (todas las estaciones; pendientes en el generador salvo donde se dice):

- **El contexto va más allá del área e incluye `landuse`, `leisure` y `natural`** (jardines, estacionamientos) con un radio mayor, para verlos en el archivo. Si se editan es otra pregunta: Ricardo quiso achicar el jardín 1275816500 de Nativitas y no pudo porque no venía en el archivo. Ricardo, textual: «tengo la sensación de que hay que ampliar el radio alrededor de la estación (no veo claramente el jardín como elemento), siento que debería ser una regla casi global, ir más allá del área de la estación, porque nos permite ver este tipo de situaciones». Trabajo en [[task-65]].
- **Trazo para la vuelta.** Ricardo, textual: «una vez que se juntan las escaleras paralelas en un nodo, debería existir un pequeño trazo lineal en la misma dirección y luego dar vuelta, en lugar de que de allí directamente se dibuje el pasillo perpendicular». El largo queda por confirmar con Ricardo: el coordinador propuso 2 m («salvo que digas otra cosa») y Ricardo no respondió; en sus versiones -rick el tramo mide entre 0,87 y 1,73 m (Nativitas 1,10/1,29; Viaducto 0,99/1,73; Xola 0,87; Villa de Cortés 0,97 y 0,88/1,18), así que sus trazos rondan 1 m. Se aplica a los bancos de las seis estaciones nuevas; a General Anaya y Portales solo si Ricardo lo pide. Trabajo en [[task-69]].
- **En la L2, el pasillo va en la mitad opuesta del pabellón a la escalera.** Ricardo, textual: «casi siempre antes de cualquier escalera desde la entrada (al menos en la L2) existe un pasillo en la mitad opuesta a donde está la escalera». En el lóbulo ancho el generador ya lo hace (el banco ocupa la mitad del fondo que no recorre quien entra); lo pendiente es el lóbulo hondo ([[task-69]]).

**Estaciones de correspondencia:**

- **Se exportan por línea** con `--line` (opción 1). Ricardo: «P2. 1». Implementado.
- **El nodo `railway=station` único de la correspondencia no se mueve hacia la línea que se trabaja** (`station_node: null` en el bloque de la estación). En Ermita es el nodo 12679525779, miembro del `stop_area` de L2 y puesto en L12; el coordinador lo resolvió así sin pregunta, por ser una edición equivocada moverlo 207 m, y lo presentó a Ricardo, que no lo objetó.
- **Las áreas de las dos líneas comparten nodos, sin hueco** (opción b). Ricardo, textual: «P12. No dejar huecos, es mejor modificar el área tantito, cualquiera de las dos, pero deberían estar colindando los nodos de las dos áreas, sin ningún hueco». En Ermita el área de L2 se estira a los nodos 12661040766 y 12661040767 que ya compartía con el área de L12.
- **Un way de OSM que ya modela el pasillo se adopta y se corrige, no se duplica** (opción 2), aunque esté con el nivel equivocado. Ricardo: «P11. sí opción 2, tiene sentido con todo y edición de etiquetas»; y el túnel que contradice el acceso por puente se da de baja en la misma edición («El id 536525793 no debería existir, lo eliminamos como parte de las ediciones?»). Detalle en [[task-62]].

**Nombre del contorno de estación:** sin «Metro», como Portales y General Anaya: «Xola», «Viaducto», «Villa de Cortés». Ricardo: «P8. Sí». El generador hoy conserva el `name` de OSM cuando choca.

**Elevadores fuera de esta edición** (opción 1): las estaciones se publican sin los elevadores que la base no tiene y se suman en una edición aparte, como las relaciones `stop_area` ([[task-51]]). Ricardo: «P4. De acuerdo, 1». Trabajo en [[task-71]].

### Consecuencias

- **Bueno:** el archivo mostrará el jardín que engañó la lectura de Nativitas y dejará de proponer bajas que OSM rechaza; el trasbordo de Ermita conserva su id e historia en OSM; las dos líneas de una correspondencia quedan pegadas.
- **Malo:** un contexto más amplio pesa más y trae más ruido al archivo; adoptar el way del trasbordo significa editar algo que llega hasta L12 antes de trazar L12; las tres reglas de trazo están decididas pero el generador todavía no las aplica, así que las versiones de hoy no las cumplen y los turnos de diff las aplican a mano; publicar sin elevadores deja a Xola y Ermita incompletas en OSM hasta la edición aparte.

### Cómo se comprueba

Por ahora, a mano en cada turno: el contexto de la estación trae `landuse`/`leisure`/`natural`, cada banco tiene su tramo para la vuelta tras el nodo de encuentro (largo por confirmar), Ermita 03 tiene el área de L2 cerrando en 12661040766/67 y el way 536525798 reetiquetado. Cuando las tasks de generador cierren, por prueba en `api/utils/osm/`.

## Más información

[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]], [[adr-0017]], [[task-62]], [[task-65]], [[task-69]], [[task-71]].
