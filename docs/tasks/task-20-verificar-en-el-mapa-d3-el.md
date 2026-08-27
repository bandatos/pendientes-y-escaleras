---
type: task
id: task-20
title: Verificar en el mapa d3 el desplazamiento La Villa/Lagunilla y La Paz/La Raza
state: open
date: 2026-08-26
owner: ricardo
related: ["[[task-3]]", "[[2026-08-26-sesion-mapeo-osm]]"]
---

# Verificar en el mapa d3 el desplazamiento La Villa/Lagunilla y La Paz/La Raza

Ricardo reportó que en la visualización d3 «La Villa y Basílica» aparece donde va Lagunilla y «La Paz» donde va La Raza. En la base recuperada de la Surface (`escaleras-local`) los cuatro estaban correctos; solo Iztacalco ↔ Iztapalapa estaba cruzado (errata «Itzapalapa» en el CSV), ya corregido al hacer que `recover_viz_features` resuelva por `stop_id`. El síntoma no se pudo reproducir: puede corresponder a otro estado de la base.

## Criterios de aceptación

- [ ] Ricardo confirma en el mapa d3, contra la base actual, si las cuatro estaciones están en su lugar
- [ ] Si siguen desplazadas: se documenta la evidencia (captura y consulta a `Station.x_position/y_position`) y se reabre con la causa
- [ ] Si están bien: se cierra
