---
type: task
id: task-36
title: Imagen satelital por estación para los turnos de afinación
state: open
date: 2026-10-21
owner: ai
source: ["[[2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin]]"]
related: ["[[task-26]]", "[[task-29]]"]
---

# Imagen satelital por estación para los turnos de afinación

Ricardo quiere que un agente vea la imagen aérea más detallada posible de cada estación, con el KML, lo que ya existe en OSM y nuestros trazos encima, para ajustar los trazos con criterio y no solo con las reglas de la plantilla. El 21 de octubre de 2026 decidió: «hoy solo investigamos y generamos la tarea específica para aplicar y decidir cómo aplicarlo después»; Mapillary queda excluido («eso será demasiado complicado»); «si funciona CDMX, pues esa, si no, pues Esri».

## Resultado de la investigación (21 de octubre de 2026)

- **La CDMX no publica ortofotos.** Se revisaron el Portal de Datos Abiertos (ADIP), el SIEG del IPDP (GeoServer, 160 capas, ninguna raster), el SIGCDMX de SEDUVI/Finanzas (descargas catastrales vectoriales) y el Atlas de Riesgos de la SGIRPC (ArcGIS Enterprise: sus carpetas `img`, `Raster` y `varios` piden token; si hay un vuelo catastral, está ahí y no es dato abierto).
- **INEGI, capa «Ortofotos 1:10 000»** vía WMS 6.1 (`https://gaia.inegi.org.mx/NLB/tunnel/wms/wms61`, EPSG:4326, MaxWidth 2048; la entrada `inegi-wms` del editor-layer-index está caída, la `inegi-wms-v6` de JOSM funciona). Licencia compatible (Términos de Libre Uso del INEGI: copiar, adaptar, extraer, explotar; atribución «Fuente: INEGI»; la wiki de OSM marca «ODbL Compliance verified: yes» para los datos de INEGI). Pero la imagen es de ≈1 m/px y fecha desconocida: se distinguen manzanas y coches, no escaleras ni pabellones. Inútil para esto.
- **Esri World Imagery queda como fuente.** Permiso explícito: «Esri and its imagery contributors grant Users the non-exclusive right to use the World Imagery map to trace features and validate edits in the creation of vector data. Users that create vector data from the World Imagery map can publicly share that vector data … through … the OpenStreetMap (OSM) Initiative» (documento «Esri World Imagery Uses Permitted», ítem de ArcGIS 8e90a00a0a6845a49262e0b756f57a10; la wiki de OSM lo recoge en su página «Esri»). Sobre San Joaquín y San Pedro la imagen es del 2025-01-30, WorldView-2, 0,5 m nativa remuestreada a 0,3 m, exactitud absoluta declarada 8,47 m (hay que alinearla contra OSM o el KML antes de confiar en ella al metro). Endpoint `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`; el máximo real es z19 (≈0,28 m/px): z20 en adelante devuelve un placeholder gris con ETag `vvvvvvvvvvvvf`. La capa Clarity redirige aquí a Wayback 2018.
- **Descartados:** Mapbox Satellite permite calcar para OSM (§1.6 de sus Product Terms) pero prohíbe la descarga automatizada y el almacenamiento (§1.9), así que no sirve para una tubería de agente. Bing requiere llave y se apaga el 30 de junio de 2028. OpenAerialMap tiene vuelos de dron a 5 cm cerca de San Antonio (L7), no sobre estas estaciones.

## Restricción de licencia

El ítem de Esri dice que la capa «is not intended to be used to export tiles for offline». Bajar tiles en vivo, coserlos en `/tmp` para que un agente los mire y ajustar trazos cabe en «trace and validate»; versionar los compuestos en el repo público o redistribuirlos, no. Los compuestos viven fuera del repo como artefacto regenerable. Los changesets llevan `imagery_used=Esri World Imagery`.

## Lo que ya existe como prototipo

Fuera del repo, de la revisión de San Joaquín del 21 de octubre: scripts respaldados en `~/respaldos/san-joaquin-2026-10-21/scripts/` (junto con los de medición contra el trazo de Ricardo, `cmp.py` y `sjslots.py`) (`tiles.py` baja los tiles z19 del bbox con margen y descarta placeholders; `common.py` tiene el marco local; `overlay.py` cose el mosaico con Pillow o `magick` y dibuja encima, georreferenciados, el área del KML, pabellones y explanadas de OSM, edificios, y nuestros trazos por nivel con colores distintos, escaleras con flecha de subida, eléctricas punteadas, torniquetes y una rejilla local cada 10 m con etiquetas u/v). Los compuestos de San Joaquín y de San Pedro (patrón de Ricardo) están respaldados en `~/respaldos/san-joaquin-2026-10-21/`.

## Lo que hay que decidir con Ricardo

1. **Dónde vive el compositor:** como command de Django junto a `export_station_osm` (reusa el marco local, el KML y la caché de contexto) o como script bajo `data/osm/`. Recomendación: command `compose_station_imagery <stop_id>`, que escribe fuera del repo (`~/respaldos/` o una ruta declarada) y nunca versiona rasters.
2. **Cómo lo usa el agente Fable en un turno de afinación:** (a) propone ajustes y Ricardo los aprueba, o (b) los aplica a la plantilla o al .osm y Ricardo revisa el resultado en JOSM. El coordinador recomendó (b), que es lo que Ricardo pidió para los turnos de afinación («rífate… yo checo el resultado»), y esa regla general ya está en el `CLAUDE.md` del proyecto (sección «Trazos en JOSM y turnos de afinación»); queda abierto solo si los ajustes se aplican sobre la plantilla o sobre el .osm.
3. Si vale la pena contrastar con Wayback 2018 (Clarity) cuando el arbolado tape la imagen actual.

## Criterios de aceptación

- [ ] El compositor vive en el repo y produce, para un `stop_id`, un PNG por lado y uno general con imagen Esri z19, KML, OSM y trazos por nivel, sin versionar ningún raster
- [ ] Ricardo decidió si los ajustes del agente se aplican sobre la plantilla o sobre el .osm (que se aplican y él revisa el resultado ya está en el CLAUDE.md del proyecto), y la decisión quedó escrita en el CLAUDE.md del proyecto o en una tarea
- [x] Los scripts del prototipo quedaron rescatados de `/tmp` a `~/respaldos/san-joaquin-2026-10-21/scripts/`
