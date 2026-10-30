---
type: task
id: task-67
title: "Generador: un acceso enlazado por osm_node con locate door debe llevar la entrada a la puerta"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Generador: un acceso enlazado por osm_node con locate door debe llevar la entrada a la puerta

Con `osm_node` en un acceso de la plantilla de Tlalpan, el generador deja la entrada donde OSM la tiene en vez de llevarla a la puerta que calcula `locate: door`; sin `relocate: true` el camino en U del pabellón se queda con un solo nodo («way tiene menos de dos nodos», Ermita) o deja un vértice de puerta huérfano en el anillo (Nativitas). Ermita tuvo que adoptar sus entradas a mano y una regeneración no lo reproduce. Del mismo turno: la 01 de Ermita no trajo al archivo la entrada 5197238663, que estaba a 2,9 m de la puerta y en `context.json`; revisar por qué se filtró. Idea del trazador de Xola: una `subway_entrance` de OSM con el nombre de la estación que cae en el lóbulo o a 2 m podría adoptarse sola como puerta del pabellón.

## Criterios de aceptación

- [ ] osm_node con locate door adopta el nodo y lo lleva a la puerta calculada sin relocate
- [ ] Las entradas de OSM cercanas a la puerta entran al archivo
- [ ] Prueba en api/utils/osm
