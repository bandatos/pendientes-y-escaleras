---
type: task
id: task-16
title: Reclasificar los 33 nodos «Andén» guardados como acceso
state: open
date: 2026-08-26
owner: ricardo
---

# Reclasificar los 33 nodos «Andén» guardados como acceso

33 de 445 stops con `location_type=2` son en realidad andenes (listado por estación en `data/analysis/osm-accesos-cruce.csv`, columna `notes`) (por ejemplo Universidad 10, Zaragoza 7, Constitución de 1917, Santa Anita), pero están guardados como acceso.

Decidir si deben ser nodo genérico u otra cosa, y corregir en Miro o en el parser según corresponda.

Actualización del 1 de septiembre de 2026 ([[2026-09-01-sesion-miro-corchetes-entrance]]): tras tres reimportaciones el conteo sigue siendo exactamente 33 (Universidad 10, Constitución de 1917 9, Zaragoza 7, Santa Anita 7). Trece de ellos llevan además la marca `[IZQ & DER]` (Zaragoza «Andén A» a «G», Santa Anita «L4 Andén B» a «G»; «L4 Andén A» de Santa Anita es la única sin marca), así que al reclasificarlos hay que decidir también qué significa esa marca en un nodo que no es acceso. Ricardo: por ahora son Entrance/Exit y se revisan con Pablo; la palabra «Andén» en el nombre de un acceso se corregirá para no confundir ([[task-24]]).

Observación del volcado con estilo (1 de septiembre de 2026): los «L4 Andén A» a «G» de Santa Anita están dibujados como rectángulo, la forma de acceso, no como el rectángulo redondeado de andén; F y G llevan además relleno casi negro `#1a1a1a`. Son los únicos rectángulos del tablero con ese color.

## Criterios de aceptación

- [ ] Está decidido qué tipo de nodo les corresponde a los 33 stops
- [ ] Los 33 quedan reclasificados en Miro o en el parser, según dónde se decidió corregir
