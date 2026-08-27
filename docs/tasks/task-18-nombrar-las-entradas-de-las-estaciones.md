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

## Criterios de aceptación

- [ ] Definido el vocabulario de nombre y `ref` de acceso y dónde se guarda en la BD
- [ ] Las estaciones modelo tienen todos sus accesos nombrados sin duplicados
- [ ] El cruce con los nodos OSM usa ese nombre/`ref` como criterio adicional
