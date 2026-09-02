---
type: task
id: task-25
title: "`import_stops` no corre sobre una base limpia"
state: open
date: 2026-09-01
owner: ricardo
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
related: ["[[task-12]]", "[[task-24]]", "[[adr-0008]]"]
---

# `import_stops` no corre sobre una base limpia

El bootstrap documentado en `api/CLAUDE.md` (`migrate` → `import_routes` → `import_stops` → …) falla en una base recién creada, verificado el 1 de septiembre de 2026 sobre una SQLite desechable. Tres causas en `api/stop/management/commands/import_stops.py`:

- Sigue escribiendo `zone_id`, campo que la migración `0007` quitó de `Stop`.
- Asigna el entero `1` a `location_type` en lugar de `location_type_id` (es una FK a `LocationType`).
- `LocationType` no tiene filas en una base nueva: ningún fixture ni migración de datos lo siembra.

`escaleras-local`, la base de desarrollo, es anterior a `0007` y por eso nunca lo mostró. El repo exige que todo se reproduzca solo con el repo, así que esto contradice la regla de replicabilidad ([[adr-0008]]).

Opciones para Ricardo:

- (a) Quitar `zone_id` del command, usar `location_type_id` y sembrar `LocationType` con una migración de datos.
- (b) Volver a agregar `zone_id` al modelo si el dato importa, y de todos modos sembrar `LocationType`.

Registro de la sesión: [[2026-09-01-sesion-miro-corchetes-entrance]]. Relacionado con la higiene técnica de [[task-12]].

## Criterios de aceptación

- [ ] Decidido (a) o (b)
- [ ] `migrate` + `import_routes` + `import_stops` corren sin error sobre una base vacía (SQLite o Postgres)
- [ ] `LocationType` queda sembrado por migración de datos o fixture versionado
