---
type: record
id: 2026-08-05-integracion-del-monorepo
title: Integración del monorepo
date: 2026-08-05
---

# Integración del monorepo

Sesión del 5 de agosto de 2026 (Claude Code, modo duo). Se convirtió este repo en monorepo integrando las historias completas de los dos subproyectos, con cada mensaje de commit prefijado por subproyecto mediante git-filter-repo:

- `bandatos/escaleras_survey_ws` → `api/` (46 commits, prefijo `[api]`, rama main)
- `bandatos/escalerasSurvey` → `vue/` (181 commits, prefijo `[vue]`, rama refactor-feature)

Antes de importar se commitearon los cambios pendientes en cada repo original. Todo vive en la rama `monorepo`; los repos originales quedaron intactos.

Además: venv de api creado e instalado (Python 3.14, Django 5.2.7), `yarn install` en vue con yarn.lock trackeado como lockfile único (se eliminó package-lock.json y la línea de .gitignore que ignoraba yarn.lock), y reorganización de la raíz: GTFS canónico en `data/gtfs/`, CSVs crudos en `data/raw/`, insumos externos en `data/sources/`, prototipo estático en `prototype/`, README reescrito.

Hallazgos de la sesión: `token.txt` contenía un PAT de GitHub trackeado en repo público (ver [[task-1]]); GitHub Pages sirve el prototipo desde la raíz de main en bandatos.org/pendientes-y-escaleras (ver [[task-2]]); `estaciones-match-stops.csv` difiere entre api y vue (ver [[task-3]]); `data/raw/escaleras_metro.csv` contiene los identificadores oficiales STC por escalera, nunca importados, y el campo `Stair.code_identifiers` diseñado para recibirlos sigue vacío (ver [[task-4]]).
