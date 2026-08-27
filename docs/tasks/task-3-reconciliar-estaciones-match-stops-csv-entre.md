---
type: task
id: task-3
title: Reconciliar estaciones-match-stops.csv entre api y vue
state: closed
date: 2026-08-06
owner: ai
source: ["[[2026-08-05-integracion-del-monorepo]]"]
validate-paths: false
---

# Reconciliar estaciones-match-stops.csv entre api y vue

El inventario de la integración detectó que las dos copias difieren en una fila y en contenido. Falta determinar cuál está vigente y alinear.

## Criterios de aceptación

- [x] Está identificada la diferencia exacta entre api/media/estaciones-match-stops.csv (163 filas) y vue/src/assets/datos/estaciones-match-stops.csv (164 filas)
- [x] Ricardo validó cuál es la fuente de verdad
- [x] Ambas copias quedan alineadas o la divergencia queda documentada como intencional

## Outcome

La divergencia 163 vs 164 era un salto de línea dentro de una celda, no una fila real de más. Se eliminó la copia de `vue/src/assets/datos/estaciones-match-stops.csv`; `api/media/estaciones-match-stops.csv` queda como única fuente de verdad. `recover_viz_features.py` se corrigió para resolver por `stop_id` en vez de por nombre.
