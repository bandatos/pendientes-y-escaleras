---
type: task
id: task-14
title: Recuperar los identificadores de escaleras que Pablo puso en Miro
state: open
date: 2026-08-26
owner: ricardo
related: ["[[task-4]]", "[[adr-0003]]"]
---

# Recuperar los identificadores de escaleras que Pablo puso en Miro

Cada escalera tiene varios códigos que conviven, ninguno claramente oficial. Pablo (Bandatos) asignó un identificador a todas las escaleras en Miro.

Falta ver cómo se extraen esos identificadores y a qué campo van (`code_identifiers` de `Stair`/`Pathway`). Los códigos físicos verificables en campo son candidatos a `ref` en OSM ([[adr-0003]]). Relacionada con [[task-4]] (identificadores oficiales del CSV de STC y los que ya traen los reportes).

## Criterios de aceptación

- [ ] Está identificado dónde y cómo Pablo capturó el identificador de cada escalera en Miro
- [ ] Los identificadores están extraídos y cargados en el campo correspondiente (`code_identifiers`)
- [ ] Está decidido cuáles de esos códigos son candidatos a `ref` en OSM
