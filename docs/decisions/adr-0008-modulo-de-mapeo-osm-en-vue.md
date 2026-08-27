---
type: decision
id: adr-0008
title: Módulo de mapeo OSM en Vue en régimen vibecoding y regla de replicabilidad del repo
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: confirmed
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["vue/CLAUDE.md", "CLAUDE.md"]
---

# Módulo de mapeo OSM en Vue en régimen vibecoding y regla de replicabilidad del repo

## Contexto

Ricardo no quiere gastar decisiones en el código del visor/generador de mapas: le importa cómo se comporta, no cómo se implementa. Y el repo es público y lo trabajan varias personas: hoy se detectó la tentación de corregir datos a mano en la base.

## Resultado

- El módulo de mapeo OSM en `vue/` se desarrolla en modo vibecoding: Ricardo define el comportamiento; los ejecutores deciden la implementación dentro de las convenciones, sin consultarle cada decisión de código. Fuera del módulo aplica el régimen normal. Escrito en `vue/CLAUDE.md`.
- Todo debe reproducirse solo con el repo: ninguna corrección de datos vive solo en la base; va por management command, migración de datos o el CSV/GTFS de origen. Escrito en `CLAUDE.md` raíz, sección «Replicabilidad».

## Más información

[[2026-08-26-sesion-mapeo-osm]].
