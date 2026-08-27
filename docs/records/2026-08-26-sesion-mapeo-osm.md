---
type: record
id: 2026-08-26-sesion-mapeo-osm
date: 2026-08-26
---

# Sesión del 26 de agosto de 2026: cómo mapear en OpenStreetMap lo que está en Miró y en la base

Objetivo de la sesión: definir una forma de facilitar el mapeo en OpenStreetMap (OSM) de escaleras, escaleras eléctricas, elevadores, andenes, pasillos y accesos del Metro CDMX a partir de lo ya relevado en el tablero de Miró y en la base de datos. Modo duo: coordinador en diálogo con Ricardo, ejecutores Opus/Sonnet para el volumen.

## Qué se hizo

- **Transcripción** de la reunión del 19 de agosto (73 min, 4 hablantes) con el pipeline de `written.django`: [[2026-08-19-reunion-bandatos-raw]] y [[2026-08-19-reunion-bandatos-limpia]]. La reunión dejó sin cerrar la fecha de la sesión de trabajo del colectivo (opciones dichas: domingo 23, sábado 29 o domingo 30 de agosto, «tipo 3 de la tarde»). La reunión ya orientaba: JOSM como editor, andén como polígono, escaleras conectadas al polígono por nodo, sin relaciones, y la idea de generar un «cuadro estándar» por estación desde Miró que el mapeador acomode.
- **Reconocimiento del repo**: solo 195 coordenadas en todo el sistema (una por estación, GTFS); ninguna escalera, pathway ni acceso tiene lat/lon; cero rastro de OSM en el código. 185 reportes de campo (oct 2025, 23 estaciones, 144 funcionan / 41 no), todos sobre `Stair` legado; 159 traen el código físico STC en `code_identifiers` (ver [[task-4]]).
- **Recuperación de la base**: `api/.env` no había viajado al monorepo (gitignorado); los originales están en `~/dev/open/`. La base `escaleras-local` se recuperó del cluster PostgreSQL 17 del disco de la Surface (`/run/media/rick/Local Disk/Program Files/PostgreSQL/17/data`), sin mojibake (el `dump.json` sí lo tenía: 55 de 163 estaciones). Respaldo en `~/databases/escaleras-local-2026-08-26.sql`.
- **Migración desde Miró**: `preview_miro_schema --all-stations` (persiste pese al nombre) pasó de 3 a **98 estaciones con topología** (1 534 stops, 384 niveles, 2 128 pathways). Las 4 importadas en la Surface se rehicieron con `--reset` (Tacubaya y Mixcoac no tenían niveles). 30 frames sin match: 20 «(en proceso)», 3 leyendas, 7 diferencias de nombre → [[task-7]].
- **Auditoría de posiciones en el mapa d3**: `recover_viz_features.py` pegaba filas del CSV y estaciones por posición (`zip`) con dos criterios de orden distintos; ahora resuelve por `stop_id`. Solo Iztacalco/Iztapalapa estaban cruzadas en esta base. Copia de vue del CSV eliminada; [[task-3]] cerrada.
- **Catálogos OSM** alineados campo por campo con nuestros modelos (informe completo en [[2026-08-26-alineacion-catalogos-osm]]; lo decidido está en [[adr-0003]] y [[adr-0004]]). Hallazgos clave: no existe tabla GTFS-Pathways → OSM; el estado de funcionamiento no va a OSM (decisión cerrada de la comunidad); la capa interior del Metro en OSM está vacía (7 escaleras eléctricas en la ciudad, de Pablo/Bandatos); 58 `stop_area` activas; `ref` ausente en 446 de 447 accesos.
- **Herramientas**: comparación JOSM / iD / Rapid / Vespucci / Every Door / MapRoulette → [[adr-0002]]; informe completo en [[2026-08-26-herramientas-mapeo-kml-plantillas]]. Análisis del KML `data/StatioArea-and-lines.kml` (187 polígonos, 12 líneas; L8 arrastra el ramal de L12; la LineString «Línea A» de 29 km es la Línea B; 3 estaciones en construcción) y del rumbo de andenes contra `shapes.txt` → [[adr-0005]] (medición en `data/analysis/kml-estaciones-orientacion.csv`).
- **Agrupamiento en familias arquitectónicas** (15 familias, firma topológica) → [[2026-08-26-agrupamiento-estaciones-familias]] y [[task-8]]; criterio en [[adr-0006]].
- **Cruce de accesos OSM** (447 nodos) contra nuestros 445 stops de acceso: 7 estaciones emparejables completas por rumbo, 55 parciales; los nombres de OSM no sirven (son el nombre de la estación). 33 «Andén» guardados como acceso → [[task-16]]. Otros 129 nodos de acceso de OSM caen en 35 estaciones que aún no tenemos capturadas (Buenavista, Indios Verdes, La Raza, Merced, Pantitlán…): insumo para priorizar el siguiente levantamiento. Cruce por estación guardado en `data/analysis/osm-accesos-cruce.csv`.
- **Fuentes de accesos**: ninguna pública con coordenada por acceso (Wikipedia y STC dan nombres; Datos Abiertos CDMX solo estaciones).
- **LLM**: sin benchmarks públicos de modelos baratos en tareas espaciales; patrón reusable en `~/dev/ibero/ocsa` (`RequestGemini`) → [[task-15]].
- **Política OSM**: subir datos de nuestra base cuenta como importación (wiki, foro con 14 días, cuenta `_Import`, conflación; licencia del GTFS vs ODbL sin verificar) → [[task-11]]; foro México y hilo de 2025 → [[task-10]].

## Decisiones menores del cierre

- El polígono de estación completa en OSM (pregunta abierta de la reunión del 19) queda para cuando se dibuje la primera estación modelo; sin tarea.
- Las transcripciones de la reunión del 19 quedan como `record` ([[2026-08-19-reunion-bandatos-limpia]], [[2026-08-19-reunion-bandatos-raw]]) por decisión de Ricardo, aunque en el diálogo se había aceptado `reference`.
- Los dos informes grandes de investigación se conservan como referencias: [[2026-08-26-alineacion-catalogos-osm]] y [[2026-08-26-herramientas-mapeo-kml-plantillas]]. Los CSV de medición viven en `data/analysis/`. Los scripts de auditoría de posiciones (`api/.claude/audit_*.py`) se borraron: `recover_viz_features` ya reporta filas sin resolver y colisiones.

## Tareas abiertas en la sesión

[[task-7]], [[task-8]], [[task-9]], [[task-10]], [[task-11]], [[task-12]], [[task-13]], [[task-14]], [[task-15]], [[task-16]], [[task-17]], [[task-18]], [[task-19]], [[task-20]].

## Decisiones

[[adr-0002]], [[adr-0003]], [[adr-0004]], [[adr-0005]], [[adr-0006]], [[adr-0007]], [[adr-0008]].

## Cambios en el harness

`CLAUDE.md` raíz: sección «Replicabilidad». `vue/CLAUDE.md`: módulo de mapeo OSM en régimen vibecoding. `api/CLAUDE.md`: gotchas de `is_double`, `preview_miro_schema` y restauración de la base.
