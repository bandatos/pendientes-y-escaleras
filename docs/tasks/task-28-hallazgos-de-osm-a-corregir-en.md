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

Errores encontrados en OSM el 2 de septiembre que nuestros archivos no tocan (regla de [[adr-0010]]: nada existente se edita hasta resolver [[task-11]]) pero que chocarán con ellos al subir:

- Nodo de estación de San Pedro de los Pinos (681454741): 31 m al oriente del eje de la Avenida Revolución, único vértice de la vía de L7 cerca de la estación (así que la vía hereda el desplazamiento) y etiquetado `service=yard`.
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
