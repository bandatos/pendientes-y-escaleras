---
type: decision
id: adr-0010
title: "Convenciones de mapeo indoor para el generador de .osm: líneas footway con indoor=yes, niveles con punto y coma, eléctricas conveying=forward y plantillas estructurales"
state: accepted
date: 2026-09-02
origin: ricardo
deliberation: confirmed
rationale: recorded
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
affects: ["api/utils/osm/tags.py", "api/stop/management/commands/export_station_osm.py", "data/osm/templates/"]
related: ["[[adr-0004]]", "[[adr-0006]]", "[[2026-09-02-investigacion-osm-indoor-y-estado-l2-l7]]"]
---

# Convenciones de mapeo indoor para el generador de .osm: líneas footway con indoor=yes, niveles con punto y coma, eléctricas conveying=forward y plantillas estructurales

# Convenciones de mapeo indoor para el generador de .osm: líneas footway con indoor=yes, niveles con punto y coma, eléctricas conveying=forward y plantillas estructurales

## Contexto y planteamiento del problema

[[adr-0004]] fijó las convenciones de etiquetado, pero al construir el primer generador y dibujar Portales y San Pedro de los Pinos quedaron ambigüedades que había que cerrar antes de escribir una sola etiqueta: el ADR pide «Simple Indoor Tagging puro (`indoor=room|corridor|area|level`)» en una viñeta y «`highway=footway` + `indoor=yes`» en otra; no dice si los niveles múltiples van con punto y coma o con guion; no dice cómo se expresa el sentido de una escalera eléctrica ni cómo se reparten `conveying`, `incline` y `oneway:foot`; y [[adr-0006]] dejó abierto cómo se empareja una plantilla con el grafo de cada estación. La investigación de [[2026-09-02-investigacion-osm-indoor-y-estado-l2-l7]] mostró que las estaciones de Viena (Taubstummengasse, Zieglergasse) resuelven todo esto de una forma consistente, y que Balbuena, el único precedente en el Metro, lo hace con errores.

## Criterios de decisión

- Que un router peatonal (OSRM, GraphHopper) pueda recorrer la estación: líneas, no áreas.
- Que el sentido de cada elemento sea verificable con una sola regla, sin ambigüedad `forward`/`backward`.
- Que la misma plantilla sirva a todas las estaciones de la familia sin editarla.
- Que nada de lo generado toque objetos existentes de OSM hasta que [[task-11]] se resuelva.

## Opciones consideradas

- **Líneas `highway=corridor`** — lo que recomienda `Tag:indoor=corridor`; OSRM y GraphHopper lo ignoran.
- **Áreas `indoor=corridor|room` por espacio, sin líneas** — SIT puro; no rutea.
- **`conveying=forward|backward` según el orden de nodos** — lo que dice el wiki; dos formas de decir lo mismo.
- **Emparejar plantillas por `miro_id`** — rompe la reutilización: cada estación tiene ids distintos.

## Resultado

Ricardo aceptó la propuesta sin modificarla («Ok con las convenciones»). Queda así, y donde contradice a [[adr-0004]] esta decisión prevalece:

- **Pasillos y vestíbulos** como líneas `highway=footway` + `indoor=yes` + `level`. El único polígono es el andén (`railway=platform` + `public_transport=platform` + `area=yes` + `subway=yes` + `level` + `name`; laterales con `destination`; subterráneos con `layer=<level>` + `location=underground`, sin `tunnel=yes`). Por ahora no se dibujan polígonos de cuartos ni de nivel ni de estación completa. Enmienda la viñeta «Esquema interior» de [[adr-0004]]: `indoor=yes` en líneas es la práctica de Viena y la mayoritaria en OSM.
- **Niveles múltiples** con punto y coma ascendente, `level=-2;-1`; nunca rango con guion. `level:ref` solo donde la base tiene `level_name` (hoy, «Andenes»): enmienda el «siempre las dos» de [[adr-0004]] a «las dos cuando exista el rótulo».
- **Escaleras fijas**: `highway=steps` + `indoor=yes` + `level=a;b`. Bidireccionales dibujadas de abajo hacia arriba con `incline=up`; unidireccionales dibujadas en el sentido de la flecha de Miró con `incline` según la diferencia de nivel en ese sentido.
- **Escaleras eléctricas**: siempre `conveying=forward` con la vía dibujada en el sentido de viaje e `incline` según ese sentido. Unidireccional (`is_bidirectional=0`) = la flecha de Miró, `from_stop → to_stop`, que el equipo dibujó con intención; bidireccional = `conveying=reversible`, dibujada hacia arriba.
- **Todo pathway con `is_bidirectional=0`** lleva además `oneway:foot=yes`, nunca `oneway`: `conveying` describe la máquina y `oneway:foot` el paso permitido, y los routers peatonales solo leen el segundo. Confirma la viñeta de dirección de [[adr-0004]].
- **Accesos**: nodo `railway=subway_entrance` + `entrance=<Stop.entrance>` + `name=<stop_name>` + `level=0`, sin `ref` hasta que [[task-18]] dé las letras.
- **Torniquetes**: nodo `barrier=turnstile` + `amenity=ticket_validator` insertado desde la plantilla sobre el pasillo del vestíbulo; el grafo no los tiene como aristas.
- **Archivo**: ids negativos únicos, `upload='never'`, sin objetos existentes, sin nodo de estación ni relación `stop_area`. Etiquetas de traza `note:stop_id`, `note:pathway_id`, `note:miro_id` para la revisión local, retiradas con `--no-trace` antes de cualquier subida.
- **Plantillas** ([[adr-0006]]): el emparejamiento es estructural, por sufijo del `stop_id` (`P-01`, `N-03`, `E-01`) más un índice ordinal entre pathways paralelos con mismo origen, destino y modo; nunca por `miro_id`.
- **`gtfs:*`** de [[adr-0004]] no se emite todavía: falta decidir el sufijo de feed ([[task-27]]).

### Consecuencias

- **Bueno:** una sola regla verificable por sentido (`conveying` siempre `forward`, la vía es la verdad); Xola exporta limpia con la plantilla de Portales sin tocarla; el archivo se fusiona sin conflictos sobre la descarga real.
- **Malo:** `indoor=yes` no lo renderiza el visor indoor recomendado en [[adr-0004]]; sin polígonos de cuarto no hay huella de vestíbulos; la conexión con los accesos ya existentes en OSM es una pasada manual por estación; el índice entre paralelos es arbitrario y el `miro_id` viaja solo en el comentario de la plantilla.

### Cómo se comprueba

`api/utils/osm/validate.py` corre en cada exportación: cada vía con `level`, `incline`/`conveying` coherentes con el orden de niveles, BFS desde cada acceso hasta cada andén, sin nodos duplicados. El catálogo de etiquetas vive solo en `api/utils/osm/tags.py`, semilla de [[task-19]].

## Más información

[[2026-09-02-sesion-primeras-dos-estaciones-josm]], [[2026-09-02-investigacion-osm-indoor-y-estado-l2-l7]], `data/osm/README.md`.
