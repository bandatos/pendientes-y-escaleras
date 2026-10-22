---
type: task
id: task-28
title: "Hallazgos de OSM a corregir en la comunidad: nodo de San Pedro de los Pinos, nivel del trazo de L7, andén-cajón de Zócalo y accesos de Aquiles Serdán"
state: open
date: 2026-09-02
owner: ricardo
source: ["[[2026-09-02-investigacion-osm-indoor-y-estado-l2-l7]]"]
related: ["[[task-10]]", "[[task-11]]", "[[task-20]]"]
---

# Hallazgos de OSM a corregir en la comunidad: nodo de San Pedro de los Pinos, nivel del trazo de L7, andén-cajón de Zócalo y accesos de Aquiles Serdán

Errores encontrados en OSM el 2 de septiembre que nuestros archivos no corrigen (corregir lo ajeno espera a [[task-11]]) pero que chocarán con ellos al subir:

- Nodo de estación de San Pedro de los Pinos (681454741): su posición ya la corrige el generador (nota del 21 de octubre de 2026, abajo); queda aquí solo su `service=yard`, que no corresponde a una estación y que lleva también el de San Joaquín (681448501).
- Vía de L7 (320892187): `level=-4` y `layer=-4` en sus 17,4 km; nuestros andenes van a −3 y solo el pasillo de cambio de andén a −4.
- Zócalo: la vía 1251764016 etiquetada como andén es el cajón completo de 180 × 55 m; los andenes reales son dos laterales. La relación `stop_area` 7902754 usa el rol `subway_entrance`, no documentado.
- Aquiles Serdán: cuatro accesos con `name=Aquiles Serdán`, el nombre de la estación, contra el wiki; la letra va en `ref`.
- Viaducto, Xola, Villa de Cortés y Nativitas: nodo de estación a más de 60 m de cualquier vía `railway=subway` (relacionado con [[task-20]]).
- Balbuena (L1): `conveying=island`, `layer=-2;-1`, niveles inconsistentes.

Ricardo decide si se corrigen en el mismo changeset de la primera subida, en uno aparte, o se llevan al colectivo ([[task-10]]).

## Criterios de aceptación

- [ ] Cada hallazgo tiene destino: corregido, delegado al colectivo o descartado con motivo

## Notas de trabajo

- 2 de septiembre de 2026 (tarde, [[2026-09-02-sesion-integracion-osm-y-niveles]]): nuevo hallazgo en Portales: las dos ways `railway=subway` de L2 (312086250, 1322667667) llevan `layer=1` y el edificio de la estación `layer=2`; nuestro andén va en `level=0` sin `layer`. Ricardo propone `layer=0` para las vías porque el puente vestibular las cruza en `layer=1`. Sin modificar por ahora. También: las rutas de L2 y L7 usan el nodo de estación con rol `stop`; Portales tiene dos `stop_position` que ninguna ruta referencia; San Pedro tiene dos `stop_area` de nombre casi igual (7927097 del Metro, 21119669 del trolebús).
- 21 de octubre de 2026 (noche): el nodo de estación deja de ser hallazgo de comunidad y pasa al generador (`station_node` en la plantilla), por decisión de Ricardo (notas de enmienda de [[adr-0014]] y [[adr-0011]]): «Sí moví la estación de OSM, creo que no debería estar congelado, es más preciso el mío y consistente con todo lo demás que se subirá». San Pedro se mueve 29,7 m, San Joaquín 2,8 m y Portales 14,5 m. El hallazgo de Viaducto, Xola, Villa de Cortés y Nativitas (nodo a más de 60 m de la vía) se resolverá igual cuando se generen esas estaciones.
