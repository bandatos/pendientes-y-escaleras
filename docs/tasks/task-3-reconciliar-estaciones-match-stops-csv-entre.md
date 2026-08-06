---
type: task
id: task-3
title: Reconciliar estaciones-match-stops.csv entre api y vue
state: open
date: 2026-08-06
owner: ai
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Reconciliar estaciones-match-stops.csv entre api y vue

El inventario de la integración detectó que las dos copias difieren en una fila y en contenido. Falta determinar cuál está vigente y alinear.

## Criterios de aceptación

- [ ] Está identificada la diferencia exacta entre api/media/estaciones-match-stops.csv (163 filas) y vue/src/assets/datos/estaciones-match-stops.csv (164 filas)
- [ ] Ricardo validó cuál es la fuente de verdad
- [ ] Ambas copias quedan alineadas o la divergencia queda documentada como intencional
