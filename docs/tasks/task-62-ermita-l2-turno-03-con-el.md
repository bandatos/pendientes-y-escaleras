---
type: task
id: task-62
title: "Ermita L2: turno 03 con el trasbordo de OSM adoptado y el área pegada a la de L12"
state: open
date: 2026-10-30
owner: ai
parent: "[[task-56]]"
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Ermita L2: turno 03 con el trasbordo de OSM adoptado y el área pegada a la de L12

Carpeta `data/osm/l2-ermita/`. Marco de la 01: rumbo 9,0° (promedio ponderado de los bordes largos del área; Ermita no tiene rumbo de shape), ancla 19.361969,-99.1429123. Se exporta como `020L12-ERMITA --line L2` porque los stops de L2 cuelgan del padre de L12. Hechos en `.claude/skills/station-tuning/references/estaciones/ermita.md`.

## Versiones

- `ermita-01-claude.osm`: generada; falla la validación (torniquete a 0,24 m del nodo de OSM 1122534026, del puente viejo).
- `ermita-02-claude.osm`: la nuestra. Edición directa sobre la 01 con script (`.claude/scratch/l2-2026-10-27/ermita-make02.py`, fuera del versionado): las adopciones de entradas y los conectores no los reproduce una regeneración ([[task-67]], [[task-70]]).
- No hay versión de Ricardo: sus respuestas vinieron en texto. El siguiente turno escribe la 03 aplicándolas, y ese es su primer entregable (no hay diff de una versión suya).

## Lo que la 03 debe aplicar (decidido por Ricardo, [[adr-0018]])

- **P11, el trasbordo.** Adoptar el way de OSM 536525798 «Transbordo Intermodal Metro Ermita» como nuestro pasillo de nivel 1: conservar su id, mover sus vértices a nuestra línea (la del way −97 de la 02, por el eje de la franja hasta donde se abre a L12), reetiquetarlo de túnel (`tunnel=yes`, `layer=0`) a `bridge=yes`, `layer=1`, `level=1`, y borrar nuestro way nuevo. Dar de baja el túnel 536525793 de nivel −1 (va de la entrada poniente al andén y contradice el acceso por puente) con `action=delete`; comprobar con `check_station_osm_live` al marcarlo `action=delete` que no pertenece a ninguna relación (no está verificado: la consulta en vivo solo revisa elementos con `action`). Ricardo: «P11. sí opción 2, tiene sentido con todo y edición de etiquetas. El id 536525793 no debería existir, lo eliminamos como parte de las ediciones?».
- **P12, sin hueco con L12.** El área de L2 se estira a los nodos 12661040766 y 12661040767, que comparte con el área de L12 (way 1367187879), apartándose unos 6 m del KML en esa punta. Ricardo: «P12. No dejar huecos».
- **Nodo de estación 12679525779** («Ermita», nodo único de la correspondencia, en L12, miembro del `stop_area` «Ermita (Linea 2)»): no se mueve (`station_node: null` en el bloque `020L12-ERMITA`).

## Ya hecho en la 02, sin objeción de Ricardo

- Entradas de OSM 5197238662 (E-01, movida 4,94 m) y 5197238663 (E-02, 2,92 m) adoptadas; la 01 ni siquiera traía la segunda.
- Puente peatonal 43763058 con sus nodos (1122534026, 30384910, 554206684) y la escalera 1304926070 con su nodo 554206678 dados de baja.
- Conectores perpendiculares soldados a mitad de banqueta con vértices nuevos: E-01 a 1367360654 (5,60 m), E-02 a 1367360653 (2,18 m).

## Abierto

- ¿L2 tendrá algún día su propio `railway=station`? Se decide al trazar L12.
- El extremo sur del pasillo queda suelto hasta trazar L12.
- Un elevador de L2 en el CSV crudo, fuera de esta edición ([[task-71]]).
- **Pregunta a Ricardo, que no le llegó:** el conector de E-01 a la banqueta 1367360654 mide 5,6 m; si no le parece evidente, se quita.

## Criterios de aceptación

- [ ] Ermita 03 con P11 y P12 aplicadas, validada y con la consulta en vivo limpia
- [ ] Versión aprobada por Ricardo
