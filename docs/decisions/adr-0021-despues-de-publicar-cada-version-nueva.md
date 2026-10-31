---
type: decision
id: adr-0021
title: Después de publicar, cada versión nueva de una estación es un snapshot completo del servidor con action solo en lo que cambia; pub solo cuando Ricardo pide o acepta subir; sin carpetas de correcciones
state: accepted
date: 2026-10-30
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
affects: ["data/osm/README.md", "api/stop/management/commands/publish_station_osm.py", ".claude/skills/station-tuning/SKILL.md", ".claude/agents/station-tracer.md"]
related: ["[[adr-0016]]", "[[adr-0015]]", "[[task-55]]", "[[task-77]]", "[[task-54]]"]
---

# Después de publicar, cada versión nueva de una estación es un snapshot completo del servidor con action solo en lo que cambia; pub solo cuando Ricardo pide o acepta subir; sin carpetas de correcciones

## Contexto y planteamiento del problema

La carpeta `correcciones/` nació el 27 de octubre ([[task-54]]) para un caso mínimo, el jardín de San Pedro, y heredaba su forma: un archivo con solo los elementos que cambian, contra ids del servidor. Hoy se armaron así cuatro correcciones masivas (235 ways con `layer` y 22 nodos nuevos) y Ricardo no pudo revisarlas: «se pierde el contexto completo de los elementos que hay alrededor»; en JOSM se abren como islas de líneas en el vacío y juzgar un nodo a medio metro de otro es inverificable. Además la `09-claude` de San Pedro, regenerada con ids negativos después de publicar, era una trampa: subirla duplicaría la estación.

## Criterios de decisión

- Que Ricardo pueda revisar cualquier cambio viendo lo que lo rodea, sin pasos extra en JOSM.
- Que el repo guarde el estado del servidor contra el que se propuso el cambio.
- Una sola cadena de versiones por estación, numeración consecutiva, sin categorías nuevas que manejar.
- Que `-pub` signifique una sola cosa.

## Decisión

- Una estación tiene una sola cadena `<slug>-NN-<autor>.osm`, consecutiva, antes y después de publicar. Una vez publicada, toda versión nueva es un **snapshot completo** del estado vivo del servidor en el bbox de la estación (nuestra estación entera, calles, edificios, la vía, relaciones del `map.json`), con ids y versiones del servidor y sin `action`, donde solo lo que cambia lleva `action='modify'` y los nodos nuevos id negativo. Conserva `upload='never'` hasta que exista su `-pub` (decisión mecánica del coordinador, nombrada a Ricardo el 30 de octubre sin respuesta).
- Nada se regenera desde la plantilla después de publicar (`export_station_osm` solo con `--out`, fuera de la carpeta), y una versión anterior a la subida no sirve de base.
- `-NN-pub.osm` existe solo cuando Ricardo pide subir esa versión o acepta la oferta; una versión para que revise y el modelo aprenda lleva su autor y nunca `pub`. En un snapshot `publish_station_osm` solo quita `upload='never'` (probado hoy).
- No hay carpetas `correcciones/` ni archivos sueltos de cambios. Lo chico se corrige directo en iD (como hizo Ricardo con las explanadas de San Pedro); lo masivo va por JOSM con una versión de la cadena.
- Antes de subir, `check_station_osm_live`; un snapshot recién bajado no debe dar conflicto.

## Alternativas descartadas

- **Archivo mínimo + descargar el contexto en JOSM a la misma capa**: funciona, pero depende de que Ricardo haga el paso cada vez y el repo no guarda lo que vio.
- **Lo que Ricardo matizó al aceptar**: «me gusta tu idea, pero sin negativos, son muy difíciles de manejar, simplemente consecutivos y -pub para lo que se sube, creo que no hay pierde así». El coordinador lo leyó como numeración simple y consecutiva, sin más categoría que `-pub`, y mantuvo el autor `-claude` en los nombres; a qué se refiere «sin negativos» no se le preguntó. Ricardo confirmó el 30 de octubre, al leer el cierre, que la lectura del coordinador (numeración consecutiva con sufijo de autor y `-pub` solo para lo que sube) es exactamente lo que quería.

## Consecuencias

- Hoy: `polanco-08-claude`, `san-antonio-07-claude`, `san-joaquin-10-claude` y `san-pedro-de-los-pinos-10-claude` son snapshots; las cuatro carpetas `correcciones/` se borraron (los archivos del 27 viven en `270df85`) y también la `09-claude` de San Pedro.
- El skill `station-tuning` y el agente `station-tracer` deben decirlo ([[task-77]]).
- `diff_station_osm` sobre un snapshot empareja solo por cercanía, porque no hay etiquetas de trazo.
