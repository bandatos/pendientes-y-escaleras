---
type: record
id: 2026-09-02-sesion-primeras-dos-estaciones-josm
title: "Sesión nocturna: generador de .osm y primeros trazos de Portales y San Pedro de los Pinos"
date: 2026-09-02
related: ["[[adr-0002]]", "[[adr-0004]]", "[[adr-0006]]"]
---

# Sesión nocturna: generador de .osm y primeros trazos de Portales y San Pedro de los Pinos

Sesión del 1 al 2 de septiembre de 2026, de las 23:30 a las 02:00 aproximadamente, bitácora `session_0144VaYsehb6bUafLXeX4aET`, rama `first-stations-josm`. Ricardo pidió una sesión distinta: una sola intervención suya y después piloto automático hasta tener dos estaciones mapeadas en JOSM, o su aproximación, listas para revisar por la mañana. Encargo textual: «una estación de la línea 2 sin correspondencia (ni terminales) que tenga un modelo que se repita y una de la línea 7, también sin correspondencias».

## Cómo se corrió

En régimen duo: el coordinador (Fable 5.1) dialogó con Ricardo y ejecutores Opus cargaron el volumen. Seis ejecutores en secuencia parcial: barrido del grafo documental (ADR, tareas, referencias), investigación OSM (wiki, estaciones modelo en Viena, Berlín y París vía Overpass, estado de las Líneas 2 y 7), instalación de JOSM en el home, extracción de los grafos de seis estaciones candidatas de la base, construcción del generador y revisión técnica con correcciones. El cierre documental lo hizo un fork.

## La intervención de Ricardo

Respondió en una sola pasada: rama `first-stations-josm`; Portales para Línea 2; para Línea 7 no San Joaquín («creo que no se parece tanto a las de la 7»), ni Polanco ni Auditorio, ni correspondencias ni terminales: se eligió San Pedro de los Pinos, que ya estaba extraída y tiene en la base los mismos 14 nodos, 26 aristas y modos que San Joaquín; difieren en la dirección de almacenamiento de algunas aristas bidireccionales, y esa diferencia hizo fallar al generador con San Joaquín hasta canonicalizar las aristas bidireccionales. Aceptó el método (generador con plantillas por familia), las tres convenciones propuestas (líneas `highway=footway` + `indoor=yes`, niveles múltiples con punto y coma, escaleras eléctricas `conveying=forward` en el sentido de la vía) y el nodo de torniquete. Sobre el sentido de las eléctricas unidireccionales: «Las unilaterales siempre suben en casi todas las de la línea 7, eso estoy seguro que se puede ver por convención de las flechas, chécalo porque sí le pusimos muchísima atención y tiempo al hacer el miró». Pidió usar el crítico en las etapas que el coordinador prefiriera. No hizo falta que instalara nada.

## Qué se construyó

- Comando `export_station_osm` en `api/stop/management/commands/export_station_osm.py` y paquete `api/utils/osm/` (`tags.py` como catálogo único de etiquetas, `graph.py` cargador que no colapsa pathways paralelos, `geometry.py` marco local métrico en Python puro, `template.py`, `document.py` con registro de nodos y soldadura por nivel, `builder.py`, `validate.py`, `preview.py`).
- Plantillas `data/osm/templates/tlalpan-surface.json` (familia D, superficie de Calzada de Tlalpan) y `data/osm/templates/l7-deep-cascade.json` (familia G, profunda de L7 en cascada). El emparejamiento es estructural: sufijo del `stop_id` (`P-01`, `N-03`, `E-01`) más un índice ordinal entre paralelos; nunca por `miro_id`, para que la misma plantilla sirva a las estaciones hermanas. En la base, la familia de Portales confirmada es Xola, Nativitas, Viaducto, Villa de Cortés y General Anaya; Ermita no tiene stops ni pathways cargados y queda provisional.
- Salidas `data/osm/portales.osm` (27 nodos, 14 vías) y `data/osm/san-pedro-de-los-pinos.osm` (41 nodos, 30 vías), previews SVG por nivel en `data/osm/preview/` y `data/osm/README.md` con el esquema de plantilla, las convenciones y la lista «Supuestos» para revisión.
- Anclaje: centroide del polígono KML; rumbo de Portales 8,2° del GTFS (coincide con las vías de OSM, 8,0° a 8,3°); San Pedro 6,5° medido sobre la Avenida Revolución en OSM, porque el GTFS no tiene shapes de L7 y la elongación del KML es baja.
- Los tres accesos que ya existen en OSM (dos de Portales, uno de San Pedro) se copiaron a menos de 10 cm como nodos nuevos; el acceso oriente de San Pedro se colocó en espejo.

## Validación

XML bien formado, ids negativos únicos, `upload='never'`, cada vía con `level`, sin nodos duplicados a menos de 0,3 m, BFS desde cada acceso alcanza la línea interior de cada andén, `incline` y `conveying` coherentes con el orden de niveles. Generación determinista: regenerar en proceso nuevo produce archivos idénticos byte a byte. Xola exporta limpia contra la plantilla de Portales. Ambos archivos abrieron en JOSM sin `IllegalDataException`; el único aviso esperado en JOSM son los ocho cruces del contorno del andén de San Pedro con las líneas de nivel −3 que salen del andén, inherentes al modelo. Tests: mismas 16 fallas previas, delta cero; la colección de `pytest` sigue rota por `utils/miro/scratch`.

## JOSM

Instalado en el home: `~/.local/share/josm/josm-tested.jar` (19613), lanzador `~/.local/bin/josm`, plugins indoorhelper, pt_assistant, ShapeTools y utilsplugin2, preferencias con Remote Control y modo experto. El Java del sistema es headless, así que el lanzador usa un Temurin JRE 21 bajo `~/.local/share/jdk/` y pasa tres `--add-exports` sin los cuales JOSM detiene el arranque con un diálogo. El estilo «Indoor» no viene en el jar; indoorhelper registra su propio `sit.mapcss`.

## Sentido de las escaleras eléctricas, medido

La comprobación que pidió Ricardo se hizo sobre toda la base, no solo sobre las dos estaciones: escaleras eléctricas unidireccionales por diferencia de nivel entre sus extremos, en Línea 7 77 suben, 18 bajan y 0 quedan al mismo nivel; en toda la red 241 suben, 50 bajan y 4 quedan al mismo nivel. «Casi todas suben» se sostiene (81 % en L7), las flechas llevan sentido real y las de bajada existen y aparecerán en estaciones hermanas.

## Desviaciones

- Un ejecutor abrió JOSM en el escritorio de Ricardo con un archivo truncado a propósito (control negativo) y la ventana de error lo despertó; después, un segundo diálogo de la JVM le exigió pulsar Continuar. Se corrigió el lanzador y se ordenó abrir JOSM solo lo indispensable. Registrado como feedback global.
- Los trazos recibieron una revisión técnica de un ejecutor general antes de congelarse, no del crítico; el crítico corrió después, sobre la sesión completa, y sus hallazgos se aplicaron: la afirmación de isomorfismo con San Joaquín corregida, las cifras de sentido de las eléctricas medidas en toda la base, la regla de escaleras fijas unidireccionales precisada en [[adr-0010]], la familia de Portales acotada a lo confirmado en la base, el valor por defecto de las etiquetas de traza llevado a [[task-27]] y el endpoint del Remote Control abierto como task.
- La revisión técnica encontró que el generador emitía `highway=footway` para elevadores en silencio; ahora falla con error nombrado. También corrigió `oneway` por `oneway:foot`, retiró `tunnel=yes` de los andenes, añadió `bridge=yes` + `layer=1` al puente de Portales vía plantilla y puso el `miro_id` en el comentario de cada arista paralela.

## Supuestos que Ricardo revisa

Son los de `data/osm/README.md`: sentido de las eléctricas unidireccionales igual a la flecha de Miró (todas suben en estas dos estaciones); lado de los andenes en San Pedro por circulación por la derecha, coincidente con el grafo pero sin observación en sitio; dimensiones inventadas (andén 150 × 10 m en Portales, 150 × 5 m con 8 m de vías en San Pedro); San Pedro sin torniquetes porque el vestíbulo de torniquetes solo recibe escaleras; forma de la losa del puente de Portales; el andén de Portales de 10 m encierra las dos vías de OSM y roza la calzada central; los accesos de San Pedro siguen el nodo existente de OSM (u ≈ +5,6 m) mientras Wikipedia los pone en Calle 4 y Calle 9 (u ≈ −31 m); el nodo de estación de San Pedro en OSM está 31 m al oriente del eje y lleva `service=yard`.

Decisiones: [[adr-0010]]. Investigación: [[2026-09-02-investigacion-osm-indoor-y-estado-l2-l7]].
