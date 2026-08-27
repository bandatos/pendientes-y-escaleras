---
type: decision
id: adr-0007
title: PostgreSQL escaleras-local restaurada de la Surface como base de desarrollo; SQLite y dump.json quedan como histórico
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["api/.env.template", "api/CLAUDE.md"]
---

# PostgreSQL escaleras-local restaurada de la Surface como base de desarrollo; SQLite y dump.json quedan como histórico

## Contexto

El monorepo no traía `api/.env` (gitignorado) y `api/dump.json` tenía 55 de 163 nombres de estación con acentos rotos (`U+FFFD`), lo que impedía cruzar 26 frames de Miró. En el disco de la Surface (`Program Files/PostgreSQL/17/data`) estaba `escaleras-local` sana y más reciente (incluía 4 estaciones migradas desde Miró en mayo).

## Resultado

La base de desarrollo es PostgreSQL `escaleras-local` en local (`POSTRGRESQL_DB=True`), restaurada del cluster de la Surface. Respaldo persistente en `~/databases/escaleras-local-2026-08-26.sql` (ruta habitual de respaldos de Ricardo). `api/db.sqlite3`, la copia `escaleras-local-apr18` y la copia del data dir en `/tmp` se eliminaron; `dump.json` se conserva en el repo como histórico, no como fuente. En local `AWS_STORAGE_BUCKET_NAME` va vacío (las llaves S3 dan 403 y `collectstatic` fallaba), aceptando que `EvidenceImage` apunte a filesystem.

### Consecuencias

- **Malo:** quien clone el repo necesita el respaldo o correr toda la carga desde CSV + Miró; documentarlo es parte de [[task-9]].

## Más información

[[2026-08-26-sesion-mapeo-osm]].
