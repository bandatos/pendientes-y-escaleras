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

## Criterios de aceptación

- [ ] Diff exhaustivo entre data/gtfs/, api/media/gtfs_metro/ y vue/src/assets/ (gtfs/ y gtfs_metro/), archivo por archivo
- [ ] Ricardo validó la discrepancia conocida: route_short_name 12 (api) vs L12 (vue) en routes_metro.csv, y cualquier otra que aparezca
- [ ] Las tres copias quedan alineadas desde la canónica, según la regla del CLAUDE.md global
