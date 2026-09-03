---
type: decision
id: adr-0011
title: "Integración del .osm generado con los objetos existentes de OSM: contexto embebido con ids reales, accesos adoptados, senda soldada al andén, áreas de estación del KML y edificios de acceso con explanada"
state: accepted
date: 2026-09-02
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
affects: ["api/utils/osm/", "api/stop/management/commands/export_station_osm.py", "api/stop/management/commands/link_osm_ids.py", "data/osm/context/", "data/osm/templates/", "data/osm/osm-links.csv"]
related: ["[[adr-0010]]", "[[adr-0005]]", "[[adr-0004]]", "[[task-11]]", "[[task-26]]", "[[task-17]]"]
---

# Integración del .osm generado con los objetos existentes de OSM: contexto embebido con ids reales, accesos adoptados, senda soldada al andén, áreas de estación del KML y edificios de acceso con explanada

## Contexto y planteamiento del problema

[[adr-0010]] fijó un archivo de solo objetos nuevos con ids negativos, sin objetos existentes, y la regla de no tocar nada de OSM hasta resolver [[task-11]]. Al revisar los dos primeros archivos en JOSM ([[2026-09-02-sesion-integracion-osm-y-niveles]]) resultó que tres de los cuatro accesos emitidos eran duplicados a 2–7 cm de los nodos `railway=subway_entrance` que ya existen, que esos nodos están aislados de toda banqueta, y que el archivo no tenía forma de decir cuál nodo es el gemelo de cuál acceso: la correspondencia vivía solo en el comentario de la plantilla. Ricardo pidió que lo generado se integre con lo existente en vez de ser una isla, que el área de la estación entre al archivo, y que la línea de circulación del andén lo recorra completo y comparta nodo con su polígono. [[adr-0005]] calificaba el polígono del KML de referencia visual; Ricardo lo corrigió: es información que hay que subir a OSM cuando no exista.

## Criterios de decisión

- Que nada de lo nuestro quede desconectado del grafo peatonal real: accesos, banquetas, andén.
- Que el archivo siga siendo reproducible solo con el repo, sin red.
- Que lo ajeno no se altere por accidente: solo se modifica lo que Ricardo decidió modificar.
- Que las etiquetas resistan la revisión del wiki de OSM y del foro de importación.

## Opciones consideradas

- **A. Todo el contexto a 50 m dentro del archivo** — 50 a 200 elementos por estación, foto que envejece, contradice adr-0010 de lleno.
- **B. Solo Remote Control** — JOSM baja el área y luego importa el archivo (lo previsto en [[adr-0002]]); permite ver el contexto pero no conectar.
- **C. Intermedia** — el archivo embebe solo aquello a lo que lo nuestro debe pegarse: los nodos de acceso enlazados en la base, las banquetas cercanas y el contorno de estación donde exista; el resto lo baja JOSM.

## Resultado

Se eligió **C**, con estas convenciones:

- **Objetos ajenos**: se escriben con su id positivo real, `version`, `timestamp`, `changeset`, `user` y `uid`, y todas sus etiquetas; nunca se les hace snap, soldadura ni se mueven salvo decisión explícita, en cuyo caso llevan `action='modify'`. El validador los exime de las reglas de id negativo, nivel obligatorio e islas.
- **Qué contexto entra** (enmendado el 2 de septiembre de 2026, ver las notas de enmienda al final): además de los nodos de acceso enlazados, las vías peatonales cercanas y el contorno de estación, entran congelados —id y versión reales, sin tocar, sin conectar, nunca destino de tramos— las calles (`highway` de `motorway` a `service`, con sus `_link`), las vías urbanas (`railway=subway|light_rail|tram`) y el transporte público (`public_transport=*`, `highway=bus_stop`, `railway=tram_stop`, `amenity=bus_station`) que caen a 50 m de cualquier nodo nuestro. La consulta a Overpass sigue siendo a 150 m. Solo las vías peatonales reciben tramos de conexión desde los accesos.
- **Fuente y caché**: consulta a Overpass por estación (`api/utils/osm/overpass.py`), guardada como JSON versionado en `data/osm/context/<estación>.json`; sin red y sin caché el exportador falla con mensaje; `--no-context` exporta sin contexto.
- **Accesos**: un stop con `osm_id` (enlace de [[task-17]], cargado desde `data/osm/osm-links.csv` por `link_osm_ids`) reutiliza el nodo de OSM y le agrega nuestras etiquetas; las existentes se conservan y un conflicto de valores se reporta. Esto enmienda la viñeta «sin objetos existentes» y la regla de no tocar objetos existentes de [[adr-0010]], por decisión de Ricardo y antes de resolver [[task-11]]. Un acceso sin enlace sigue siendo nodo nuevo.
- **Tramos a banquetas**: de cada acceso sale un `highway=footway` con `level=0` recto al vértice existente más cercano de cada way peatonal distinta a menos de 40 m, terminando en ese vértice para no modificar la way ajena; un solo tramo por vértice destino. En esquinas salen dos o más y Ricardo poda en JOSM.
- **Senda del andén**: de punta a punta (`spine_margin` 0) y con sus dos extremos insertados como vértices de los lados cortos del polígono, que pasa de 4 a 6 nodos. Etiquetas `highway=footway` + `indoor=yes` + `level`; `highway=corridor` sigue descartado porque OSRM y GraphHopper lo ignoran.
- **Área de estación**: se lee del KML (`api/utils/osm/kml.py`). En estaciones subterráneas se emite como área con `public_transport=station`, `station=subway`, `subway=yes`, `location=underground` y `name`, dejando intacto el nodo de estación existente. Donde OSM ya tiene contorno de estación se embebe ese contorno; en Portales, por esta vez, van ambos para que Ricardo elija. Opción `station_area` por plantilla y `--station-area` en el command.
- **Edificios de acceso** (familia L7): cuadrado `building=yes` de 12 m centrado en la coordenada del acceso, tres puertas `railway=subway_entrance` + `entrance=yes` + `level=0` sobre un lado (`door_side` en la plantilla; por defecto el lado que mira a la banqueta más cercana), el nodo de OSM adoptado como puerta central, las escaleras del grafo arrancando del punto medio del lado sin puertas, y una explanada `highway=pedestrian` + `area=yes` centrada en el edificio con medio lado igual a la distancia perpendicular a la banqueta más cercana, compartiendo nodo con los tramos que la cruzan. Puertas clausuradas: `disused:railway=subway_entrance` vía `closed_doors`.
- **Etiquetas**: el nombre del acceso va en `description`, no en `name` (el wiki prohíbe nombre de estación y descripciones en `name`; la letra señalizada irá en `ref`, [[task-18]]); `level:ref` se retira; `wheelchair=no` en toda `highway=steps`, fija o eléctrica; `destination` en andenes laterales se conserva; `wheelchair` desde `wheelchair_boarding` no se emite hasta que sea dato medido; `tunnel=yes` no aplica a pasillos interiores, que van con mapeo indoor y `level`; un `level_index` no entero detiene la exportación nombrando el stop, en vez de redondear.
- **Lector de la edición**: `diff_station_osm <generado> <editado>` compara el archivo editado por Ricardo con el generado y reporta movimientos, altas, bajas y cambios de etiquetas en metros locales de la plantilla, para dialogar antes de llevar el ajuste a la plantilla.

### Consecuencias

- **Bueno:** los accesos dejan de duplicarse y quedan conectados a la banqueta; el andén y su senda son un solo grafo; el archivo se funde por id sobre la descarga real; el polígono del KML deja de ser solo un centroide.
- **Malo:** el archivo modifica objetos ajenos antes de que [[task-11]] cierre la política de importación, así que un voluntario podría subir cambios sin el proceso; el caché de Overpass envejece y hay que refrescarlo; el lado de las puertas depende de que OSM tenga banqueta cerca, y en el poniente de San Pedro no la tiene.

### Cómo se comprueba

`export_station_osm` con contexto valida sin errores en las dos estaciones; los .osm traen ways con id positivo y `version`, nodos de acceso con `action='modify'`, andenes de 6 vértices y, en San Pedro, dos edificios con tres puertas y dos explanadas. `git ls-files data/osm/context/` muestra el caché versionado.

## Más información

[[2026-09-02-sesion-integracion-osm-y-niveles]], [[task-26]], [[task-27]], [[task-28]].

## Notas de enmienda

- 2 de septiembre de 2026 (noche, [[2026-09-02-sesion-integracion-osm-y-niveles]]): el criterio del camino C —«solo aquello a lo que lo nuestro debe pegarse»— se amplía por decisión de Ricardo. El contexto embebido ya no se limita a lo conectable: entran también, como objetos ajenos congelados, calles, vías urbanas y transporte público a 50 m de cualquier nodo nuestro, con la lista de etiquetas de la viñeta «Qué contexto entra» del Resultado. El motivo es de lectura, no de topología: el mapeador debe ver la estación dentro de su manzana al abrir el archivo en JOSM, no flotando. Lo demás del camino C sigue igual —lo ajeno no se toca ni se conecta, y solo las vías peatonales reciben tramos desde los accesos—. Resultado en las dos estaciones: Portales embebe 12 calles (Calzada de Tlalpan, Calzada Santa Cruz, Avenida Víctor Hugo, Calle Albert, Calle Hamburgo) y las vías de la Línea 2; San Pedro de los Pinos, 12 calles (Avenida Revolución, Avenida 1, Avenida 1º de Mayo, Calles 2, 4, 7, 9 y 13), la vía de la Línea 7 y la plataforma del Trolebús Elevado.
