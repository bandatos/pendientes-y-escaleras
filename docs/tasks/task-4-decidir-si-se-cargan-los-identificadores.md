---
type: task
id: task-4
title: Decidir si se cargan los identificadores oficiales STC a Stair.code_identifiers
state: open
date: 2026-08-06
owner: ricardo
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Decidir si se cargan los identificadores oficiales STC a Stair.code_identifiers

`data/raw/escaleras_metro.csv` (468 registros) contiene un identificador por escalera física que no existe en ningún otro dato del repo: 304 con patrón alfanumérico `<línea><estación><posición><tipo>` (p. ej. `1BA11S`, consistente con la señalización oficial del STC) y 164 folios numéricos puros. Nunca fue importado ni referenciado por código. El modelo `Stair` (y `Pathway`) tiene el campo `code_identifiers` (JSONField) diseñado justo para esto, y hoy está vacío en todas las escaleras. Cubre el mismo universo que `api/media/escaleras_electricas.csv` (mismas 104 combinaciones línea+estación, 468 vs 467 filas), con variantes de normalización de nombres que complican un match automático (además hay numero_identificacion duplicados, p. ej. `K6`, `8727`).

## Criterios de aceptación

- [ ] Ricardo confirmó qué es numero_identificacion (patrón tipo 1BA11S y folios numéricos) y si vale la pena importarlo
- [ ] Si procede, existe una task hija con el alcance del comando de importación/match
