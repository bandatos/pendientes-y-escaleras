---
type: task
id: task-18
title: Nombrar las entradas de las estaciones
state: open
date: 2026-08-26
owner: ricardo
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
related: ["[[task-16]]", "[[task-11]]"]
---

# Nombrar las entradas de las estaciones

Pendiente que dejó la reunión del 19 de agosto («ponerle nombre a las entradas»). Nuestros accesos se llaman `[L<n>] Acceso <rumbo|calle>` (con duplicados, p. ej. dos «L1 Acceso suroriente» en Tacubaya). En OSM, de 447 nodos `railway=subway_entrance`, 274 tienen `name` pero casi todos con el nombre de la estación, no de la salida, y solo 1 tiene `ref`. Wikipedia y el sitio del STC traen los nombres de salida (rumbo + calle) sin coordenada. Objetivo: que cada acceso tenga `name` (calle/referencia) y `ref` (letra o número señalizado) verificables en sitio, para subir a OSM y para el cruce con los nodos existentes (Tacubaya y Mixcoac como modelo: ahí OSM ya copió las salidas de Wikipedia). Depende de reclasificar los 33 «Andén» ([[task-16]]).

## Avance del 1 de septiembre de 2026

[[adr-0009]] responde parte del primer criterio: el nombre neutro de un acceso bidireccional es «Acceso», la dirección va en `Stop.entrance` con el vocabulario OSM (`yes` / `entrance` / `exit`, alimentado por `[salida]` / `[entrada]` en Miro) y las marcas de clasificación van entre corchetes, nunca en el nombre. Sigue abierto el `ref` (letra o número señalizado) y el nombre por calle. Registro en [[2026-09-01-sesion-miro-corchetes-entrance]].

Sobre los andenes: alguien había escrito «Llegadas» / «Salidas» en lugar de la dirección en ocho andenes del tablero (Constitución de 1917, Martín Carrera, Universidad, El Rosario); Ricardo lo revirtió porque la dirección es el dato. Pero la idea es válida para la interfaz y para la capa OSM: cuando se muestre o exporte un andén, conviene hacer visible su `entrance` («solo llegadas» / «solo salidas»), que en OSM es el rol `platform_exit_only` / `platform_entry_only` de la relación de ruta.

## Criterios de aceptación

- [ ] Definido el vocabulario de nombre y `ref` de acceso y dónde se guarda en la BD (la dirección ya está: `entrance`, [[adr-0009]]; falta `ref` y el nombre por calle)
- [ ] Las estaciones modelo tienen todos sus accesos nombrados sin duplicados
- [ ] El cruce con los nodos OSM usa ese nombre/`ref` como criterio adicional
