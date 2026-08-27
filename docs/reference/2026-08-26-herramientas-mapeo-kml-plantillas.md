---
type: reference
id: 2026-08-26-herramientas-mapeo-kml-plantillas
title: Herramientas de mapeo, análisis del KML y plantillas
state: current
date: 2026-08-26
related: ["[[2026-08-26-sesion-mapeo-osm]]", "[[adr-0002]]", "[[adr-0005]]", "[[adr-0006]]"]
---

# Herramientas de mapeo, análisis del KML y plantillas

Investigación del 2026-08-26 sobre la herramienta para llevar a OpenStreetMap la topología de las estaciones (GTFS-Pathways importada desde Miro, sin coordenadas salvo un punto GTFS por estación). Tres preguntas: (A) ¿es JOSM la mejor herramienta?; (B) ¿se puede construir una plantilla desde una estación terminada y duplicarla con rotación?; (C) ¿los polígonos de andén pueden seguir el rumbo de la línea automáticamente? Lo decidido está en [[adr-0002]], [[adr-0005]] y [[adr-0006]]; el agrupamiento derivado, en [[2026-08-26-agrupamiento-estaciones-familias]]. El CSV de medición de la Parte B es `data/analysis/kml-estaciones-orientacion.csv`.

Limitación de origen: Overpass no fue alcanzable desde el entorno del investigador principal; los conteos de cobertura del Metro en OSM de la adenda los obtuvo un segundo agente vía el espejo `maps.mail.ru` (mismo timestamp de planet, 2026-08-27T01:59Z). `overpass-api.de` bloqueó al agente a media corrida: si la app va a lanzar ~195 consultas, hay que contar con límite de tasa y espejos desde el diseño.

# Parte A — Comparación de herramientas

## A.1 El formato: `.osm` con ids negativos

Un archivo `.osm` es XML con `<osm version generator>` y elementos `node`/`way`/`relation`. **Los ids negativos son el mecanismo previsto para objetos nuevos aún no subidos** («Negative ids are used by editors for new elements»); al subir, el servidor asigna ids positivos. JOSM usa un atributo `action="modify"` en vez de `timestamp`/`version`/`changeset` para objetos nuevos, así que un archivo generado puede omitirlos. Fuente: https://wiki.openstreetmap.org/wiki/OSM_XML

`osmChange` (`.osc`) es un formato de *cambios* (`<create>`/`<modify>`/`<delete>`). Para crear objetos nuevos que un humano moverá antes de subir, el `.osm` plano es lo correcto; el `.osc` entra sólo con MapRoulette (A.5).

## A.2 JOSM Remote Control

Puerto fijo `127.0.0.1:8111`. Fuente: https://josm.openstreetmap.de/wiki/Help/RemoteControlCommands

- **`/load_data?data=…&new_layer=true&layer_name=…&mime_type=…`** — carga XML OSM incrustado en la URL. Único `mime_type` soportado: `application/x-osm+xml`. **«only suited for smaller data (some browsers limit the maximum URL length)»**: no sirve para una estación grande (Tacubaya: 41 stops, 82 pathways).
- **`/import?url=…`** — descarga el archivo desde una URL y lo abre como capa. El `url` **debe ser el último parámetro**. Es el camino correcto: la app Vue expone `…/estacion/tacubaya.osm` y dispara `import`.
- **`/open_file?filename=/tmp/x.osm`** — abre un archivo local.
- **`/load_and_zoom?left=&right=&top=&bottom=&new_layer=&layer_name=&changeset_comment=&changeset_source=&changeset_hashtags=&changeset_tags=`** — descarga los datos existentes de OSM en el bbox y **acepta los tags del changeset**, que exige la política de importaciones.
- **`/version`** — handshake JSON (`protocolversion`, `application`, `version`); sirve para que la app detecte si JOSM está abierto. Fallback `?jsonp=callback`.
- **`/add_node`, `/add_way`** — requieren el permiso «Create new objects», desactivado por defecto.

Flujo resultante («dos disparos», etiqueta del investigador): la app lanza `load_and_zoom` con el bbox y los `changeset_*`, y enseguida `import` con la URL del `.osm`. El voluntario termina con dos capas: lo existente y lo nuestro por colocar.

## A.3 Plugins de JOSM

- **`indoorhelper`** — mantenido (https://github.com/JOSM/indoorhelper; https://wiki.openstreetmap.org/wiki/JOSM/Plugins/indoorhelper). Simple Indoor Tagging; filtrado por nivel («Working level»), presets de cuarto/puerta/elevador/pasillo, validador de `level` faltante. Con 5 niveles por estación, trabajar sin filtro es inviable.
- **`utilsplugin2`** — https://wiki.openstreetmap.org/wiki/JOSM/Plugins/utilsplugin2. **No rota ni espeja**: la documentación no menciona rotación ni plantillas. Sí tiene «Replace geometry (Ctrl+Shift+G)» (sustituye la geometría conservando historial — clave para conflación manual), «Paste tags from previous selection (Shift+R)», «Add nodes at intersections», «Align way nodes».
- **`PicLayer`** — georreferencia una imagen (plano de estación) como fondo. Mantenimiento incierto (tickets #5338, #9086, #24550).
- **`conflation`** — https://github.com/JOSM/conflation. Se autodescribe como «an experimental plugin not ready for widespread use». No ponerlo en el camino crítico.
- **`ShapeTools`** — https://github.com/JOSM/ShapeTools; https://wiki.openstreetmap.org/wiki/JOSM/Plugins/ShapeTools. **Rota la selección un ángulo en grados tecleado**, alrededor del centro de la selección. Es el plugin de rotación numérica.
- **`Level0`** — editor web aparte de texto plano. Irrelevante aquí.

JOSM base: rotar `Shift+Ctrl+arrastrar`, escalar `Ctrl+Alt+arrastrar`; el ángulo se muestra en la barra de estado pero no se teclea (https://josm.openstreetmap.de/wiki/Help/Action/Select).

## A.4 Las alternativas

- **iD** — no sirve como herramienta de colocación. Su API (https://github.com/openstreetmap/iD/blob/develop/API.md) sólo admite `gpx` como datos externos por URL; la capa de datos personalizada es referencia, no editable.
- **Rapid** (https://github.com/facebook/Rapid, Meta) — presenta geometría pregenerada que el mapeador acepta con un clic, pero el dataset debe publicarse en ArcGIS Online y **Esri lo revisa** antes de habilitarlo (https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/mapping/arcgis-data-support-in-osm-editors; https://wiki.openstreetmap.org/wiki/Esri/ArcGIS_Datasets). Segunda opción si el proyecto crece.
- **Vespucci** (Android, https://vespucci.io) — importa GeoJSON y lee/escribe `.osm`, pero bajo tierra no hay GPS. Útil para accesos en superficie.
- **Every Door** (https://every-door.app) — «entrance mode» que añade entradas y las fusiona al contorno del edificio. La mejor herramienta para la campaña de superficie (nombres de acceso, `wheelchair`, `ref`). No sirve para topología interior.
- **StreetComplete** — sólo quests predefinidas.
- **OsmInEdit** (https://wiki.openstreetmap.org/wiki/OsmInEdit) — editor web de interiores, sucesor de iD-indoor; no verificado si acepta datos externos pregenerados.
- **OpenLevelUp** (https://wiki.openstreetmap.org/wiki/OpenLevelUp) — visor por nivel; uso: control de calidad.

## A.5 MapRoulette como gestor de tareas

Resuelve el reparto de ~195 estaciones entre voluntarios. Admite *cooperative challenges* de tipo `tag` y `change`; en `change` cada tarea del GeoJSON lleva `cooperativeWork` con un `.osc` en base64 que se carga en el editor al abrir la tarea. La herramienta oficial es **`mr-cli`** (https://github.com/maproulette/mr-cli): `mr cooperative change` toma **archivos `.osm` guardados desde JOSM o `.osc`** y emite el GeoJSON del desafío. Nuestro generador produce el insumo exacto. Tutorial análogo: https://www.openstreetmap.org/user/mvexel/diary/400460

## A.6 La política: esto es una importación

**Import/Guidelines** (https://wiki.openstreetmap.org/wiki/Import/Guidelines): página wiki (fuente, licencia, software con código fuente, metodología, tags, cuenta), discusión en el foro con etiqueta `import` y 14 días de espera, cuenta `(Usuario)_Import`, compatibilidad ODbL, conflación obligatoria. **Automated Edits code of conduct** (https://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct) incluye los imports «fully automated or using standard editors». Lectura: colocar cada elemento a mano sí es revisión individual, pero no deja de ser un import, y la duplicación por plantilla introduce geometría no observada. Detalle y tarea: [[task-11]].

## A.7 Etiquetado (resumen; el detalle está en [[2026-08-26-alineacion-catalogos-osm]])

Simple Indoor Tagging (https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging) y Metro Mapping (https://wiki.openstreetmap.org/wiki/Metro_Mapping). Correspondencia casi uno a uno: `location_type=1` → `railway=station`+`station=subway`; `0` → `railway=platform`+`public_transport=platform`; `2` → `railway=subway_entrance`; `3` → nodo con `level`; Walkway → `highway=footway`+`indoor=yes`; Stairs → `highway=steps`; Escalator → `highway=steps`+`conveying=*`; Elevator → `highway=elevator`; `is_bidirectional=0` → `oneway`; `level_index` → `level`. Modos 6 y 7 (torniquete, puerta) son nodos `barrier=*`, no ways. **No existe correspondencia documentada GTFS `pathways.txt` → OSM** (confirmado en la adenda): la tabla es una propuesta, no la aplicación de un estándar.

## A.8 Consultas Overpass para no duplicar

Alrededor de un punto de estación, radio 300 m:

```
[out:xml][timeout:60];
(
  node(around:300,{LAT},{LON})["railway"="subway_entrance"];
  way (around:300,{LAT},{LON})["railway"="platform"];
  way (around:300,{LAT},{LON})["public_transport"="platform"];
  node(around:300,{LAT},{LON})["public_transport"="platform"];
  way (around:300,{LAT},{LON})["highway"="steps"];
  node(around:300,{LAT},{LON})["highway"="elevator"];
  way (around:300,{LAT},{LON})["highway"="elevator"];
  way (around:300,{LAT},{LON})["indoor"];
  way (around:300,{LAT},{LON})["level"];
  node(around:300,{LAT},{LON})["level"];
);
(._;>;);
out meta;
```

Para la `stop_area` existente:

```
[out:xml][timeout:60];
node(around:300,{LAT},{LON})["railway"="station"]["station"="subway"];
rel(bn)["public_transport"="stop_area"];
(._;>>;);
out meta;
```

`[out:xml]` es cargable directamente en JOSM; `out meta` es imprescindible (sin `version` JOSM no puede modificar ni subir). Se pasa a JOSM con `/import?url=https://overpass-api.de/api/interpreter?data=…`.

# Parte B — Análisis del KML y viabilidad de plantillas

Medición sobre `data/StatioArea-and-lines.kml` (539 KB) con Python stdlib (`api/.venv` no tiene numpy, shapely, pyproj, fastkml ni lxml); proyección equirectangular local por polígono. CSV: `data/analysis/kml-estaciones-orientacion.csv` — 187 filas, 26 columnas: `folder, name, gtfs_match, gtfs_stop_id, gtfs_stop_name, dist_gtfs_point_m, n_vertices, centroid_lat, centroid_lon, area_m2, mar_length_m, mar_width_m, aspect_ratio, rect_fill, bearing_mar_deg, bearing_pca_area_deg, elongation_pca, line_bearing_shape_proj_deg, dist_centroid_to_track_m, diff_pca_vs_track_deg, bearing_longest_edge_deg, longest_edge_m, bbox_w_m, bbox_h_m, line_bearing_kml_seg_deg, diff_kml_seg_deg`.

## B.1 Estructura del archivo

Un `Document` → carpeta `StatioArea` → 12 subcarpetas (`Line 1`…`Line 12`, `Line A`, `Line B`). **187 polígonos** (todos `Polygon`/`LinearRing` simple) y **12 LineStrings**. Todas las coordenadas con `z=0`: no hay información de altura ni de nivel. Reparto: L1 20, L2 24, L3 21, L4 10, L5 13, L6 11, L7 14, L8 19, L9 12, LA 10, LB 21, L12 12.

Dos correcciones a lo que se creía: (1) **sí hay polígonos de Línea 12** — 12; falta la mitad oriental (las 11 estaciones del ramal a Tláhuac) y sobran **tres estaciones que no existen todavía**: Álvaro Obregón, Valentín Campa y Alfonso XIII (ampliación Mixcoac–Observatorio en construcción). (2) **La Línea B sí tiene su LineString, mal archivada**: la carpeta `Line A` contiene `'Lína A'` (15.05 km, pasa a < 100 m de 10/10 paradas de LA) y `'Línea A'` (29.02 km, pasa a < 100 m de 21/21 paradas de LB). La carpeta `Line B` no tiene LineString.

## B.2 Las LineStrings

| Carpeta | Nombre | pts | Largo | Línea real | Paradas tocadas (<100 m) |
|---|---|---|---|---|---|
| Line 1 | `Línea 1` | 42 | 17.07 km | L1 (med. 6 m) | 20/20 |
| Line 2 | `Línea 2` | 44 | 20.98 km | L2 (med. 5 m) | 24/24 |
| Line 3 | `Línea 3` | 64 | 27.89 km | L3 (med. 5 m) | 21/21 |
| Line 4 | `Línea 4` | 41 | 21.91 km | L4 (med. 2 m) | 10/10 |
| Line 5 | `Lína 5` | 32 | 28.11 km | L5 (med. 15 m) | 13/13 |
| Line 6 | `Línea 6` | 46 | 20.81 km | L6 (med. 3 m) | 11/11 |
| Line 7 | `Línea 7` | 27 | 17.50 km | L7 (med. 5 m) | 14/14 |
| Line 8 | `Línea 8` | 105 | 33.09 km | **L8 + L12** | 14/19 de L8 y 12/20 de L12 |
| Line 9 | `Línea 9` | 20 | 14.35 km | L9 (med. 13 m) | 12/12 |
| Line 12 | `Línea 12` | 45 | 26.29 km | **sólo L12 poniente** | 8/20 (mediana 3081 m) |
| Line A | `Lína A` | 17 | 15.05 km | LA (med. 7 m) | 10/10 |
| Line A | `Línea A` | 43 | 29.02 km | **LB** (med. 8 m) | 21/21 |

Colas fuera del recorrido real (tramo dibujado antes de la primera y después de la última estación):

| Línea | Cola inicial | Cola final | % del trazo |
|---|---|---|---|
| L1 | 0.07 km | 0.13 km | 1.2 % |
| L2 | 0.06 | 0.10 | 0.8 % |
| LA | 0.03 | 0.10 | 0.9 % |
| L7 | 0.37 | 0.16 | 3.0 % |
| L9 | 1.42 | 0.08 | 10.5 % |
| L8(+L12) | 0.10 | 5.40 | 16.7 % |
| L3 | 6.55 | 0.10 | 23.9 % |
| LB | 0.88 | 7.87 | 30.1 % |
| L6 | 0.19 | 9.20 | 45.1 % |
| L5 | 3.03 | 10.63 | 48.7 % |
| L4 | 0.06 | 12.36 | 57.0 % |
| L12 | 4.06 | 14.74 | 71.6 % |

Dato que decide: el espaciado mediano entre vértices de las polilíneas del KML va de **200 a 730 m**, con máximos de hasta 5.6 km (L5). Un andén mide ~150 m; una traza con un vértice cada 500 m no puede dar el rumbo local de una estación.

## B.3 Nombres contra el GTFS

Comparación normalizada contra `data/gtfs/stops_only_metro.txt` (195 paradas): **173 de 187 hacen match exacto** (92.5 %); 1 con `stop_id` raro (Moctezuma L1, `0200L1_MOCTEZUMA` con guion bajo, bug del GTFS); 13 sin match, todos explicables: renombres oficiales (Bulevar Puerto Aereo → «Boulevard Puerto Aéreo»; Ninos Heroes → «Niños Héroes y Poder Judicial CDMX»; Etiopia → «Etiopía y Plaza de la Transparencia»; Viveros → «Viveros y Derechos Humanos»; Ferreria → «Ferrería y Arena Ciudad de México»; La Villa → «La Villa y Basílica»; Azcapotzalco → «UAM Azcapotzalco»; Garibaldi (L8 y LB) → «Garibaldi y Lagunilla»), una errata (`Sam Juan de Letran`), y las tres estaciones inexistentes. 22 paradas del GTFS sin polígono: las 11 de L12 oriente, las 8 renombradas, más Moctezuma.

Distancia del centroide del polígono al punto GTFS: mediana **10 m**, p90 51 m, máximo 213 m (Zócalo L2). Ambas fuentes se validan mutuamente.

## B.4 Geometría de los polígonos

Área: mín 332 m², mediana **4 454 m²**, máx 15 377 m² (Pantitlán LA). Rectángulo mínimo: largo mediano 157 m (79–774), ancho mediano 87 m (8–310). Relación de aspecto mediana 2.07. Vértices por polígono: 8 a 187, mediana ~26.

**Hallazgo geométrico clave**: el `rect_fill` (área del polígono ÷ área de su rectángulo mínimo) va de **0.19 a 0.40**. Los polígonos no son rectángulos: son figuras ramificadas (andén + pasillos + salidas) que llenan el 20–40 % de su caja. Estimar la orientación con el rectángulo mínimo es el estimador equivocado.

## B.5 Orientación del polígono contra el rumbo de la línea

Con MAR y las LineStrings del KML: inservible (sólo 5 estaciones con rumbo). Se cambió la fuente del rumbo a **`shapes.txt` del GTFS** (filtrando `routes.txt` por `route_type=1` → `trips.txt` → `shapes.txt`; 26 shapes con espaciado mediano de 20 a 83 m; proyectar el centroide sobre la traza, tomar los vértices dentro de 150 m y sacar el eje por PCA) y el estimador de orientación al **eje principal del área** (momentos de segundo orden exactos del polígono por shoelace, centrados en el centroide; ángulo = ½·atan2(2·Cxy, Cxx−Cyy)).

| Estimador de orientación | Mediana de la diferencia | ≤10° | ≤20° |
|---|---|---|---|
| Rectángulo mínimo (MAR) | 18.4° | 37 % | 54 % |
| **Eje principal del área (PCA)** | **2.0°** | **76 %** | **83 %** |

Distribución con PCA (n=127): ≤5° 87 (69 %), ≤10° 96, ≤15° 102, ≤20° 105, ≤30° 109, ≤45° 114; mediana 2.0°, p75 9.8°, p90 49.8°. Distribución bimodal: **de las 18 estaciones con diferencia > 30°, 17 son correspondencias** (Pantitlán ×4, Chabacano ×3, Tacubaya ×3, Consulado, Morelos, Jamaica, Tacuba, La Raza, San Lázaro, Salto del Agua, Atlalilco, Deportivo 18 de Marzo; la excepción es Tasqueña, terminal).

| Elongación | n | Mediana | ≤20° |
|---|---|---|---|
| ≥2.5 | 75 | 1.2° | 96 % |
| 1.8–2.5 | 23 | 4.7° | 74 % |
| 1.3–1.8 | 20 | 13.8° | 60 % |
| <1.3 | 9 | 23.2° | 44 % |

Las 60 estaciones sin diferencia calculada no fallaron: los shapes del GTFS de su línea no llegan (L1 truncados por la rehabilitación, L3, L7). Nota: `route_short_name` colisiona entre agencias (una ruta `CMX0700L1` con nombre corto «1» sube hasta lat 19.667); filtrar por `route_id`.

**Conclusión (C)**: automatizable con `shapes.txt` + eje principal del área; disparo automático con **elongación ≥ 2.5** (75 estaciones, 96 % dentro de 20°); correspondencias a mano. → [[adr-0005]].

## B.6 Semejanza de forma entre estaciones de la misma línea

Agrupación por rectángulo mínimo (largo ±20 %, ancho ±25 %); grupos mayores: L2 14 de 24 (158 × 82 m: San Antonio Abad, Colegio Militar, Xola, Viaducto, Portales, Villa de Cortés, Nativitas, Allende, Bellas Artes, Normal, Revolución, Popotla, General Anaya, Cuitláhuac); L1 8 de 20 (146 × 92); L8 8 de 19 (152 × 61); L6 7 de 11 (155 × 52); L7 6 de 14 (126 × 110: Camarones, San Pedro de los Pinos, San Antonio, Mixcoac, San Joaquín, Barranca del Muerto); LB 6 de 21 (180 × 73); L5 5 de 13; L3 5 de 21; L4 4 de 10; L12 4 de 12; LA 4 de 10; L9 3 de 12. Advertencia: agrupa el polígono dibujado, no la arquitectura; hipótesis a validar. El agrupamiento por topología real está en [[2026-08-26-agrupamiento-estaciones-familias]].

## B.7 Lo que había en la base al medir (3 estaciones con pathways)

| Estación | Stops | Andenes | Accesos | Nodos genéricos | Pathways | Modos | Niveles |
|---|---|---|---|---|---|---|---|
| Tacubaya (L1/L7/L9) | 41 | 6 | 11 | 23 | 82 | 44 escaleras, 24 eléctricas, 14 pasillos | ninguno asignado |
| Mixcoac (L7/L12) | 25 | 4 | 8 | 12 | 44 | 20 escaleras, 19 eléctricas, 4 pasillos, 1 elevador | ninguno asignado |
| San Pedro de los Pinos (L7) | 14 | 2 | 2 | 9 | 26 | 8 escaleras, 10 eléctricas, 8 pasillos | 0, −1, −2, −3, −4 |

Los nombres de los nodos genéricos codifican el nivel de forma recuperable («Vestíbulo andén», «Mezzanine −2», «Mezzanine central −2.5» en Tacubaya). **San Pedro de los Pinos es estructuralmente simétrico**: dos ramas idénticas (andén → vestíbulo andén −3 → mezzanine −2 → vestíbulo torniquetes −1 → edificio acceso 0 → acceso), unidas abajo por el pasillo inferior de cambio de andén (−4), cada peldaño con el mismo triple escalera fija bidireccional + eléctrica bidireccional + eléctrica unidireccional. El espejo de la plantilla ya está en los datos.

Sobre los pathways con la misma tupla (origen, destino, modo, bidireccional): el informe los llamó duplicados; el agrupamiento posterior demostró que cada uno tiene `miro_id` distinto y son elementos paralelos reales (cuatro tramos de escalera fija en Portales). **No se deduplican** ([[adr-0006]]). Los 37 pares origen-destino con modos distintos son legítimos.

## B.8 Cómo funcionaría la plantilla

Una plantilla es un JSON con los elementos en **coordenadas locales métricas** relativas al centroide del andén y a su eje (x apunta en el sentido de avance de la línea):

```
{
  "id": "l7-paso-simple-doble-espejo",
  "origen": "L7-SANPEDRODELOSPINOS",
  "eje": "el eje x local apunta en el sentido de avance de la línea",
  "nodos": [
    {"ref":"P-01","tipo":"platform","x":0,   "y":-4.5,"level":-3},
    {"ref":"N-01","tipo":"node",    "x":-62, "y":-4.5,"level":-3}
  ],
  "ways": [{"de":"P-01","a":"N-01","modo":"walkway","bidir":true}],
  "espejo": {"eje":"y", "aplica_a":["P-02","N-05","N-06","N-07","N-08"]}
}
```

Instanciación: `x_local, y_local` → rotar por `θ` (rumbo de la línea en esa estación, de `shapes.txt`) → trasladar al centroide → lat/lon:

```
x' = x·cos θ − y·sin θ
y' = x·sin θ + y·cos θ
lat = lat₀ + y'/m_lat(lat₀)
lon = lon₀ + x'/m_lon(lat₀)
```

con `m_lat(φ) = 111132.92 − 559.82·cos 2φ + 1.175·cos 4φ − 0.0023·cos 6φ` y `m_lon(φ) = 111412.84·cos φ − 93.5·cos 3φ + 0.118·cos 5φ` (serie WGS84 estándar). A escala de estación (radio < 500 m) el error de la aproximación equirectangular es milimétrico; no hace falta pyproj. Validado contra el KML: los centroides recalculados caen a mediana de 10 m del punto GTFS. El espejo es `y → −y` antes de rotar.

Herramientas existentes: **`ogr2osm`** (https://github.com/roelderickx/ogr2osm) lee cualquier fuente OGR incluida PostgreSQL, con translation files en Python y uso como biblioteca; verificar en un archivo de prueba si sus ids son negativos por defecto (la bandera `--positive-id` sugiere que sí). Alternativa: `xml.etree` a mano (~80 líneas). Rotación numérica en JOSM: ShapeTools. Reparto: `mr-cli` + MapRoulette. No existe generador de OSM basado en plantillas con rotación reutilizable.

Firma topológica sugerida para decidir plantillas: `(nº de andenes, nº de accesos, nº de niveles, multiconjunto de modos por salto de nivel, simétrica sí/no)`, calculable desde la base sin coordenadas. Desarrollado en [[2026-08-26-agrupamiento-estaciones-familias]].

# Adenda — cobertura del Metro CDMX en OSM (Overpass, espejo maps.mail.ru, 2026-08-27T01:59Z)

Bbox `(19.15,−99.40,19.72,−98.90)`:

| Elemento | Conteo |
|---|---|
| `railway=subway_entrance` | 447 |
| `railway=station` + `station=subway` | 159 nodos (+34 estaciones como ways) |
| `route=subway` | 24, todas PTv2, `network=STC Metro` |
| `public_transport=stop_area` | 383 |
| `highway=elevator` | 39 en toda el área; 10 a menos de 250 m de una estación |
| `highway=steps` + `conveying` | 7 en toda la red — ninguna dentro de una estación del Metro (son de Pablo, Bandatos) |
| `indoor=*` cerca de estaciones | 195 elementos en 26 estaciones; geometría interior real sólo en Zócalo |

**La capa de red está completa; la capa interior está vacía.** Los accesos sí son riesgo de duplicado: 447 `subway_entrance`, `ref` en 1 de 447; la conflación de accesos será espacial y manual (cruce medido en `data/analysis/osm-accesos-cruce.csv`). 59 de los 159 nodos de estación no tienen ningún acceso a menos de 500 m (toda la Línea A, el oriente de L12, el tramo mexiquense de LB, El Rosario, Tacuba, Morelos, Consulado, Zaragoza, Constitución de 1917).

Correspondencia GTFS-Pathways → OSM: confirmado que no existe (https://wiki.openstreetmap.org/wiki/General_Transit_Feed_Specification/Mapping_to_OSM_tags cubre paradas, rutas y viajes; el único trabajo relacionado va en dirección OSM → GTFS, https://github.com/public-transport/ideas/issues/16). Namespace: México usa `gtfs_*` (6 979 usos de `gtfs_id`); `gtfs:*`, el aprobado, tiene 0 usos en México (https://taginfo.geofabrik.de/north-america:mexico/). Decidido `gtfs:*` en [[adr-0004]].

Hilo del foro mexicano, febrero–marzo de 2025: https://community.openstreetmap.org/t/trazo-de-estaciones-del-metro-en-cdmx-mexico/125839 — se quejan de perímetros de estación sin `level`, citan Zócalo como caso patológico y dejan el mapeo indoor aplazado «a la espera de recursos futuros», remitiendo a Metro Mapping. Canales: foro México https://community.openstreetmap.org/c/communities/mx/65; Telegram https://t.me/osm_mx; Matrix `#OSM-Mexico:matrix.org`; la lista talk-mx está muerta. → [[task-10]].

Sin verificar: mantenimiento real de `ogr2osm` y alternativas (`esy-osm-pbf`, `osmread`); precedentes de generadores por plantilla; **compatibilidad de la licencia del GTFS de la CDMX con ODbL** — requisito de sí o no de Import/Guidelines, resolver antes que cualquier otra cosa técnica ([[task-11]]).

## Observaciones del investigador

Juicio del ejecutor Opus.

- JOSM es la respuesta correcta y la investigación la refuerza: es la única herramienta que acepta datos externos pregenerados en una capa editable. Segunda opción: Rapid, sólo si el proyecto crece.
- La pieza que faltaba no es un plugin sino MapRoulette encima: una tarea por estación con su `.osc`.
- `utilsplugin2` no rota (ShapeTools sí); `conflation` es experimental; `load_data` no sirve para estaciones grandes — el flujo es `/import?url=…` precedido de `/load_and_zoom`.
- Rumbo del andén: `shapes.txt` + eje principal del área; rotación automática con elongación ≥ 2.5; correspondencias a mano.
- Plantillas: sólida, pero diseñarla con 3 estaciones era prematuro; el espejo ya está probado en San Pedro de los Pinos.
- El KML necesita tres arreglos si se quisiera usar (LineString de LB mal archivada, ramal de L12 dentro de L8, erratas) y una decisión sobre los tres polígonos de estaciones en construcción; pero si el rumbo sale del GTFS y los centroides concuerdan a 10 m, el KML deja de ser insumo del generador y pasa a ser referencia visual ([[adr-0005]]).
- La política de OSM es el riesgo más grande del proyecto, y es de calendario: abrir la consulta al foro en paralelo al desarrollo.
