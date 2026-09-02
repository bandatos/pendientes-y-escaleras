---
type: reference
id: 2026-09-02-investigacion-osm-indoor-y-estado-l2-l7
title: "Mapeo indoor de estaciones en OSM: reglas del wiki, estaciones modelo, formato JOSM y estado de las Líneas 2 y 7"
state: current
date: 2026-09-02
related: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]", "[[2026-08-26-alineacion-catalogos-osm]]", "[[2026-08-26-herramientas-mapeo-kml-plantillas]]", "[[adr-0010]]"]
---

# Mapeo indoor de estaciones en OSM: reglas del wiki, estaciones modelo, formato JOSM y estado de las Líneas 2 y 7

# Mapeo indoor de estaciones en OSM: reglas del wiki, estaciones modelo, formato JOSM y estado de las Líneas 2 y 7

Investigación del 2 de septiembre de 2026 (Overpass `overpass-api.de`, base OSM al 2026-09-02T06:00Z; wiki de OSM y de JOSM). Complementa a [[2026-08-26-alineacion-catalogos-osm]] con lo que faltaba: ejemplos reales verificados, el formato de archivo y el estado concreto de las dos líneas de las primeras estaciones.

## Reglas del wiki que gobiernan

- IndoorOSM está muerto: «now is defunct and has been replaced… Please do not use for any new projects». El consenso es Simple Indoor Tagging (SIT).
- Niveles de una escalera, ambas sintaxis válidas: «`level=0;1` or `level=0-1` could be used on some stairs that connect levels 0 and 1» (SIT) y «Use a hyphen (-) to specify a range… `level=-2-32`» (Key:level). El `level` de una escalera codifica presencia, no conectividad: «regardless whether level 3 can be accessed from these stairs». Se adoptó punto y coma ([[adr-0010]]): un elevador que salta un nivel (`level=-2;0`) no se puede expresar como rango.
- Elevador: nodo `highway=elevator` con lista de niveles, ejemplo del wiki «`level=-1;0;1;2`»; en SIT además `indoor=room` o `indoor=area`.
- Pasillos: `Tag:indoor=corridor` dice «`highway=corridor` is the way routers can follow», pero `Tag:highway=corridor` reconoce que «at least GraphHopper and OSRM ignore it» y que `highway=footway` + `indoor=yes` tiene 79 222 usos contra 70 010. SIT no tiene sección de ruteo.
- Puertas: «Staircases and escalators… are connected to other indoor spaces… via a `door=*` node on each floor (including `door=no`…)». No se adoptó por ahora: la conectividad se resuelve por nodo compartido.
- `repeat_on` excluye el nivel de partida: «a feature with level='0' then repeat_on starts with '1'».
- `layer` vs `level`: «Ways in buildings… should be mostly described with level=* instead of layer»; «A change in layer should not be used to indicate a change in elevation». Dentro de la estación se usa `level`; `layer` solo en el andén subterráneo (Metro Mapping) y en el puente de Portales.
- Andén: `area=yes` «is not required» para `public_transport=platform`, pero `railway=platform` sí lo pide; se ponen las tres.
- Accesos: `railway=subway_entrance` solo en nodo, «tagged as a node on a way leading to (or exiting from) the station»; `name` es el nombre de la salida, no de la estación; `ref` con la letra o número. En la relación `stop_area` el rol vacío es el correcto: el rol `entrance` es «redundant» y `subway_entrance` no está documentado. El wiki no documenta miembros indoor en `stop_area`: declarar que un pasillo pertenece a una estación no tiene forma estándar.

## Estaciones modelo verificadas

**Taubstummengasse, Viena U1** (nodo 3500582336): la analogía más cercana a una estación de paso del Metro. Sin polígonos `indoor=level`; los niveles viven en `level` de cada objeto. El andén es un solo objeto `indoor=corridor` + `public_transport=platform` + `railway=platform` + `level=-2` (relación multipolígono 6227976). Elevador doble: nodo `highway=elevator` + polígono `indoor=room` + `elevator=yes`, ambos `level=-2;0` con el mismo `ref`. Escaleras eléctricas: `highway=steps` + `conveying=forward` + `incline=up` + `indoor=yes` + `level=-1;0`, siempre `forward`, con la vía dibujada en el sentido de viaje (vías 418912615, 418912637, 418912675, 418912676). Escaleras fijas con `step_count`, `width`, `incline=down` dibujadas de arriba abajo. Accesos: `railway=subway_entrance` + `entrance=yes` + `level=0` + `name=<calle>` + `wheelchair`. Muros por nivel `indoor=wall`.

**Zieglergasse, Viena U3** (nodo 4348437231): añade andenes apilados a −2 y −3, `level=-3;-1` en escaleras largas que saltan un nivel, y una capa completa de líneas de ruteo `highway=footway` + `indoor=yes` + `level` junto a las áreas `indoor=corridor` (vías 495695647, 495706585, 495711217). Usa `layer` redundante con `level` en algunas vías.

**Amrumer Straße, Berlín U9** (nodo 29045595): andén central `ref=1;2`, `area=yes`, `layer=-2` + `level=-2`; elevador nodo `level=-1;0;1;2;3;4;5`.

**Louvre-Rivoli, París**: trampa. Lo indoor es el museo; el metro son dos vías de andén y un acceso, con sintaxis IndoorOSM muerta (`buildingpart=verticalpassage`) y niveles fraccionarios. No usar.

## Balbuena (Línea 1): el precedente local

Alguien ya empezó a mapear indoor una estación del Metro (vías 1547147224, 1547147225 andenes con `indoor=area`, `destination`, `layer=-1`, `level=-1`; escaleras 1547147173 a 1547147182; relación `stop_area` 7898709). Tres defectos: `conveying=island` no existe (los valores son `yes`, `forward`, `backward`, `reversible`); `layer=-2;-1` no admite lista y varias vías llevan `layer` sin `level`, invisibles para el filtro de niveles de JOSM; niveles inconsistentes (`level=-1;0` y `level=0;-1`). Usa `tunnel=building_passage`. No se copia; sí obliga a decidir en comunidad si publicamos una convención que la corrija ([[task-10]], [[task-11]]).

## Formato de archivo y JOSM

- No hay página del wiki de JOSM para el formato; la canónica es «JOSM file format» en el wiki de OSM: ids negativos crean objetos, «IDs have to be allocated uniquely throughout the document»; `action=modify|delete` solo para objetos existentes; en nuevos se omiten `version`, `timestamp`, `changeset`. `visible='true'` es opcional; se escribe.
- `upload`: `true` normal; `false` avisa antes de subir; `never` desactiva el botón y «not possible» de cambiar desde la GUI, solo editando el archivo (Help/Action/EncourageDiscourageUpload).
- JOSM renumera los ids negativos al cargar (ticket 12197, wontfix): nunca sirven como clave de unión. La traza va en etiquetas (`note:*`, se retiran antes de subir).
- Ticket 18293 (corregido, r15515): el test de cruces trata `level` como `layer`, así que vías en niveles distintos que se cruzan en planta no se reportan. `UnconnectedWays` («Way end node near other way») no cambió: esperar muchos avisos en estaciones apiladas.
- El filtro automático de niveles del núcleo solo lee `level`; ignora `repeat_on`, `min_level`, `max_level` (ticket 16523, abierto). indoorhelper lo cubre y sigue activo (v269, agosto de 2026).
- Errores que sí importan: nodos duplicados (dos objetos que parecen tocarse pero no comparten nodo rutean desconectados); vías sin etiqueta.
- Fusión: un archivo todo-nuevo mergeado con Ctrl+M sobre la descarga real no puede tener conflictos; conectar con objetos existentes es una pasada manual por estación.

## Estado de las Líneas 2 y 7 en OSM

Relaciones de ruta: 443191 y 7935435 (L2), 5365308 y 7935373 (L7), todas `network=STC Metro`; el rol `stop` mezcla nodos `station` y `stop_position` a partes iguales. Transbordos y terminales coinciden exactamente con Wikipedia: L2 transborda en Tacuba, Hidalgo, Bellas Artes, Pino Suárez, Chabacano y Ermita; L7 en El Rosario, Tacuba, Tacubaya y Mixcoac. Zócalo, San Antonio Abad y San Pedro de los Pinos no son transbordo.

En todas las estaciones de ambas líneas, dentro de 120 m: cero escaleras eléctricas, cero elevadores salvo uno en Zócalo (nodo 13829291845, a la vez `railway=subway_entrance`), un solo «andén» fuera de transbordos y terminales, el de Zócalo (vía 1251764016), que en realidad es el cajón completo de 180 × 55 m y no un andén. Accesos por estación de L2: Zócalo 7, Panteones 3, Cuitláhuac 2, San Cosme 2, Revolución 2, Allende 2, Xola 2, Villa de Cortés 2, Portales 2, Colegio Militar 1, Nativitas 1, Popotla 0, Normal 0, San Antonio Abad 0, Viaducto 0, General Anaya 0. De L7: Aquiles Serdán 4 (nombrados con el nombre de la estación, contra el wiki), Camarones 4, Polanco 3, San Joaquín 2, Constituyentes 2, San Antonio 2, Auditorio 1, San Pedro de los Pinos 1, Refinería 0.

Rumbo de vía: L7 es una sola vía (320892187) de 130 vértices en 17,4 km, espaciado mediano 66 m, con `level=-4` y `layer=-4` en toda su longitud; en Camarones y Polanco solo hay un vértice a 150 m, así que no da rumbo. L2 (vía 616927360) tiene 20 m de espaciado mediano. En Viaducto, Xola, Villa de Cortés y Nativitas no hay vía `railway=subway` a menos de 60 m del nodo de estación. El nodo de estación de San Pedro de los Pinos (681454741) está 31 m al oriente del eje de la Avenida Revolución, es el único vértice de la vía de L7 cerca de la estación y lleva `service=yard`. La relación `stop_area` de Zócalo (7902754) usa el rol `subway_entrance`.

## Anomalías de los seis grafos candidatos en la base

Extraídos de la base el 2 de septiembre (Portales, Xola, Cuitláhuac, Panteones, San Pedro de los Pinos, San Joaquín; scripts reproducibles en `.claude/scratch/`, fuera del repo). Portales y Xola son idénticos (9 nodos, 12 pathways, cuatro escaleras paralelas andén–vestíbulo); San Pedro y San Joaquín son idénticos (14 nodos, 26 pathways). En los seis: `stair_count`, `length`, `traversal_time`, `max_slope`, `pathway_description` y `code_identifiers` vacíos; ningún pathway de modo 5 (elevador), 6 ni 7 (torniquetes): los torniquetes solo existen como nombre de nodo. Xola tiene tres elevadores en `data/raw/elevadores_escaleras_v4.csv` y ninguno en la base, siendo la única con `wheelchair_boarding=1`. Panteones está submapeada (7 aristas, sin eléctricas, sin edificios de acceso, ausente del CSV). La dirección de almacenamiento de las aristas bidireccionales es ruido (una de tres paralelas guardada al revés en Cuitláhuac y San Joaquín). El comando `export_station_graph` colapsa los pathways paralelos y omite `entrance`, `is_closed`, `is_double`, lat/lon: no sirve para geometría.
