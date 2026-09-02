---
type: task
id: task-6
title: Verificar y alinear las tres copias del GTFS
state: open
date: 2026-08-06
owner: ai
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Verificar y alinear las tres copias del GTFS

La regla «actualiza data/gtfs/ y propaga, no al revés» quedó como imperativo en el CLAUDE.md global por decisión delegada de Ricardo (5-ago-2026), respaldada por esta verificación. Discrepancia ya detectada: un byte en routes_metro.csv (12 vs L12, línea 13). Sin script de propagación por ahora: disciplina manual; si el GTFS empieza a cambiar seguido, reevaluar un script en data/.

Hallazgos del 1 de septiembre de 2026 ([[2026-09-01-sesion-miro-corchetes-entrance]]): no hay un `stops.txt` completo bajo la carpeta `gtfs` de `api/media`; la copia que consume la API es `api/media/gtfs_metro/stops_metro.csv` (subconjunto Metro, 195 filas), cuya canónica equivalente es `data/gtfs/metro_stops.csv` (idéntica a `data/gtfs/stops_only_metro.txt`). Tras corregir los dobles espacios de Viveros y Niños Héroes en todas ellas, `data/gtfs/stops.txt` y `vue/src/assets/gtfs/stops.txt` son idénticas, y la copia de la API difiere de la canónica en una sola fila: `0200L1_MOCTEZUMA` (guion bajo) en `data/gtfs/metro_stops.csv` frente a `0200L1-MOCTEZUMA` en `api/media`. El `stops.txt` completo trae decenas de dobles espacios fuera del Metro (Metrobús, corredores) que no se tocaron; `import_stops` ya los colapsa al importar.

## Criterios de aceptación

- [ ] Diff exhaustivo entre data/gtfs/, api/media/gtfs_metro/ y vue/src/assets/ (gtfs/ y gtfs_metro/), archivo por archivo
- [ ] Ricardo validó la discrepancia conocida: route_short_name 12 (api) vs L12 (vue) en routes_metro.csv, y cualquier otra que aparezca
- [ ] Las tres copias quedan alineadas desde la canónica, según la regla del CLAUDE.md global
