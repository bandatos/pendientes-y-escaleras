---
type: decision
id: adr-0005
title: El rumbo de los andenes sale de shapes.txt del GTFS; el KML queda como referencia visual
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["data/gtfs/shapes.txt", "data/StatioArea-and-lines.kml", "data/analysis/kml-estaciones-orientacion.csv"]
---

# El rumbo de los andenes sale de shapes.txt del GTFS; el KML queda como referencia visual

## Contexto

Ricardo pidió que los polígonos de andén sigan el trazado de la línea (rotación automática). Se midió sobre 127 estaciones el eje principal del polígono del KML contra el rumbo de la línea.

## Opciones consideradas

- **LineStrings del KML:** un vértice cada 200–730 m (hasta 5,6 km); no dan el rumbo local de un andén de 150 m; además L8 arrastra el ramal de L12, la «Línea A» de 29 km es en realidad LB, y varias líneas tienen colas imaginadas.
- **`shapes.txt` del GTFS:** un vértice cada 20–83 m; proyectando el centroide y tomando los vértices a 150 m, la diferencia con el eje principal del polígono es de 2° de mediana, 96 % dentro de 20° cuando el polígono es alargado (elongación ≥ 2,5; 75 estaciones). Con el rectángulo mínimo en vez del eje principal el error sube a 18°.

## Resultado

Rumbo desde `shapes.txt` (filtrando por `route_id`, no por nombre corto) y eje principal del área del polígono; rotación automática solo con elongación ≥ 2,5; las correspondencias (17 de las 18 con error > 30°) van en fase manual. El KML no se corrige: sus centroides coinciden con el punto GTFS a 10 m de mediana y sirve solo como referencia visual; sus tres estaciones en construcción no se suben.

## Más información

[[2026-08-26-sesion-mapeo-osm]].

La medición que sustenta esta decisión (187 polígonos con orientación y diferencia contra el rumbo del shape) está en `data/analysis/kml-estaciones-orientacion.csv`; el método, en [[2026-08-26-herramientas-mapeo-kml-plantillas]].
