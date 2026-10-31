---
type: decision
id: adr-0019
title: Los ways subterráneos de circulación llevan layer igual al nivel más bajo, además de indoor y level, sin tunnel; el layer de las vías no se toca
state: accepted
date: 2026-10-30
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
affects: ["api/utils/osm/tags.py", "data/osm/README.md", ".claude/skills/station-tuning/references/general.md"]
related: ["[[adr-0013]]", "[[adr-0010]]", "[[adr-0011]]", "[[adr-0004]]", "[[task-76]]", "[[task-78]]"]
---

# Los ways subterráneos de circulación llevan layer igual al nivel más bajo, además de indoor y level, sin tunnel; el layer de las vías no se toca

## Contexto y planteamiento del problema

El catálogo vigente ([[adr-0013]]) ponía `layer` y `location=underground` solo en los andenes subterráneos y dejaba pasillos y escaleras con `highway=footway`/`steps` + `indoor=yes` + `level`, apoyado en la frase del wiki de Key:layer «ways in buildings… should be mostly described with level instead of layer» y en que JOSM, desde su ticket 18293, trata `level` como `layer` en el test de cruces. iD no lo hace: en `isLegitCrossing` el `level` solo exime cuando **ambos** ways son interiores, y una calle de superficie no lleva `indoor` ni `level`, así que un pasillo nuestro de −1 queda en capa 0 y aparece cruzando la avenida, el cruce semaforizado y el drive-through. Ricardo lo vio en San Antonio el 30 de octubre de 2026: ocho avisos en el sendero del andén. El riesgo no es estético: las opciones que iD ofrece («Añadir un túnel», «Conectar») cortan el pasillo o lo sueldan a la calle, y cualquier mapeador puede aplicarlas.

## Criterios de decisión

- Que iD y JOSM callen ante un cruce en planta entre un pasillo subterráneo y la superficie.
- Respetar el wiki: Key:layer dice que `layer` va casi siempre acompañado de `tunnel`, `bridge`, `steps`, `elevator`, `covered` o `indoor=yes`; Key:level prefiere `level` dentro de estaciones. Las dos conviven.
- No llamar túnel a un vestíbulo.
- No depender de corregir datos ajenos.

## Decisión

Todo way nuestro de circulación subterráneo (senda de andén, pasillo, escalera) lleva `layer` igual al nivel más bajo que toca, como entero, solo cuando ese nivel es negativo (`level=-2` → `layer=-2`; `level=-1;0` → `layer=-1`), y conserva `indoor=yes` + `level`. Sin `tunnel`. Un way de nivel 0 o superior no lo lleva; los puentes de Tlalpan reciben `bridge=yes` + `layer=1` del bloque `tags` de la plantilla, que se aplica después y manda. Los andenes siguen con `layer` + `location=underground`, ahora como caso particular de la regla. Implementado en `underground_layer` (`api/utils/osm/tags.py`). Acordado por Ricardo con Pablo.

El `layer` de las vías (`railway=subway`) no se toca, aunque esté mal: Pablo, transmitido por Ricardo, «mientras tanto puedes subir los cambios con el layer que tienen las vias (aunque aparezca el conflicto) y decirle a Claude que nunca toque el layer de las vías». Quitarle `level` a la vía es consenso con Pablo, pero como edición de la comunidad, no de un turno nuestro. Con la vía de L7 en `layer=-4`, nuestro pasillo bajo las vías (nivel −4, `layer=-4`) producirá en iD un aviso de cruce por estación; se acepta. Lo que se le proponga a la comunidad sobre la vía es [[task-76]].

## Alternativas descartadas

- **`layer` + `tunnel=yes`**: lo más frecuente en estaciones europeas según el sondeo del foro de 2023, pero contradice cuatro ADR y el propio issue iD#10790 cuestiona llamar túnel a una cámara de estación.
- **Dejar solo `level` y que quien revise pulse «Ignorar»**: sin costo hoy, con el riesgo de que otro usuario de iD «arregle» el aviso fragmentando el pasillo.
- **`location=underground` en los pasillos**: no cuenta en el validador de iD; podría añadirse por semántica, no decidido.
- **`layer` una unidad por debajo de la vía en el pasillo de −4**: correcto en el orden físico, pero depende de un dato ajeno que ha cambiado cinco veces; Pablo prefirió aceptar el aviso.

## Consecuencias

- Las cuatro estaciones subterráneas publicadas reciben una versión nueva con `layer` en 235 ways ([[task-75]]).
- En iD desaparecen los avisos de pasillos contra calles y edificios (22, 33, 56 y 27 pares en Polanco, San Antonio, San Joaquín y San Pedro) y aparece uno por estación con la vía.
- JOSM pasa a evaluar los pasillos de −3 contra el área del andén de −3: lo resuelve [[adr-0020]].
- Enmienda a [[adr-0013]]: su frase «nunca `tunnel=yes` en pasillos interiores, que van con mapeo indoor y `level`» sigue vigente; se le suma el `layer`.
- Cualquier esquema de `layer` depende del contexto: [[task-78]] propone que el validador prediga los avisos de iD.
