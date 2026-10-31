---
type: task
id: task-78
title: El validador del generador predice los avisos de cruce de iD con el contexto real
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
related: ["[[adr-0019]]", "[[task-47]]", "[[task-48]]", "[[task-76]]"]
---

# El validador del generador predice los avisos de cruce de iD con el contexto real

Cualquier esquema de `layer` nuestro depende de datos ajenos que cambian (la vía de L7 cambió de `layer` cinco veces en diez años). Lo que protege no es el valor elegido sino saber, antes de aprobar un archivo, qué cruces marcará iD. La regla de iD (`isLegitCrossing` en `modules/validations/crossing_ways.ts`) son unas treinta líneas: ambos interiores con `level` distinto → legítimo; misma `layer` explícita → aviso; `bridge` o `tunnel` en uno solo → legítimo; `layer` distinta (0 por omisión) → legítimo; solo entran líneas o áreas de highway, building, railway de vía (líneas), waterway y aeroway, y se saltan los pares que comparten nodo. Hoy existió una réplica desechable en `/tmp/layer-cross/crosslib.py` que dio los conteos de la sesión; hay que reescribirla dentro de `api/utils/osm/validate.py` como aviso, corriendo sobre nuestros ways contra los del contexto (`context.json`) y entre nuestros propios ways, y que el command la reporte por archivo. Con ella, la regla «layer = level» se queda como default y cada estación muestra sus excepciones antes de aprobarse.

## Criterios de aceptación

- [ ] `validate()` emite un aviso por cada par de ways que iD marcaría como cruce, con ids y la razón (misma layer, capa 0, etc.)
- [ ] Sobre San Antonio regenerada el aviso lista exactamente el cruce del pasillo de −4 con la vía de L7 y ningún otro
- [ ] Test unitario con un par que avisa y un par exento por `level`
