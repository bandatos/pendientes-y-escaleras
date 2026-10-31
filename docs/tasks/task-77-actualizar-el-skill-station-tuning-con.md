---
type: task
id: task-77
title: Actualizar el skill station-tuning con la convención de versiones después de publicar
state: open
date: 2026-10-30
owner: ricardo
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
related: ["[[adr-0021]]", "[[task-52]]"]
---

# Actualizar el skill station-tuning con la convención de versiones después de publicar

Es harness del proyecto: se aplica con el ok de Ricardo, que se fue antes de darlo. La convención está decidida ([[adr-0021]]) y escrita en `data/osm/README.md`; el skill todavía dice lo de antes. La línea «nunca tocar las vías» ya se aplicó hoy en `references/general.md` por instrucción directa de Ricardo.

Texto propuesto:

- `SKILL.md`, en el ciclo de versiones (hoy línea ~25), después de la primera frase: «Publicada la estación, la versión siguiente es un snapshot del servidor con `action='modify'` solo en lo que cambia (`data/osm/README.md`, «Después de publicar»): ni se regenera desde la plantilla ni parte de una versión anterior a la subida.»
- `SKILL.md`, en publicación (hoy línea ~57), al final: «Publicada la estación, la cadena sigue con snapshots del servidor, y la `-pub` de una versión existe solo cuando Ricardo pide o acepta subirla; lo chico se corrige directo en iD.»
- `.claude/agents/station-tracer.md` (hoy línea ~24), después de la primera frase: «Si la estación ya está publicada, la versión nueva es un snapshot del servidor (`data/osm/README.md`, «Después de publicar»), con `action='modify'` solo en lo que cambias.»
- `references/estaciones/{polanco,san-antonio,san-joaquin,san-pedro-de-los-pinos}.md` (línea 3): «La versión vigente es la más alta de la carpeta.» pasa a «La versión vigente es la más alta de la carpeta; lo publicado es la de su `-pub` más reciente, y desde el 30 de octubre de 2026 cada versión nueva es un snapshot del servidor.» En `polanco.md`, lista «## Versiones»: «- 08, snapshot del servidor del 30 de octubre de 2026: `layer` en 56 ways subterráneos y 4 nodos compartidos entre pasillos del −3 y los andenes.»
- `references/general.md`, catálogo de pasillos (línea ~20): «… + `level`, más `layer` cuando es subterráneo».

## Criterios de aceptación

- [ ] Ricardo da el ok al texto o lo corrige
- [ ] Las líneas quedan aplicadas y el validador documental en cero
