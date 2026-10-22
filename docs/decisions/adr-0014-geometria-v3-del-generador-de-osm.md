---
type: decision
id: adr-0014
title: "Geometría v3 del generador de .osm: andenes inscritos en la franja del KML, bancos de escaleras paralelas, pabellones de OSM adoptados, solo el área del KML y contexto a 120 m"
state: accepted
date: 2026-10-21
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[task-26]]", "[[2026-09-30-imagenes-sotm-evolucion-portales]]", "[[2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin]]"]
affects: ["api/utils/osm/builder.py", "api/utils/osm/geometry.py", "api/utils/osm/overpass.py", "api/utils/osm/template.py", "api/utils/osm/document.py", "api/utils/osm/fit.py", "api/utils/osm/validate.py", "api/stop/management/commands/export_station_osm.py", "data/osm/templates/", "data/osm/README.md"]
related: ["[[adr-0011]]", "[[adr-0013]]", "[[adr-0006]]", "[[adr-0005]]", "[[task-35]]", "[[task-11]]"]
---

# Geometría v3 del generador de .osm: andenes inscritos en la franja del KML, bancos de escaleras paralelas, pabellones de OSM adoptados, solo el área del KML y contexto a 120 m

## Contexto y planteamiento del problema

El commit `788d624` del 2 de septiembre de 2026 (20:57; bitácora local `28f31194-3d8d-4cc4-a3fa-8745045c72fe`, sesión `session_01Hpdsm3RR7obQnGYi72cSa2`) rehízo la geometría del generador de .osm —la «v3»— y se cerró con «cierre documental pendiente». Lo que esa versión decidió vive solo en `data/osm/README.md` y en las plantillas; ningún ADR lo gobierna, y tres viñetas de [[adr-0011]] (contexto a 50 m, dos áreas en Portales, edificios de acceso de 12 m) quedaron superadas por el código. Este ADR registra el estado de la v3 tal como corre hoy, el 21 de octubre de 2026, y quién decidió cada pieza.

La v3 respondió a un encargo largo de Ricardo, escrito al revisar los archivos de la v2 en JOSM antes de salir a la reunión de Bandatos. Sus frases que fijan reglas, textuales:

> Hoy traemos cosas de OSM en un radio de 50 metros creo, pero deberíamos ampliar ese rango a 120 metros.

> Hoy no traemos edificios, pero me doy cuenta que en San Pedro de Los Pinos los dos edificios ya estaban mapeados. También los edificios alrededor nos pueden ayudar a delimitar elementos como "límites de explanada" o las rutas hacia banquetas

> Al comparar las áreas mapeadas con las áreas que yo tenía desde el .kml, definitivamente están mejor hechas las del .kml, lo que yo propondría sería reemplazar el existente (cuando exista, obvio) como parte de las ediciones.

> El área de la estación debería delimitar la ubicación y los límites de los polígonos de las plataformas, cuyos nodos (todos y cada uno de ellos) deben de compartir los nodos del área [...] Todas las vías y realmente todo lo de la estación debe quedar siempre dentro de los límites del área de la estación.

> los conjuntos de 2, 3 o 4 escaleras que no salgan desde la plataforma del andén deben estar paralelas, con una separación de ~4 metros entre ellas y al final, las 3 deben tener una pequeña way que la una con un nodo 4 metros adelante (debe estar en un punto central), esto para cada uno de los extremos

> Son 3 salidas, cada una en uno de los lados del cuadro o rectángulo del edificio de entrada, excepto el lado por donde salen las escaleras, las 3 salidas conectadas por una vía peatonal al centro del edificio

Y en las preguntas de la misma sesión: barreras y muros además de banquetas; «Mismo largo: 4 esquinas en el borde» entre andén y área; «Estímalos tú del kml y de OSM» para los anchos; «Cada vía mide 3 metros, 6.5 donde están juntos, igual manda el kml»; «No: andén de 150 m centrado, extremos dentro del área» para Portales; y del pabellón poniente de San Pedro, «Hacia el norte, es la que está clausurada, pero a los lados sí tiene 2 abiertas».

## Criterios de decisión

- El polígono del KML es la mejor forma disponible de la estación, y todo lo de la estación cae dentro de él.
- Las plantillas declaran relaciones con la franja del KML («de qué borde cuelgo»), no coordenadas, para que la misma plantilla sirva a las hermanas (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final).
- Lo que OSM ya tiene bien mapeado se adopta, no se duplica.
- El archivo debe leerse en JOSM dentro de su manzana.

## Opciones consideradas

No se evaluaron alternativas formales fuera de las preguntas citadas arriba: la mayoría de las piezas son instrucciones de Ricardo y el resto, decisiones de implementación del coordinador de esa sesión en piloto automático.

## Resultado

Quién decidió cada pieza va al final de su viñeta: **Ricardo** (instrucción o respuesta suya, citada arriba) o **sesión** (lo eligió el modelo al implementar; README lo lista como supuesto pendiente de su visto bueno).

### Área de estación y andenes

- **Solo el área del KML** (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final) (`station_area: "kml"` en las dos plantillas). Donde OSM ya tiene contorno de estación, ese contorno conserva id, versión y etiquetas, toma la geometría del KML (`action='modify'`) y sus vértices que nadie más usa salen con `action='delete'`; donde no hay, se dibuja un way nuevo. Ya no van dos áreas en Portales. — Ricardo.
- **D1, andenes inscritos en la franja del KML**: de la franja larga del polígono salen ancho y posición transversal del andén; la plantilla declara `band_side` (`+v`, `-v` o `axis`), `band_inset` y el ancho como `width` en metros, `track_gap` (hueco de vías, del que sale `width = (franja − track_gap) / 2`) o `width: "band"` (la franja entera). Los seis vértices del andén se meten como vértices del anillo del área. San Pedro: franja de 15.07 m, `track_gap` 6.5 m, andenes de 4.29 m. Portales: `width: "band"`, 12.98 m. — Ricardo en la regla (andén dentro del área y con nodos compartidos; 6.5 m de vías) y sesión en la lectura de la franja (que sea exactamente andenes más vías, y que en Portales no incluya vía).
- **Largo**: `length_fit: "ring"` por omisión (los cruces del anillo fijan el largo); `"centred"` en Portales, 150 m centrados en la franja de 171 m, con las puntas dentro del área. — Ricardo.
- **D2, senda desplazada**: `spine_v` corre la línea de circulación 1.5 m hacia la vía en los andenes laterales de San Pedro; en Portales va en el eje. — Sesión; convención de dibujo, no observación.

### Bancos de escaleras paralelas

- Bloque `banks` de la plantilla (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final): un banco tiene `from` y `to` (los dos nodos de encuentro), `spacing` (4 m por omisión) y `lead` (4 m por omisión); cada escalera del banco se desplaza `spacing · (slot − (n−1)/2)` en perpendicular, con `slot` 0 a la izquierda mirando de `from` a `to` y por omisión igual al `index` de la arista. Cada punta se une a su nodo de encuentro con un tramo corto `highway=footway` + `indoor=yes` + `level` de esa punta. Con `axis` mandan las escaleras y los nodos del grafo se recolocan `lead` más allá de cada punta; `place` dice cuál se muda, para que dos bancos encadenados no se pisen el nodo. Un banco entre nodos demasiado cercanos recorta el `lead` y avisa (`MIN_BANK_STAIR_M` = 2 m). Implementado en `StationBuilder._plan_banks`, `_bank_segment` y `_build_bank_joins`. — Ricardo en la regla (paralelas, ~4 m, nodo central 4 m adelante en cada extremo); sesión en el mecanismo (`axis`, `place`, `slot`).
- Las escaleras que nacen del andén quedan fuera de la regla: las cuatro de Portales van en abanico con geometría propia. — Ricardo («que no salgan desde la plataforma del andén»).
- **D3, espaciado y orientación en San Pedro** (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final): 4 m entre ejes y 4 m de aproche en todos los bancos; en el rectángulo de salida las escaleras −2→−1 corren a lo largo de v, perpendiculares a las vías, porque es lo único que hacía caber los tres niveles en el rectángulo del KML. — Ricardo en los 4 m; sesión en la orientación −2→−1.
- `bow`, que viene de la v1, sigue disponible para separar en pantalla dos pathways que comparten sus dos extremos fuera de un banco; un banco lo sustituye, y hoy ninguna de las dos plantillas lo usa.
- **`extra_ways`** sostiene lo que el grafo no modela: la losa del puente de Portales, el vestíbulo transversal −3 de San Pedro y el tramo −1 que lleva los torniquetes de San Pedro.

### Edificios de acceso

- Un `building=*` de OSM (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final) que contiene el acceso o pasa a menos de 10 m (`BUILDING_ADOPT_M`) se adopta: conserva id, versión y etiquetas y solo recibe los nodos de puerta; si podado de vértices casi colineales no queda un cuadrilátero, se avisa y se dibuja el cuadrado. San Pedro adopta los pabellones 476125317 y 476125318. — Ricardo.
- Sin edificio en OSM, cuadrado de `side` metros (12 por omisión), centrado en el acceso: Portales usa 14 y 13 m, la medida de los lóbulos del KML. — Sesión.
- Una puerta `railway=subway_entrance` en el punto medio de cada lado salvo el de las escaleras (`stair_side`, por omisión el que mira al eje de la estación), un nodo en el centro y un `highway=footway` de cada puerta al centro; el grafo llega al centro y su acceso es una de las tres puertas. `closed_doors` por índice o por rumbo del muro sale con `disused:railway=subway_entrance`. San Pedro poniente: escaleras por `-u`, puerta `+u` clausurada. El oriente lleva la misma disposición por simetría y `closed_doors` vacío. — Ricardo en la regla y en el poniente; sesión en la simetría del oriente.

### Contexto de OSM

- Overpass consulta (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final) a 250 m del ancla (`DEFAULT_RADIUS_M`) y el archivo embebe lo que roza la extensión de la estación más 120 m (`CONTEXT_EMBED_M`). Además de lo que ya traía, entran todos los edificios (`way["building"]`) y las barreras (`way["barrier"]`), congelados como escenografía. Solo ways: un edificio multipolígono no entra. Solo las peatonales reciben connectors. — Ricardo en los 120 m, los edificios y las barreras; sesión en el radio de consulta de 250 m.
- No se filtra por altura: puentes y túneles son candidatos de connector. — Ricardo (su frase está en [[task-35]], donde sigue abierto el nivel del connector).

### Consecuencias

- **Bueno:** andenes, área y accesos se derivan de la forma de la estación y de lo que OSM ya tiene, así que una hermana cambia de ancla y rumbo sin redibujar; los pabellones mapeados dejan de duplicarse; la estación se lee dentro de su manzana.
- **Malo:** el archivo modifica y da de baja objetos ajenos (el contorno de Portales y sus 20 vértices) antes de que [[task-11]] cierre la política de importación; el contexto a 120 m multiplica el tamaño del archivo; D1, D2, D3, la simetría del pabellón oriente y la repartición de puertas no tienen observación de campo.

### Cómo se comprueba

`export_station_osm` de las dos estaciones valida sin errores e imprime la franja y el ancho de cada andén (Portales: franja de 12.98 m, andén de 150 m; San Pedro: franja de 15.07 m, andenes de 4.29 m y 152.8/152.5 m) y un banco por línea con su separación y aproche. Regenerar las dos estaciones el 21 de octubre de 2026 con el código de `788d624` (extraído con `git archive`, con la caché de contexto versionada) produjo archivos idénticos byte a byte a los versionados.

## Lo que este ADR deja abierto

- **D3 está siendo reemplazado** (enmendado el 21 de octubre de 2026, ver las notas de enmienda al final). Ricardo corrigió a mano San Pedro de los Pinos en JOSM (`data/osm/reference/san-pedro-de-los-pinos-ricardo-2026-10-21.osm`, 21 de octubre de 2026), y esas correcciones cambian la geometría de la cascada de L7: el espaciado, el aproche y la orientación −2→−1. Ricardo decidió el mismo día enmendar este ADR en vez de reemplazarlo: la geometría nueva está en las notas de enmienda.
- Los supuestos de la v3 pendientes del visto bueno de Ricardo están listados en [[task-26]].

## Supera en parte a [[adr-0011]]

Quedan superadas de [[adr-0011]] y rige lo de arriba: la viñeta «Qué contexto entra» en distancia y contenido (50 m de embebido y 150 m de consulta pasan a 120 m y 250 m, con edificios y barreras); la viñeta «Área de estación» en que se embebe el contorno de OSM tal cual y en que Portales lleva «por esta vez» las dos áreas; y la viñeta «Edificios de acceso» en el cuadrado fijo de 12 m, las tres puertas sobre un mismo lado (`door_side`, que ya no existe en el código) y el nodo de OSM como puerta central. Lo demás de [[adr-0011]] sigue vigente. Como el esquema admite un solo `supersedes` por decisión y [[adr-0011]] sigue vigente en lo demás, no se declara `supersedes`: el enlace va en una nota de enmienda de [[adr-0011]].

## Más información

`data/osm/README.md` (esquema de plantilla y «Supuestos — para revisión»), `data/osm/templates/`, [[2026-09-30-imagenes-sotm-evolucion-portales]] (las tres versiones y la edición a mano), [[task-26]], [[adr-0013]] (catálogo de etiquetas, que la v3 no cambió).

## Notas de enmienda

- 21 de octubre de 2026 (noche), al generar San Joaquín. Ricardo revisó el primer San Joaquín y fijó la regla que manda sobre todo lo demás:

  > Viendo San Joaquín, noto que no estás siguiendo algo que debería ser la regla fundamental inicial: todos los trazos deberían caber dentro del área de la estación. En el caso de San Joaquín, las escaleras son perpendiculares a las vías del tren. Cómo darte de cuenta de eso? Pues no caben si fuera al revés....

  > Te inventaste los edificios de entrada en lugar de respetar los que ya tenía bien establecidos openStreetMap, a pesar de que tenía la etiqueta de building: transportation.

  > Otra cosa que noté es que no trajiste la explanada oriente ni su entrada, que, por cierto, están muy bien dibujadas en el mapa, con todo y entrada y todo, tal vez tengamos que ampliar el radio de lo que traemos para incluirlo.

  > Sí moví la estación de OSM, creo que no debería estar congelado, es más preciso el mío y consistente con todo lo demás que se subirá.

  > Las reglas no deberían ser tan estrictas.

  Lo que cambia en el Resultado, pieza por pieza; quién decidió va al final de cada viñeta, con la misma convención de arriba:

  - **D3 queda reemplazada por la cascada paralela de San Pedro.** Es el trazo que Ricardo corrigió a mano en JOSM (`data/osm/reference/san-pedro-de-los-pinos-ricardo-2026-10-21.osm`), llevado a `l7-deep-cascade.json` y redondeado a medio metro: las −3→−2 bajan hacia el sur, 17 m en planta; las −2→−1 vuelven hacia el norte, 20,5 m al oriente y 16 m al poniente; las −1→0 siguen hacia el norte apiladas encima de las −2→−1, 12,5 m al oriente y 8,5 m al poniente, y desembocan en el centro del pabellón, que queda donde ellas llegan. Entre ejes, 1 a 2,5 m; tramos cortos al nodo de encuentro de 0,5 a 2,5 m. Los bancos se declaran con `junction` + `direction` + `length`. — Ricardo (su trazo); sesión (el redondeo).
  - **Regla de slots.** Mirando el banco desde el nivel bajo, de izquierda a derecha: las eléctricas que bajan, las fijas y las que suben; la reversible de L7 cuenta como la que baja (`reversible_runs`). Manda también en los bancos −2→−1 de San Pedro, aunque su trazo ahí tuviera la fija en el borde. Un `slot` escrito a mano solo vale si todo el banco lo trae. — Ricardo («avanzas por la derecha, los que vienen en el otro sentido, los ves a tu izquierda» y «la fija siempre enmedio»; y que mande también en las −2→−1).
  - **Bancos apilados.** Un banco que va encima de otro declara `stacked_on` y `stack_offset` (corrimiento lateral respecto del de abajo); el generador mide la holgura en planta entre las dos capas y avisa si baja de 0,5 m. Valores de L7: −0,5 m al oriente y −1,5 m al poniente. — Ricardo (los valores y el umbral del aviso); sesión (el mecanismo).
  - **El área del KML es la regla fundamental.** Todo nodo interior propio —andenes, sendas, pasillos, escaleras, nodos de encuentro, torniquetes— cae dentro del área; la validación lo trata como **error**, con la lista completa de nodos fuera, y ya no como aviso. — Ricardo.
  - **Encaje en las hermanas.** La plantilla es el trazo de su estación de referencia, y el bloque `fit` guarda las medidas del KML de esa estación (bordes de la franja, u de los tres ramales por lado, v del vestíbulo transversal). En otra estación: (1) los corredores (pasillos de andén, vestíbulo transversal, paso bajo las vías, escaleras de cambio de andén) se deforman por tramos de las medidas de referencia a las medidas de la hermana, solo si alguna discrepa más de 1,5 m; (2) cada cascada (`fit.cascades`: sus bancos, sus `extra_ways` marcados con `cascade` y su pabellón) se mueve en bloque, sin deformarse, probando primero tal como está dibujada y después las ocho simetrías del cuadrado ancladas al pabellón de OSM; cabe la que deja todos sus puntos dentro del área y el centro del pabellón dentro del pabellón. Entre las que caben gana, en este orden: la que no mete las escaleras por el muro donde OSM ya tiene la puerta, la paralela a las vías como San Pedro, la de pasillo de aproche más corto. Si ninguna cabe se prueban las cascadas acortadas a lo largo de su eje (95 % a 70 %) y, si tampoco, el archivo se escribe y el comando falla con las medidas. Los vértices de un rodeo propio del trazo de referencia (`via`) se cambian por un codo en L dentro del área cuando la cascada se mueve. En San Joaquín las dos cascadas salen perpendiculares a las vías, reflejadas, sin acortar. — Ricardo (que todo quepa y que San Joaquín vaya perpendicular «porque no caben si fuera al revés»; la preferencia por la paralela venía del encargo); sesión (el mecanismo, el orden de preferencia y la tolerancia de 1,5 m).
  - **Alcance del segundo criterio de decisión.** «Las plantillas declaran relaciones con la franja del KML, no coordenadas» rige ahora solo para los andenes: las cascadas se declaran en coordenadas del trazo de referencia y el encaje las lleva a cada hermana. — Sesión (consecuencia del encaje).
  - **Pabellones de OSM aunque lleven `building=transportation`.** Un way con etiqueta de contorno de estación (`building=train_station|transportation` o `public_transport=station`) cuya intersección sobre unión con el área del KML es menor que 0,25 no es el contorno sino un pabellón, y se adopta como tal; en San Joaquín los dos pabellones dan 0,05 y el contorno de Portales 0,71. La entrada `railway=subway_entrance` de OSM que está dentro del pabellón o a menos de 2 m de sus muros se adopta como el acceso aunque la base no la enlace; si la plantilla clausura justo esa puerta, la puerta se deja abierta y se avisa. — Ricardo (adoptar los pabellones; decisión del 21 de octubre, en [[2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin]]); sesión (los umbrales de 0,25 y 2 m y la regla de la puerta).
  - **Explanadas de OSM.** Las explanadas `highway=pedestrian` mapeadas como multipolígono se traen con su relación y sus anillos, congeladas; la puerta de un pabellón adoptado que cae sobre el anillo de una explanada (a 0,3 m o menos) se mete como vértice de ese anillo, que sale con `action='modify'`, y así el acceso queda conectado sin un connector pegado al muro. Donde OSM tiene la explanada no se dibuja la cuadrada. Los anillos de explanada cuentan como destino de connector. — Ricardo (traer la explanada y su entrada); sesión (cómo se conectan).
  - **Radio de contexto.** Se midió: la explanada oriente de San Joaquín queda entre 19 y 67 m del ancla y la poniente llega a 123 m, dentro de los 120 m de embebido medidos desde lo dibujado. No faltaba radio: faltaba traer las relaciones, que la consulta no pedía. Se conserva 120 m de embebido y 250 m de consulta, ahora como parámetro (`--context-radius`, y la consulta cubre ese radio más 130 m). `CONNECTOR_MAX_M` sube de 40 a 45 m, porque los dos connectors que Ricardo trazó en San Pedro desde el acceso oriente miden unos 42,5 y 44,7 m en su archivo (41,2 y 42,1 m los generados) y con 40 se perdían. — Ricardo (los connectors de su trazo); sesión (no ampliar el radio y el nuevo tope).
  - **El nodo de estación de OSM lo recoloca el generador.** Excepción explícita al principio de [[adr-0011]] de no mover lo ajeno: el `railway=station` se lleva al eje de la franja de andenes, en la u del cruce de la estación que declara la plantilla (`station_node`): en L7 el paso bajo las vías, en Portales el vestíbulo-puente, y si ahí hay un nodo nuestro se corre sobre el eje hasta quedar a 1 m. Reproduce la posición en que Ricardo dejó el 681454741 en San Pedro a 0,8 m. Como el nodo suele ser vértice de la línea `railway=subway`, la línea se dobla con él. Movimientos: San Pedro 29,7 m, San Joaquín 2,8 m, Portales 14,5 m. — Ricardo (descongelarlo); sesión (la regla).
