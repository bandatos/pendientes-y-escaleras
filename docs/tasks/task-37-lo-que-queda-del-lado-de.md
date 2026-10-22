---
type: task
id: task-37
title: Lo que queda del lado de Ricardo tras la sesión del 21 de octubre de 2026
state: open
date: 2026-10-21
owner: ricardo
source: ["[[2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin]]"]
related: ["[[task-24]]", "[[task-26]]", "[[task-29]]", "[[task-34]]", "[[task-36]]", "[[task-28]]", "[[adr-0014]]"]
---

# Lo que queda del lado de Ricardo tras la sesión del 21 de octubre de 2026

Ricardo pidió, antes de irse a dormir el 21 de octubre, que la sesión avanzara todo lo posible y le dejara en una tarea lo que queda de su lado, para revisarlo con calma. Esta es esa lista, como índice: cada punto dice qué es en una línea y enlaza la tarea donde están el detalle y las opciones, que es también donde se anota la respuesta. Ninguno bloquea al siguiente paso del asistente salvo que se diga.

## Revisar en JOSM y en imagen

1. **San Joaquín** (`data/osm/san-joaquin.osm`, previews `data/osm/preview/san-joaquin-level*.svg`, compuestos satelitales `sj-overview-sat.png`, `sj-oriente-sat.png`, `sj-poniente-sat.png` y `spp-ricardo-*-sat.png` en `~/respaldos/san-joaquin-2026-10-21/`): qué mirar y dónde dejar el veredicto, en [[task-29]].
2. **San Pedro regenerado** (`data/osm/san-pedro-de-los-pinos.osm`) contra tu archivo: qué coincide y qué no, en [[task-26]].

## Decisiones abiertas

3. Posición del banco −3→−2 en San Joaquín: [[task-29]].
4. Hechos por estación en la plantilla (puerta norte del pabellón oriente, `closed_doors` heredado de San Pedro): [[task-29]].
5. Orden de preferencia entre orientaciones de cascada que caben: [[task-29]].
6. Entradas de OSM no enlazadas en `osm-links.csv`: [[task-29]].
7. Puertas insertadas como vértices en anillos de explanadas ajenas: [[task-29]].
8. Pellizcos del KML: [[task-29]].
9. Imagen satelital (dónde vive el compositor y sobre qué aplica los ajustes): [[task-36]].
10. Dividir `builder.py` (unas 2000 líneas): sacar bancos y encaje a módulos propios (`fit.py` ya nació como módulo aparte por micro-llamado del ejecutor). Propuesto, no hecho.
11. Tests propuestos y no escritos: regla de slots (con y sin `--mirror`), `slot` manual completo o parcial, holgura de bancos apilados, `side_door_inset`, `CorridorWarp` identidad dentro de la franja, `move_cascade` con `stack_offset` y `closed_doors`, `unpinch_ring`, IoU que degrada contorno a pabellón, puerta sobre anillo de explanada, nodo de estación corrido si hay nodo propio a menos de 1 m, nodo fuera del área como error, regresión de Portales byte a byte. Hoy solo existe `api/utils/osm/test_weld.py` (3 pruebas).
12. `TESTING.md` creado hoy en la raíz con el nivel pytest de `api/` y su puntero en `CLAUDE.md`, para tu visto bueno. El 2 de septiembre lo declinaste («sin testing por ahora», [[task-24]] inciso j); hoy aprobaste el test de soldadura y la sesión lo creó sin volver a preguntarte. Se queda mientras decides: conservarlo (la regla global de testing lo pide cuando hay tests) o borrarlo con su puntero.
13. Idioma del `CLAUDE.md` del proyecto: la regla global pide inglés para todo CLAUDE.md y el de este repo está en español, incluida la sección nueva «Trazos en JOSM y turnos de afinación». Confirmar si es excepción deliberada (repo público, equipo hispanohablante) y dejarla escrita, o traducirlo.

## Decisiones abiertas tras la revisión del crítico

21. **Entradas de OSM movidas al muro.** El 21 de octubre preguntaste qué quería decir «Los accesos de OSM se movieron hasta 10 m hacia el punto medio de un muro»: el generador reutiliza el nodo de entrada de OSM y lo convierte en una de las puertas de su pabellón, sobre el muro al que estaba más pegado, con `action='modify'` (en San Pedro 8,9, 10,3 y 8,3 m, [[task-26]]; el README lo llama «el cambio más discutible del archivo»). En San Joaquín pasó lo mismo con 5582692122 y 5582692121 (1,3 y 1,6 m), después de tu «respetar los que ya tenía bien establecidos openStreetMap». Opciones: (a) moverlas al muro, como hoy; (b) congelarlas en su posición de OSM y poner la puerta donde caen; (c) moverlas solo por debajo de un umbral. Recomendación del coordinador: (c) con 2 m (hoy `ENTRANCE_ADOPT_M`), que deja San Joaquín como está y protege casos como los 8 a 10 m de San Pedro.
22. **Nodo de estación recolocado por una regla de la sesión.** Tú moviste el de San Pedro; la sesión dedujo la regla (eje de la franja de andenes, en la u del cruce que declara la plantilla) y la aplicó a las tres: San Pedro queda a 0,8 m de donde lo dejaste; Portales se mueve 14,5 m, aunque en tu edición de Portales del 2 de septiembre no lo moviste; San Joaquín se mueve 2,8 m y, como el nodo es vértice de la vía `railway=subway` 320892187, la vía de L7 se dobla. Opciones: (a) la regla vale para toda estación, como está; (b) solo se recoloca donde hay un trazo tuyo de referencia, y Portales vuelve a congelarse; (c) se recoloca pero nunca se dobla una vía ajena. Recomendación del coordinador: (c), y dejar Portales como está hasta tu visto bueno. Detalle en las notas de enmienda de [[adr-0014]].
23. **Redacción de la sección «Trazos en JOSM y turnos de afinación» del `CLAUDE.md`.** La redactó el coordinador a partir de tus frases, y añadió sin consultarte dos precisiones: que si OSM o la imagen contradicen una regla «se propone a Ricardo adaptar la regla», y que lo único innegociable es que quepa todo trazo *interior* propio (accesos, pabellones, explanadas y conectores quedan fuera). Opciones: (a) dejarla como está; (b) volver a tu frase literal («Las reglas no deberían ser tan estrictas») más la regla del área tal como la dijiste; (c) quitar solo «se propone a Ricardo». Se queda como está hasta que decidas.
24. **Umbrales fijados por la sesión, para tu visto bueno:** `OUTLINE_MIN_IOU` 0,25; `ENTRANCE_ADOPT_M` 2 m; `PAVILION_MIN_INSIDE` 50 %; `PLAZA_DOOR_M` 0,3 m; tolerancia de deformación de corredores 1,5 m; acortamiento de último recurso 95 % a 70 %; `CONNECTOR_MAX_M` de 40 a 45 m; `unpinch_ring` con `PINCH_TOLERANCE_M` 0,3 m y `PINCH_GAP_M` 0,05 m; consulta de contexto al radio más 130 m, nunca menos de 250 m; nodo de estación corrido a 1 m (`STATION_NODE_CLEAR_M`). Quién decidió cada uno, en las notas de enmienda de [[adr-0014]].
25. **Imagen satelital usada antes de decidir cómo aplicarla (desviación).** Dijiste «hoy solo investigamos y generamos la tarea específica para aplicar y decidir cómo aplicarlo después»; aun así la sesión construyó un prototipo de compositor y un ejecutor Fable revisó San Joaquín sobre la imagen Esri (su única corrección de código, `unpinch_ring`, salió del validador de JOSM, no de la imagen). Los compuestos (PNG con imagen Esri) y los scripts del prototipo están en `~/respaldos/san-joaquin-2026-10-21/` (PNG y `scripts/`); decide si se quedan ahí o se borran tras tu revisión, porque la licencia de Esri no contempla guardar teselas fuera de línea ([[task-36]]).
26. **Tramos cortos entre escaleras paralelas.** Pediste estandarizar «los 2 o 3 footways que conectan las 2 o 3 escaleras paralelas» con el pasillo siguiente; quedó resuelto de hecho como un `lead` común por banco (`[from, to]`, redondeado a medio metro) que parte del nodo de encuentro, pero no se te dijo. Confirma que es lo que querías.

## Lo que tú dijiste que harías

14. Revisar D1 (la franja del KML es exactamente andenes más vías) y D2 (senda desplazada 1,5 m) de [[adr-0014]]; los supuestos sin cerrar del README siguen listados en [[task-26]].
15. Relevar las puertas clausuradas (pabellón oriente de San Pedro, [[task-26]]; San Joaquín no tiene ninguna relevada, [[task-29]]).
16. La regla del validador de parejas de eléctricas en L7 ([[task-34]]); las que solo bajan ya quedaron decididas ahí (`forward` + `incline=down`).

## Pendientes menores que no necesitan decisión, solo que los sepas

17. Hueco de `weld`: una punta de escalera de banco ya no se suelda a otras ways, pero otra way sí puede meter un vértice en la escalera; no ocurre en las tres estaciones. Propuesta del ejecutor: que `weld` no inserte vértices en `highway=steps`. La fixture de `test_weld.py` reproduce ese hueco sin afirmarlo: su tramo corto es colineal con la escalera y `weld` mete su otro extremo, (5, −3), como vértice de la escalera; el ejecutor propuso mover el tramo corto para una fixture más limpia.
18. Permutación de los pasillos de andén por `miro_id` en San Joaquín, sin verificar: [[task-29]].
19. Cosmético de la preview −3 de San Joaquín: [[task-29]].
20. El `service=yard` del nodo de estación de San Pedro: [[task-28]].

## Criterios de aceptación

- [ ] Ricardo revisó San Joaquín en JOSM y dejó su veredicto en [[task-29]]
- [ ] Las decisiones 3 a 8 tienen respuesta anotada en [[task-29]], la 9 en [[task-36]] y la 12, la 13 y de la 21 a la 26 aquí
- [ ] Lo que decida sobre tests y sobre dividir `builder.py` queda como tarea del asistente o descartado
