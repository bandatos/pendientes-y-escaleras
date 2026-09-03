---
type: task
id: task-33
title: "Command prune_orphan_levels: filas de Level sin ningún stop tras las reimportaciones"
state: open
date: 2026-09-02
owner: ai
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
related: ["[[task-25]]", "[[task-12]]"]
---

# Command prune_orphan_levels: filas de Level sin ningún stop tras las reimportaciones

Reimportar una estación desde Miró sin `--reset` es idempotente pero deja filas de `Level` a las que ningún stop apunta cuando cambia el `level_id` (por ejemplo, al ganar la marca de andenes). No existe ningún command que las limpie: lo único que toca `Level` es la rama `--reset` de `MiroSchemaBuilder`, que borra y reconstruye la estación entera y arrastra sus pathways (y `StairReport.pathway` es `on_delete=CASCADE`). Al 2 de septiembre hay 11 huérfanas: `CIUDADDEPORTIVA-L9-+1`, `CONSTITUCIONDE1917-L8-+2` (solo tenía los ítems del trolebús, que el importador omite), `CONSULADO-L4-+1`, `COPILCO-L3--2`, `ERMITA-L12--3` (reemplazada por `ERMITA-L12-ANDENES-3`), `JAMAICA-L4-+3` y `MORELOS-L4-+3` (ya pobladas al reimportar con la flecha corregida), `PUEBLA-L9-+1`, `SALTODELAGUA-L8--1`, `SANTAANITA-L4-+1`, `TACUBAYA-L7--2`. Ricardo decidió no escribir el command hoy; queda para después, con `--dry-run` y reporte de lo que borraría.

## Criterios de aceptación

- [ ] Existe `prune_orphan_levels` con `--dry-run`, idempotente, que solo borra `Level` sin stops
- [ ] Corrido una vez sobre `escaleras-local` con el reporte de filas borradas
