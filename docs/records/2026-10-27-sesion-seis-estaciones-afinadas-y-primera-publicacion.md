---
type: record
id: 2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion
title: "Sesión del 26 y 27 de octubre de 2026: seis estaciones afinadas con Pablo y primera publicación en OSM"
date: 2026-10-27
---

# Sesión del 26 y 27 de octubre de 2026: seis estaciones afinadas con Pablo y primera publicación en OSM

Bitácora `8a038b6f-5cf4-48e8-acd0-4bde8e85b3d4`. Rama `first-stations-josm`. Commits: `14dcab4`, `423e2ef`, `8b6da43` y el del cierre.

## Punto de partida

Dos sesiones del 26 de octubre quedaron congeladas sin cerrar: la de General Anaya (`f4f115f4-…`) y la de Polanco (`dea421a0-…`). Esta sesión las retomó por exploración de bitácoras en vez de revivirlas. Ninguna había hecho commit ni abierto su nodo-tarea; el trabajo (carpetas de estación, bloque de Polanco y mecanismo `keys` en la plantilla L7) estaba en el árbol sin versionar.

## Qué pasó

- **Portales: linaje bifurcado.** La `portales-03-claude.osm` del repo era la 01 regenerada con el nodo de estación movido, no sucesora de la edición de Ricardo (`02-rick`). Ricardo decidió borrarla. Pablo había afinado Portales sobre esa 03 (que Ricardo le mandó creyéndola la última), así que su versión no traía el vestíbulo de nivel 1 de Ricardo; se injertó en la 05. Lección: verificar el linaje (coincidencia al centímetro con cada versión previa) es el primer paso cuando llega una versión de un tercero.
- **JOSM no dejaba subir** porque todos los `.osm` llevan `upload='never'` por [[adr-0010]] y [[adr-0013]], condicionado a [[task-11]]. Ricardo decidió publicar unas doce estaciones como mapeo manual con cuenta personal (la de Pablo, mapeador con historial), no como import: todo el relevamiento es de campo, recorridos del equipo de Bandatos. Pablo confirmó por WhatsApp que las relaciones `stop_area` del servidor no se tocan: quedan ausentes de nuestros archivos, nunca con `action='delete'`. Nació `publish_station_osm`, que escribe la copia `<slug>-NN-pub.osm` sin traza y sin `upload`.
- **Cinco archivos de Pablo** (correo de las 19:35 del 26 de octubre) entraron como versiones `-pablo`: Portales 03, General Anaya 03, San Joaquín 07, San Antonio 04 y San Pedro 06. Polanco 03 ya estaba. Cada uno recibió un turno de diff completo con hipótesis de intención y capa, y correcciones de oficio (derivas de arrastre, ortogonalidad, nodos coincidentes sin unir en San Pedro, reversibles).
- **Reglas nuevas dictadas por Pablo y confirmadas por Ricardo**, o decididas por Ricardo: la reversible de cada trío se dibuja de arriba hacia abajo con `incline=down` ([[adr-0016]]); el par de −1 a 0 de la cascada L7 va a 3,0 m entre ejes; conectores a la banqueta solo cuando son evidentes (San Pedro queda sin ninguno, San Antonio con sus tres rectos); la boca de un acceso a cielo abierto es vértice del anillo del área; el lóbulo del área es el pabellón de Tlalpan y no lleva `building` propio; una sola puerta por pabellón hacia la Calzada; banco de acceso de dos escaleras a 1,8 m, 12,5 m, en el eje del brazo del puente con el pie a 3 m del fondo; el nodo de estación a media distancia entre los brazos conservando el despeje de 1 m; las escaleras del andén de Tlalpan conservan la disposición en serie de Ricardo y toman el largo de las de acceso o el máximo que quepa (9,1 m en General Anaya; 12,5 y 9–10 m en Portales); en Polanco las escaleras de salida a 10 m (solo esa estación) y el acceso doble oriente con el descanso de Pablo (9,95 y 8,73 m); el pasillo superior de OSM se borra solo si cae sobre el área; General Anaya con una sola puerta por pabellón; San Joaquín con una sola puerta por pabellón y nombre «Entrada Metro San Joaquín»; San Pedro con la puerta norte del oriente clausurada y el área agrandada 8,5 m al sur por lóbulo; los nodos de calle que Pablo movió en Portales se quedan (Hamburgo termina donde él dice).
- **El generador** ya no da de baja nodos que la Calzada o las vías siguen usando (`settle_deletes`), mide brazos y lóbulos del área (`arms.py`) para la plantilla de Tlalpan, dibuja las reversibles hacia abajo (`draws_reversed`), exime a los ways ajenos del chequeo de `incline`, y el bloque de Polanco reproduce la 06 con residuo cero. 24 pruebas en verde.
- **Versiones aprobadas**: General Anaya 06, Polanco 07, Portales 05, San Joaquín 09, San Pedro de los Pinos 08 y San Antonio 06, cada una con su `-pub`. `data/osm/publicacion-2026-10-27.md` lleva la mecánica en JOSM y los textos de changeset (corto para `comment`, 255 caracteres; largo para la discusión), revisados por el agente de voz.
- **Publicado por Ricardo** con su cuenta: General Anaya (changeset 191085829: 79 creados, 2 modificados, 14 borrados) y Portales (changeset 191085874: 81 creados, 7 modificados, 25 borrados), verificados contra la API: el contenido coincide objeto por objeto con el `-pub`. Pendientes de subir: Polanco, San Joaquín, San Pedro y San Antonio.
- **Harness del proyecto**: el skill `station-tuning` pide ahora reportar cada hallazgo entero, sin resumir (corrección de Ricardo de esta sesión), y la línea de relevo ya no nombra tareas.

## Incidente

Un tracer puso el correo de Ricardo en la cabecera User-Agent de una consulta a overpass-api.de, una sola vez. Ricardo quedó avisado; la consulta siguiente usó un identificador neutro del proyecto. Trabajo abierto en su task.

## Lo que queda abierto

Las tareas nuevas de esta sesión: plantilla de Tlalpan con el vestíbulo longitudinal, corrimientos de apilado de la L7 con el par a 3,0 m, validador (descanso de dos niveles y cercanía entre segmentos), command de validación de archivo, User-Agent fijo, CRLF, relaciones `stop_area` en edición aparte, y el linaje como primer paso del diff en el skill.
