---
type: task
id: task-75
title: Subir a OSM las cuatro versiones de L7 con layer y nodos de andén
state: open
date: 2026-10-30
owner: ricardo
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
related: ["[[adr-0019]]", "[[adr-0020]]", "[[adr-0021]]", "[[task-11]]"]
---

# Subir a OSM las cuatro versiones de L7 con layer y nodos de andén

Las versiones `l7-polanco/polanco-08-claude.osm`, `l7-san-antonio/san-antonio-07-claude.osm`, `l7-san-joaquin/san-joaquin-10-claude.osm` y `l7-san-pedro-de-los-pinos/san-pedro-de-los-pinos-10-claude.osm` son snapshots del servidor del 30 de octubre de 2026 con `action='modify'` en los ways subterráneos que reciben `layer` (56, 57, 61 y 61) y en los pasillos de −3 y andenes que reciben nodo compartido (4, 6, 6 y 6 nodos nuevos). Verificadas en vivo con `check_station_osm_live` sin conflictos. Procedimiento, conteos que JOSM debe mostrar al subir (agregar/modificar/borrar 4/58/0, 6/59/0, 6/63/0, 6/63/0), `source=survey` sin `imagery_used` y el comentario de cada changeset (recortado a menos de 255 caracteres) están en `data/osm/publicacion-2026-10-27.md`, sección del 30 de octubre.

Para cada estación: Ricardo la revisa en JOSM (los modificados se ven resaltados); si acepta subir, dice «sube» y `publish_station_osm` escribe la `-pub` (probado hoy sobre un snapshot: solo quita `upload='never'`); antes de subir se vuelve a correr `check_station_osm_live` por si alguien editó en el intervalo. El aviso de iD de cruce entre el pasillo de −4 y la vía de L7 (`layer=-4` en ambos) es aceptado por Ricardo y Pablo, no se corrige. En San Pedro cuatro de los seis nodos nuevos quedan a entre 0,5 y 0,7 m de un vértice del mismo pasillo (por encima del umbral de 30 cm de reutilización): recomendación, dejarlos; fusionarlos en JOSM correría el borde del andén hasta 0,7 m.

Idea anotada, no comprometida: que cada versión posterior a la publicación salga con una imagen compuesta sobre Esri (lo publicado en rojo, el cambio en verde), como la que sirvió para el jardín de San Pedro el 27; es el mejor «a ojo» para cambios chicos de geometría.

## Criterios de aceptación

- [ ] Ricardo revisó las cuatro versiones en JOSM y dijo cuáles suben
- [ ] Cada estación aceptada tiene su `-pub` escrita por `publish_station_osm` y su changeset subido, con el número anotado aquí
- [ ] Las fichas del skill de las cuatro estaciones nombran la versión publicada (va con [[task-77]])
