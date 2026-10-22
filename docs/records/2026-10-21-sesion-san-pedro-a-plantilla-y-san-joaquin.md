---
type: record
id: 2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin
title: "Sesión del 21 de octubre de 2026: convenciones de San Pedro a la plantilla, San Joaquín generada, cierre documental de la v3"
date: 2026-10-21
source: ["[[task-26]]", "[[2026-09-30-imagenes-sotm-evolucion-portales]]"]
---

# Sesión del 21 de octubre de 2026: convenciones de San Pedro a la plantilla, San Joaquín generada, cierre documental de la v3

Sesión del 21 de octubre de 2026 (session log `session_017Cbrxn4s2qsEMQmwknNUox`), rama `first-stations-josm`. Ricardo trajo su corrección manual completa de San Pedro de los Pinos en JOSM (`data/osm/reference/san-pedro-de-los-pinos-ricardo-2026-10-21.osm`, los dos lados alineados) y preguntó qué quedaba del proceso de pasar los esquemas a JOSM. La sesión pasó sus convenciones a la plantilla `l7-deep-cascade` y al generador, generó por primera vez San Joaquín, hizo el cierre documental que la v3 nunca tuvo ([[adr-0014]]) y dejó en una tarea lo que queda de su lado. Ricardo se fue a dormir a media sesión y pidió que se avanzara todo lo posible con delegados y se cerrara completo.

## Decisiones de Ricardo, en su orden

- **Feedback de proyecto.** «Los FB no deberían ocurrir a nivel de proyecto, hay que mover esos FB a las tasks en todo caso.» Y después: «Esta vez será mejor borrar por completo toda la carpeta de fb para no confundirnos en el futuro». fb-1 estaba promovido al CLAUDE.md, fb-2 absorbido por [[adr-0012]], fb-3 pasó a [[task-35]]; las citas que solo vivían ahí se copiaron a [[task-7]], [[task-35]] y [[adr-0012]], y la carpeta de feedback del proyecto se borró (respaldo en `~/respaldos/pendientes-y-escaleras-feedback-2026-10-21/`).
- **Cierre documental de la v3 antes de tocar el generador:** sí; nació [[adr-0014]], y adr-0011 recibió nota de enmienda.
- **Corroborar la convención de escaleras paralelas con un delegado:** sí. Se sostiene contra la wiki de OSM y contra 32 637 escaleras eléctricas del mundo (Overpass al 20 de octubre): mismo `level` en la pareja, ambas `incline=up` si se dibujan hacia arriba, `reversible` para la que baja de ordinario y se invierte, pasillos como `footway` + `indoor=yes`. Un par de Montparnasse (ways 679728899 y 679728907) es idéntico a la convención. La justificación de `oneway:foot` se corrigió en el README y en [[adr-0013]]: OSRM lee `conveying` desde v26.5.0; GraphHopper y Valhalla solo leen `oneway:foot`. Las eléctricas de un solo sentido que bajan se quedan dibujadas hacia abajo con `forward` + `incline=down` (en [[task-34]]).
- **P1, regla de posición lateral:** «La fija siempre enmedio (L7), si hay 3 eléctricas (dos que suben y una que baja) las que suben van juntas a la derecha, luego las fijas enmedio y la que baja a la izquierda (visto desde abajo)». Y la regla general: «Siempre las escaleras de la L7 (y todas las paralelas que van en sentidos opuestos) deben ir en el sentido de las calles, avanzas por la derecha, los que vienen en el otro sentido, los ves a tu izquierda, no importa si subes o bajas».
- **P2, defecto de soldadura:** arreglar en el código común (`weld()` ya no suelda puntas de banco), no en la plantilla; test de regresión aprobado y escrito (`api/utils/osm/test_weld.py`).
- **P3, camino:** codificar primero sus convenciones, regenerar San Pedro hasta que coincida con su archivo, y entonces generar San Joaquín.
- **P4, estado de adr-0014:** lo dejó al asistente; queda `accepted`.
- **P5:** el ADR de la nueva cascada enmienda a adr-0014, no lo reemplaza.
- **P6:** en los bancos −2→−1 manda la regla (fija al centro) aunque su trazo tuviera la fija en el borde.
- **P7:** corrimiento lateral de los bancos apilados con sus valores (−0,5 m oriente, −1,5 m poniente), no 1 m.
- **P8:** un edificio de OSM que se traslapa poco con el área del KML no se trata como contorno; se adopta como pabellón (umbral de IoU 0,25 fijado por la sesión).
- **Nodo de estación de OSM:** «Sí moví la estación de OSM, creo que no debería estar congelado, es más preciso el mío y consistente con todo lo demás que se subirá». El generador lo recoloca al eje de la franja de andenes: regla de la sesión, aplicada también a Portales (14,5 m) y San Joaquín (2,8 m, la vía de L7 se dobla); pendiente de su visto bueno en [[task-37]].
- **Regla fundamental:** «todos los trazos deberían caber dentro del área de la estación. En el caso de San Joaquín, las escaleras son perpendiculares a las vías del tren. Cómo darte de cuenta de eso? Pues no caben si fuera al revés». Es error de validación y el generador prueba orientaciones hasta que la cascada cabe.
- **Pabellones:** «Te inventaste los edificios de entrada en lugar de respetar los que ya tenía bien establecidos openStreetMap, a pesar de que tenía la etiqueta de building: transportation.» Y la explanada oriente de San Joaquín con su entrada, que no se traía: ahora se adoptan explanadas (relaciones) y entradas de OSM. El radio no hizo falta ampliarlo: la explanada quedaba dentro de los 120 m, lo que faltaba era pedir las relaciones a Overpass; los 120 m quedan como parámetro (`--context-radius`).
- **Reglas no estrictas y turnos de afinación:** «Las reglas no deberían ser tan estrictas», y «rífate con los SAG hasta que quede y haga sentido, yo checo el resultado, pero intenta ir a fondo antes de presentarme algo». Ambas quedaron en el CLAUDE.md del proyecto, sección «Trazos en JOSM y turnos de afinación». También: «usa Fable si hace falta para lo más fino, sin ningún cuidado».
- **Imagen satelital:** «investiguemos de una vez si la CDMX tiene datos públicos… Excluyamos mapillary… Si funciona CDMX, pues esa, si no, pues Esri, pero bueno, hoy solo investigamos y generamos la tarea específica». La CDMX no publica ortofotos; Esri queda como fuente. Tarea creada: [[task-36]].
- Ricardo arregló él mismo el enlace roto que el borrado de fb-3 dejó en el harness global (fb-335).

## Lo hecho, por bloque

1. Exploración de apertura y lectura del archivo de Ricardo: inventario, parejas de eléctricas, defecto del corredor −2 oriente (way −594 enganchado a la punta de la fija) con origen en `weld()` del generador.
2. Soldadura: `OsmDocument.bank_tips`, exclusión en `weld`, regla `_check_bank_tips` en el validador, test de regresión que muerde.
3. Grafo: adr-0014 (geometría v3), task-35 (nivel del conector desde fb-3), feedback borrado y enlaces reparados, task-26 corregida y con la lista de los supuestos sin cerrar, README y adr-0013 enmendados.
4. Plantilla y generador: bancos por `junction`/`direction`/`length`, `stacked_on`/`stack_offset`, regla de slots (`_assign_bank_slots`), `side_door_inset`, cambio de andén al pasillo central; San Pedro regenerado coincide con el archivo de Ricardo en 231 de 252 nodos a menos de 0,5 m; Portales idéntico byte a byte.
5. San Joaquín a fondo: `fit.py` (encaje: deformación de corredores a los ramales del KML, ocho simetrías de la cascada, la que cabe), área del KML como error, pabellones `transportation` adoptados, explanadas como relaciones con sus puertas, entradas de OSM adoptadas, `--context-radius`, connectors hasta 45 m, nodo de estación recolocado (San Pedro 29,7 m, Portales 14,5 m, San Joaquín 2,8 m). Validación sin errores, 0 nodos fuera, 1 aviso legítimo.
6. Revisión fina con Fable sobre imagen Esri z19 compuesta con KML, OSM y trazos: veredicto de plausibilidad de la cascada, pabellones y entradas correctas; una corrección general (`unpinch_ring` en `geometry.py`: los pellizcos del KML que cruzaban el borde del anillo se separan 5 cm; el validador de JOSM headless ya no marca el área). Compuestos respaldados en `~/respaldos/san-joaquin-2026-10-21/`.
7. Investigación de ortofotos (CDMX, INEGI, Esri, Bing, Mapbox) y tarea de imagen satelital.
8. `TESTING.md` creado con el nivel pytest de `api/` y puntero en el CLAUDE.md.

## Lo que quedó abierto

Todo lo de Ricardo está en [[task-37]], creada hoy; los llamados técnicos con opciones, en [[task-29]]. Una corrección del coordinador que vale registrar: afirmó a Ricardo que «en los cuatro bancos la reversible quedó al oriente de la forward»; era falso (solo en los −3→−2) y el ejecutor lo refutó con los datos.
