---
type: record
id: 2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion
title: "Sesión del 30 de octubre de 2026: por qué iD avisa cruces en lo subterráneo, layer y nodos de andén en el generador, y las versiones después de publicar son snapshots del servidor"
date: 2026-10-30
session: d67a8ec5-8320-4fec-b61f-44fa02cf3c07
---

# Sesión del 30 de octubre de 2026: por qué iD avisa cruces en lo subterráneo, layer y nodos de andén en el generador, y las versiones después de publicar son snapshots del servidor

Bitácora `d67a8ec5-8320-4fec-b61f-44fa02cf3c07`, 30 de octubre de 2026, rama `first-stations-josm`. Commit de partida `464ef6a` (el cierre de la sesión de L2 superficie, [[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]); el commit de esta sesión es el de cierre, pendiente al escribir este record. Ricardo se fue antes del cierre y pidió cerrar de forma autónoma; nada de lo de hoy está revisado en JOSM por él.

## Lo que disparó la sesión

Ricardo revisaba en iD la estación San Antonio (L7) publicada el 27 y vio que casi todos los ways subterráneos traían avisos de «X cruza Sendero peatonal» (la avenida, el cruce semaforizado, un drive-through), aunque llevan `level=-1`, `-2`, `-3`. Pidió investigar antes de dialogar. En paralelo retomó las explanadas de San Pedro de los Pinos ([[task-54]]).

## Lo investigado: iD y JOSM no validan igual

- iD (`modules/validations/crossing_ways.ts`, función `isLegitCrossing`; idéntica en la 2.42.3 con la que Ricardo edita): un cruce se perdona si **ambos** ways son interiores (`indoor`, `level` o `highway=corridor`) y su `level` difiere como cadena; si no, por `bridge` en uno solo, por `tunnel` en uno solo, o por `layer` distinta (0 por omisión). `location=underground`, `covered` y estar dentro del área de la estación no cuentan. Nuestro `footway` + `indoor=yes` + `level=-1` frente a una calle sin `level` queda en capa 0 y choca. Además iD avisa siempre que dos ways comparten la misma `layer` explícita, aunque uno sea túnel (#10999, enero de 2026). Issues relacionados: iD#10790 (2025, el mismo caso, cerrado sin cambio de código), iD#6227 (abierto desde 2019).
- JOSM (`CrossingWays.java`, `areLayerOrLevelDifferent`): desde el ticket 18293 (2019) trata `level` como `layer`, por eso nunca vimos el aviso; además excluye `railway=subway` del test pero sí evalúa el área de `railway=platform`.
- La comunidad no tiene una regla única: Key:layer pide `layer` casi siempre con `indoor=yes`; Key:level prefiere `level` dentro de estaciones; el hilo de 2023 «Footways in subway stations should be tagged with tunnel?» registra `tunnel`+`layer`+`indoor`+`level` como lo más frecuente en Europa.

Ricardo lo consultó con Pablo; acordaron `layer` igual al nivel en los ways subterráneos, sin `tunnel` ([[adr-0019]]).

## La vía de L7 y las vías en general

El way 320892187 (`railway=subway`, toda la L7 en una sola línea de 17 km) lleva `layer=-4` y `level=-4`. Su historial: `layer` −5 (2015), −1 (2019), −3 (2023), −4 (2024), y `level=-4` añadido en 2025 por un mapeador copiando el layer. En la red, 8 de unos 1100 ways de vía llevan `level`; los tramos en túnel de las demás líneas usan −1 o −2; L2 en Tlalpan lleva `layer=1` sin `bridge`. Con `layer=-4` en nuestro pasillo bajo las vías (nivel −4), iD avisará un cruce por estación de L7; Pablo pidió subir así y **nunca tocar el `layer` de las vías**. Lo demás (quitar `level` a la vía, −2 salvo Rosario, seccionar la línea en tramos dentro de una relación) queda en [[task-76]].

## Lo construido

- `api/utils/osm/tags.py`: `underground_layer`; `platform_spine_tags`, `footway_tags` y `steps_tags` emiten `layer` = nivel más bajo si es negativo.
- `api/utils/osm/builder.py`: `_join_platform_crossings` inserta un nodo compartido donde un way de un solo nivel cruza el contorno de un andén de ese mismo nivel ([[adr-0020]]); `api/utils/osm/validate.py`: `unjoined_platform_crossings` y el aviso correspondiente.
- Tests nuevos `test_tags.py` y `test_platform_crossings.py` (8; la suite de `utils/osm` pasa de 28 a 36; la regresión muerde). `TESTING.md` con sus dos filas.
- Regeneradas fuera de las carpetas: Portales y General Anaya byte a byte iguales; San Antonio +55 `layer`; nodos compartidos 4/6/6/6 en Polanco, San Antonio, San Joaquín y San Pedro.
- Cuatro versiones nuevas en la cadena, snapshots completos del servidor con `action='modify'` solo en lo que cambia ([[adr-0021]]): `polanco-08-claude`, `san-antonio-07-claude`, `san-joaquin-10-claude`, `san-pedro-de-los-pinos-10-claude`; verificadas en vivo sin conflictos; procedimiento, conteos y comentarios en `data/osm/publicacion-2026-10-27.md`. Su subida es [[task-75]].
- `data/osm/README.md`: convención post-publicación, catálogo con `layer` y nodo de andén, bullet «Las vías y lo ajeno». `.claude/skills/station-tuning/references/general.md`: la línea de no tocar las vías (instrucción de Ricardo); el resto del skill queda en [[task-77]].

## Explanadas de San Pedro

Ricardo decidió devolver también la oriente y resolvió las dos directamente en iD (changeset 191252788): oriente en v2 con cinco vértices; poniente con sus cuatro nodos movidos, sin el chaflán de su 03. [[task-54]] cerrada. Se borraron `correcciones/2026-10-27-jardin-poniente.osm` y `2026-10-27-explanada-oriente.md` (viven en `270df85`), y la `09-claude` de San Pedro (regenerada con ids negativos después de publicar, base de nada).

## Correcciones de Ricardo en la sesión

- Un archivo de corrección con solo lo que cambia es inverificable: todo lo que él revisa trae el contexto completo; `-pub` solo cuando él lo pide o acepta. Carpetas `correcciones/` eliminadas.
- Al cierre, sin auditor de congruencia: el crítico lee sus reglas y asume esa parte.
- El coordinador contó a L2 en Tlalpan entre los viaductos con `level=1`; Ricardo corrigió: de San Antonio Abad a Tasqueña la vía es superficial, ni túnel ni puente, salvo dos pasos bajo avenidas transversales.
- El coordinador afirmó en una línea rápida que «solo la oriente quedó editada» cuando los nodos de la poniente también se habían movido; corregido en el mensaje siguiente.

## Lo que queda abierto

[[task-75]] (subir las cuatro versiones), [[task-76]] (la vía con Pablo), [[task-77]] (skill), [[task-78]] (el validador predice iD). Notas en [[task-28]], [[task-48]], [[task-49]] y [[task-55]].
