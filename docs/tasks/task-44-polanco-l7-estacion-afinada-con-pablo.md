---
type: task
id: task-44
title: "Polanco (L7): estación afinada con Pablo y publicada, pendiente de cierre"
state: open
date: 2026-10-27
owner: ricardo
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-38]]", "[[adr-0015]]", "[[adr-0016]]"]
---

# Polanco (L7): estación afinada con Pablo y publicada, pendiente de cierre

Estación profunda de la Línea 7 con accesos a cielo abierto, familia `l7-deep-cascade`, bloque `stations.0200L7-POLANCO`, carpeta `data/osm/l7-polanco/`, hechos en `.claude/skills/station-tuning/references/estaciones/polanco.md`.

## Estado al 27 de octubre de 2026

- Versión aprobada: `polanco-07-claude.osm`. Cadena: 01 generada con `keys` (renombra los sufijos N-xx porque el tablero numeró los nodos con otros papeles), 02 tracer, 03 de Pablo (respondió las cuatro dudas: boca norponiente en la punta de la pestaña, lóbulos sur son nichos electromecánicos sin trazo, salida doble al oriente, pasillo central bien identificado), 04 integra a Pablo, 05 escaleras de salida a 10 m (regla de Pablo solo para Polanco) y relación `stop_area` 8429771 ausente, 06 acceso doble oriente en línea con el descanso de Pablo (9,95 y 8,73 m; Ricardo eligió la opción 1, en línea con el descanso de Pablo; la variante centrada de 61 cm no se le preguntó y se dejó sin aplicar), 07 reversibles de arriba hacia abajo con `incline=down`.
- Publicada en OSM por Ricardo con `polanco-07-pub.osm`: changeset 191085961 (00:51 del 27 de octubre; 243 creados, 4 modificados: las tres entradas y el nodo de estación), con el texto de `data/osm/publicacion-2026-10-27.md`.
- La plantilla reproduce la 06 con residuo cero (`relocate`, `connector`, `end_tags` y el área de la 06 en el bloque); falta solo el cambio de la 07 (sentido de las reversibles), que el generador ya hace por `draws_reversed`.
- Correcciones de Pablo al área (0,2 a 0,4 m y la pestaña sur alargada 4,5 m) viven en el bloque `area` del JSON.

## Criterios de aceptación

- [ ] Polanco publicada en OSM con el `-pub` de la versión aprobada y el texto de `data/osm/publicacion-2026-10-27.md` (el archivo y el comentario corto sí, changeset 191085961; el texto largo en la discusión del changeset no se ha publicado)
- [ ] Ricardo declara cerrada la estación
- [ ] Regenerar con --out reproduce la versión aprobada
