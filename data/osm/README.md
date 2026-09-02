# Exportación de estaciones a OSM

Esta carpeta contiene archivos `.osm` **generados**, no dibujados a mano. Cada archivo es el punto de partida para editar una estación en JOSM: trae la topología completa que el relevamiento registró (andenes, pasillos, escaleras, escaleras eléctricas, accesos, torniquetes) colocada en coordenadas aproximadas pero georreferenciadas. Lo que se afina a mano en JOSM es la geometría; lo que no hay que tocar a mano es la topología, porque viene de la base y se puede regenerar.

El producto real no son los dos archivos sino el generador: el command `export_station_osm` más una **plantilla por familia arquitectónica**. Las estaciones que comparten grafo comparten plantilla y solo cambian de ancla y rumbo, así que el trabajo de una estación se replica a sus hermanas sin volver a dibujar nada.

## Archivos

- `<slug>.osm` — la estación lista para abrir en JOSM. Todos los ids son negativos y el encabezado lleva `upload='never'`: son objetos nuevos, no tocan nada de lo que ya existe en OSM.
- `templates/<familia>.json` — la geometría local de una familia arquitectónica. Es el archivo que se edita a mano para mejorar el trazo.
- `preview/<slug>-level<N>.svg` — vista en planta por nivel, en metros, para revisar antes de abrir JOSM. Todos los niveles de una estación comparten encuadre y escala, así que se pueden comparar superponiéndolos.

## Regenerar

```
api/.venv/bin/python api/manage.py export_station_osm 0200L2-PORTALES \
    --family tlalpan-surface --bearing 8.2 \
    --anchor 19.3699523,-99.1415639 --preview

api/.venv/bin/python api/manage.py export_station_osm 0200L7-SANPEDROPINOS \
    --family l7-deep-cascade --bearing 6.5 \
    --anchor 19.3914395,-99.1858392 --preview
```

Opciones: `--out RUTA` para escribir en otro lado; `--no-trace` para omitir las etiquetas de trazabilidad; `--mirror` para invertir el eje transversal cuando la estación hermana es la imagen espejo de la plantilla; `--preview` para escribir además los SVG.

El command falla con error si la validación encuentra problemas, y siempre imprime el resumen por etiqueta y la lista de avisos.

## Marco de coordenadas

La plantilla no guarda latitudes y longitudes sino un marco local métrico anclado a la estación: **u** son metros sobre el eje del andén, positivos hacia el rumbo; **v** son metros a la derecha de ese eje. Con los rumbos de estas dos estaciones (8.2° y 6.5°, casi norte), `v > 0` es el oriente. El command proyecta (u, v) a WGS84 con los metros por grado a la latitud del ancla, sin dependencias externas.

El ancla es el centroide del polígono KML de la estación, tomado de `data/analysis/kml-estaciones-orientacion.csv` (columnas `centroid_lat`, `centroid_lon`).

## Esquema de la plantilla

Un JSON con cuatro secciones. Las claves de nodo son el sufijo del `stop_id` (`L2-PORTALES-N-05` → `N-05`): es lo único estable entre estaciones hermanas, porque los `miro_id` cambian de una estación a otra.

- `nodes` — dónde va cada stop del grafo. Todo nodo lleva `u` y `v`. Los andenes llevan además `length` y `width` (el rectángulo, con el largo sobre u), `spine_v` (desplazamiento transversal de la línea de circulación interior respecto del centro del andén) y `spine_margin` (cuánto se recorta esa línea respecto de las puntas del andén). `underground` es opcional; por omisión se deduce del nivel negativo. `tags` añade etiquetas sueltas al andén.
- `edges` — cómo se dibuja cada pathway. Se empareja con la base por `from`, `to`, `mode` e `index`; el `index` distingue los pathways paralelos —las cuatro escaleras del andén de Portales, los tres pasillos de cada andén de San Pedro— y se asigna ordenando los paralelos por `miro_id`. `geometry` es una lista de puntos, donde cada punto es una clave de nodo (`"N-05"`) o un par `[u, v]`, **escrita siempre en el sentido `from` → `to` de la propia arista**: de ahí salen el orden de los nodos del way y, con él, el `incline`. El generador la invierte solo en los pathways bidireccionales, que dibuja siempre de abajo hacia arriba. Una geometría escrita al revés no es un detalle estético —deja el archivo diciendo que se sube por donde se baja—, así que la validación la caza comparando el `incline` con los niveles de los dos extremos. En un pathway bidireccional el par `from`/`to` puede estar declarado en cualquiera de los dos órdenes: la base guarda el sentido en que se trazó el conector en Miró, que cambia de una estación hermana a otra, y el emparejamiento busca el par también invertido. `bow` desplaza el punto medio en perpendicular: es lo que separa en pantalla dos pathways que comparten sus dos extremos, como la escalera y la escalera eléctrica de un mismo tramo. `name` fuerza el nombre del way; si no está, los pasillos heredan el nombre del nodo que empieza con «Pasillo». `tags` añade etiquetas sueltas y se aplica después de las que calcula el generador, así que también sirve para sobreescribirlas: es la vía para todo lo que es propio de una familia y no del modo de pathway. Así llevan `{"bridge": "yes", "layer": "1"}` los dos tramos vestibulares de Portales, que cruzan la Calzada de Tlalpan por encima; ninguna regla del generador lo sabría, pero las estaciones hermanas heredan el puente junto con la plantilla, que es exactamente lo que se quiere. `turnstile` inserta un nodo de torniquete sobre el way: `{"from": "N-01", "distance": 6}` lo pone a seis metros de N-01 hacia el otro extremo.
- `extra_ways` — geometría que la plantilla añade y el grafo no modela. Los grafos del relevamiento son topológicos: un vestíbulo es un nodo, no una superficie. Si un archivo necesita un tramo de unión que no corresponde a ningún pathway, se declara aquí con `geometry`, `level` (o `levels`) y opcionalmente `name` y `tags`. Ambas plantillas actuales lo dejan vacío.
- `description` y `axes` — texto libre para quien edita la plantilla: qué familia es, qué estaciones hermanas la usan y hacia dónde apuntan los ejes u y v.
- `comment` — campo libre admitido dentro de cualquier nodo o arista, para explicar qué es esa pieza y, en un grupo de paralelos, cuál de ellos es. El cargador ignora las claves que no conoce, así que anotar de más no rompe nada.

Si la base tiene un pathway que la plantilla no dibuja, el command falla y dice cuál. Si la plantilla define una arista que la base no tiene, avisa y sigue.

## Cómo se arma el archivo

1. Cada andén produce dos ways: el polígono cerrado (`railway=platform`) y una línea de circulación interior (`highway=footway`) que corre a lo largo. Toda escalera del andén arranca o termina en un nodo de esa línea.
2. Cada pathway produce un way con la geometría de la plantilla.
3. Los nodos que caen a menos de 25 cm uno de otro son el mismo nodo, así que dos ways que llegan al mismo punto quedan unidos. Este pegado **no mira el nivel**, a diferencia de la soldadura del paso siguiente: dos piezas de niveles distintos que coincidan en planta comparten nodo. A veces es lo correcto —las puntas de una escalera pertenecen a los dos niveles que une— y a veces no; la validación lo reporta como aviso cuando los ways que se juntan en un nodo no tienen ningún nivel en común.
4. Después se **suelda**: el extremo de cada way se inserta como vértice de cualquier otro way que pase por ahí. Sin esto la conectividad sería solo visual, dos líneas que se tocan en pantalla y no comparten nodo no son un grafo. La soldadura solo une ways que comparten algún nivel, para no coser un pasillo del +1 con el andén del 0 que pasa por debajo.
5. Se validan ids únicos y negativos, referencias `nd` resueltas, `level` en todo way, distancia mínima entre nodos, coherencia de `incline` y `conveying` con el orden de niveles, y conectividad: desde cada acceso se llega, por BFS, a la línea de circulación de todos los andenes.

## Convenciones de etiquetado

Vienen del ADR 0004 y de las decisiones tomadas al generar estos dos archivos. Viven todas en `api/utils/osm/tags.py`, en un solo lugar, para que una tarea posterior las mueva a configuración.

- **Andén**: way cerrado con `railway=platform` + `public_transport=platform` + `area=yes` + `subway=yes` + `level` + `name` (el de la estación). `level:ref` solo si el `Level` tiene nombre, y solo en el andén: los accesos y pasillos del mismo nivel no lo llevan. Los andenes laterales llevan `destination` con la terminal, sacada del `stop_name` («L7 => Rosario» → `El Rosario`); el andén central no lleva ninguna. Los andenes subterráneos añaden `layer` igual al nivel y `location=underground`. Sin `tunnel`: es una clave de vía lineal y el andén es un área, así que `location` ya dice lo que hay que decir.
- **Pasillos y vestíbulos**: líneas con `highway=footway` + `indoor=yes` + `level`. Nunca `highway=corridor`, nunca polígonos de sala.
- **Escaleras**: `highway=steps` + `indoor=yes` + `level=<inferior>;<superior>` + `incline`. Se omite `step_count` a propósito: el relevamiento no lo tiene.
- **Escaleras eléctricas**: lo mismo más `conveying`. Las bidireccionales (`is_bidirectional=1`) se dibujan de abajo hacia arriba con `conveying=reversible` e `incline=up`. Las de un solo sentido (`is_bidirectional=0`) se dibujan de `from_stop` a `to_stop` —esa es la flecha que el equipo trazó en Miró, no un accidente— con `conveying=forward` y el `incline` que corresponda a ese sentido. En estas dos estaciones todas las de un solo sentido suben.
- **Sentido único**: todo pathway con `is_bidirectional=0` lleva `oneway:foot=yes`, sea escalera, escalera eléctrica o pasillo, y la clave es siempre `oneway:foot` y nunca `oneway` (ADR 0004). En las eléctricas convive con `conveying=forward` sin redundancia: `conveying` describe el movimiento de la máquina y `oneway:foot` la restricción de paso, y ningún ruteador peatonal lee la primera, así que sin la segunda la restricción no quedaría en el archivo.
- **Accesos**: nodo con `railway=subway_entrance` + `entrance` (el valor del campo `Stop.entrance`) + `name` + `level=0`. Sin `ref`: no conocemos las letras.
- **Torniquetes**: nodo insertado sobre un pasillo, con `barrier=turnstile` + `amenity=ticket_validator` + `level`.
- **Nodos genéricos**: no se etiquetan. Son cruces de la red peatonal; su nombre, cuando describe un pasillo, pasa al `name` del way.
- **Trazabilidad**: `note:stop_id`, `note:pathway_id` y `note:miro_id` permiten volver del objeto dibujado al registro de la base. **No son etiquetas OSM y no se suben nunca**: hay que regenerar con `--no-trace` antes de cualquier carga.

## Supuestos — para revisión

Todo lo de esta sección es una decisión tomada sin evidencia de campo. Se puede corregir editando la plantilla y regenerando; nada de esto está en el código.

**Anclas y rumbos.** Portales usa el rumbo `line_bearing_shape_proj_deg` del CSV de orientaciones, 8.2°, que coincide con el trazo `railway=subway` de la Línea 2 en OSM (8.0°–8.3° en los segmentos junto a la estación). San Pedro de los Pinos no tiene rumbo de vía en el CSV, así que se usó el de la Avenida Revolución bajo la que corre la Línea 7: 6.5°, calculado por componentes principales sobre los vértices de las cuatro ways `Avenida Revolución` de OSM que caen a menos de 150 m del centroide (ways 1446414820 a 1446414823). El respaldo previsto, `bearing_pca_area_deg` = 9.4°, no hizo falta.

**El índice de los paralelos no es una posición.** El `index` que distingue los pathways paralelos se asigna ordenando el grupo por `miro_id`, y los `miro_id` son de cada tablero: no hay ninguna garantía de que la escalera que en Portales quedó en el índice 0 sea la que ocupa ese mismo lugar físico en Xola o en Nativitas. Es decir, al replicar una plantilla las cuatro escaleras de Portales o los tres pasillos de cada andén de San Pedro pueden caer permutadas entre sí, con la geometría correcta pero repartida mal. Como todas son paralelas entre los mismos dos extremos, el archivo se ve bien igual y el error solo aparece al comparar con la realidad. Por eso, en cada estación hermana hay que verificar el emparejamiento índice ↔ posición con las etiquetas `note:miro_id` del archivo generado, contra el tablero de Miró, antes de dar la estación por buena.

**Posición de los accesos.** Los tres accesos que ya existen en OSM se copiaron con una diferencia menor a 10 cm: en Portales, el nodo 5197203900 es el acceso poniente y el 5197203901 el oriente; en San Pedro, el nodo 3761143341 es el acceso poniente. El **acceso oriente de San Pedro no existe en OSM** y se colocó como espejo del poniente; es el punto que más conviene verificar contra imagen satelital.

**Sentido de las escaleras eléctricas de un solo sentido.** Se dibujan de `from_stop` a `to_stop` porque se asume que la flecha que el equipo trazó en Miró es el sentido real de la máquina y no un accidente del dibujo. De ahí salen el orden de los nodos, el `incline` y el `conveying=forward`: si la flecha estuviera invertida, las tres etiquetas quedarían invertidas juntas. En estas dos estaciones todas las de un solo sentido suben, que es lo esperable, pero no está verificado en campo.

**Lados de los andenes en San Pedro.** El grafo dice que el acceso poniente lleva, por su cascada, al andén `P-02` («L7 <= Barranca del Muerto»), y el oriente al `P-01` («L7 => Rosario»). Eso coincide con la circulación por la derecha del Metro de la Ciudad de México: un tren hacia El Rosario viaja hacia el norte y va por la vía oriente, así que su andén es el oriente. Grafo y regla coinciden, pero ninguno de los dos es una observación de campo.

**Ancho de la Calzada de Tlalpan.** Los ejes de los cuerpos centrales de la calzada están a unos ±11 m del centroide y las laterales a ±15 m, medido sobre OSM. Los accesos, ya medidos, quedan a ±28 m. El andén se dibujó de 150 m × 10 m centrado en el camellón.

**Geometría de San Pedro.** Andenes laterales de 150 m × 5 m separados por 8 m de vías, y una cascada por lado con tramos de unos 8 m de proyección horizontal por nivel. Ninguna de esas medidas está relevada.

**El vestíbulo-puente de Portales.** El grafo modela el vestíbulo como un solo nodo (`N-01`), así que las cuatro escaleras del andén llegan todas a él: en el archivo se ven como un abanico desde la línea del andén hasta el eje del puente, dos por cada lado del cruce. La forma real de la losa hay que dibujarla a mano.

**Torniquetes.** Se pusieron los dos de Portales, sobre los pasillos vestibulares, a seis metros del vestíbulo. En **San Pedro no se puso ninguno**: sus vestíbulos de torniquetes (`N-03` y `N-07`, nivel -1) son nodos donde solo confluyen escaleras, y un torniquete no puede ir sobre un `highway=steps`. Hace falta decidir si se dibuja un tramo corto de pasillo en el nivel -1 que lo sostenga.

**Nombres que se pierden.** `N-04` de San Pedro se llama «Pasillo inferior - cambio de andén», pero llega a él por escaleras, no por pasillos, así que ese nombre no quedó en ningún way. La regla actual solo pasa el nombre a pasillos.

**El andén de Portales encima de las vías.** OSM traza las dos ways `railway=subway` de la Línea 2 a v = −3.1 y v = +3.4 en el marco local, o sea a 6.5 m una de otra, y el andén se dibujó de 10 m de ancho centrado en el camellón: las dos líneas de vía caen **dentro** del polígono del andén, y su esquina norte se mete unos 0.6 m en el cuerpo central de la calzada. Lo más probable es que OSM tenga ahí el trazo corrido de la línea, sin la separación que las vías toman al llegar a una estación de camellón, y no que el andén esté mal; pero es lo que se va a ver al abrir el archivo con la capa de OSM cargada, y se resuelve angostando el andén en la plantilla o corrigiendo las vías a mano.

**Los accesos de San Pedro contra la calle que los nombra.** Los dos accesos quedaron en u ≈ +5.6, siguiendo al nodo OSM 3761143341 del acceso poniente. La Wikipedia en español ubica las dos salidas en «Avenida Revolución y Calle 9» (oriente) y «Avenida Revolución y Calle 4» (poniente), y esas dos calles son el mismo cruce a ambos lados de la avenida: cortan el eje de la estación en **u ≈ −31**. Son 37 m de discrepancia entre OSM y la Wikipedia, no algo que la plantilla haya inventado, pero conviene resolverla contra imagen satelital antes de replicar a San Joaquín, porque de E-01 cuelga toda la cascada poniente.

**El nodo de estación de San Pedro en OSM.** El `railway=station` 681454741 está a v = +31.5, unos 31 m al oriente del eje de la Avenida Revolución, y además lleva `service=yard`, que no corresponde a una estación. La way `railway=subway` de la Línea 7 (320892187) no tiene ningún otro vértice cerca, así que hereda el mismo corrimiento. El ancla usada aquí se apoya en el eje de la avenida, no en ese nodo. Esa misma way declara `level=-4` y `layer=-4` para toda la línea, mientras que aquí los andenes son −3 y solo el pasillo bajo las vías es −4.

**Puente sobre la calzada.** Los dos tramos vestibulares del nivel +1 de Portales cruzan la Calzada de Tlalpan y ya llevan `bridge=yes` y `layer=1`, puestos desde el bloque `tags` de sus aristas en la plantilla. Lo que sigue sin dibujar es la forma de la losa: el puente es hoy dos líneas rectas que se encuentran en el vestíbulo.

**`step_count` y `ref` de accesos.** Se omiten porque no se conocen, no porque no correspondan.
