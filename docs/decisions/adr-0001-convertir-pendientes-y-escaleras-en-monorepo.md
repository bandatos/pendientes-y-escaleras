---
type: decision
id: adr-0001
title: Convertir pendientes-y-escaleras en monorepo con historia integrada
state: accepted
date: 2026-08-06
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-05-integracion-del-monorepo]]"]
affects: ["api/", "vue/"]
---

# Convertir pendientes-y-escaleras en monorepo con historia integrada

## Decisión

Este repo deja de ser un contenedor de datos sueltos y pasa a ser el monorepo del proyecto: `api/` (Django) y `vue/` (Vue 3) se integran con su historia completa de git, cada commit importado con prefijo `[api]` o `[vue]`, mediante git-filter-repo (reescritura a subdirectorio + prefijo de mensaje) y merges con `--allow-unrelated-histories`. La rama de integración es `monorepo`; los repos originales no se tocan.

## Porqué

Ricardo mantiene solo los tres repos y la separación duplicaba información (sobre todo datos GTFS y catálogos repetidos entre la raíz, api y vue) y fragmentaba el contexto. Un solo repo con linajes identificables conserva la trazabilidad de cada subproyecto sin perder historia.

## Alternativas descartadas

- `git subtree`: preserva historia pero no permite prefijar los mensajes.
- Importar la rama `main` de vue: se eligió `refactor-feature` por contener el trabajo más reciente (incluye su CLAUDE.md); su historia ya contenía a main.

## Convenciones derivadas

- Commits nuevos que toquen un solo subproyecto llevan prefijo `[api]` o `[vue]`.
- Gestor de paquetes del frontend: yarn (yarn.lock trackeado, package-lock.json eliminado).
