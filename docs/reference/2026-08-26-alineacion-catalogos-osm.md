---
type: reference
id: 2026-08-26-alineacion-catalogos-osm
title: Alineación de nuestro esquema con los catálogos de etiquetado de OSM
state: current
date: 2026-08-26
related: ["[[2026-08-26-sesion-mapeo-osm]]", "[[adr-0003]]", "[[adr-0004]]"]
---

# Alineación de nuestro esquema con los catálogos de etiquetado de OSM

Investigación del 2026-08-26. Todos los conteos de uso provienen de la API de taginfo (`taginfo.openstreetmap.org/api/4/…`), con `data_until: 2026-08-26T00:59:38Z`, y son `type=all` (nodos + vías + relaciones) salvo que se indique el desglose. Los conteos sobre el Metro CDMX provienen de consultas Overpass ejecutadas ese día sobre el bbox `19.15,-99.40,19.75,-98.90`. Nada está estimado: donde una consulta falló, se dice. Lo decidido a partir de este informe está en [[adr-0003]] y [[adr-0004]]; el catálogo como configuración del generador es [[task-19]].

Tres advertencias sobre el estatus de lo que sigue.

**Primera: no existe una tabla oficial GTFS→OSM que cubra lo que nos importa.** La página que se acerca, [GTFS/Mapping to OSM tags](https://wiki.openstreetmap.org/wiki/GTFS/Mapping_to_OSM_tags), lleva un aviso en el encabezado: *«As of 2017-04-08, this mapping has not gained consensus, and is for reference only»*. Y, más importante, **sólo cubre `stops.txt`, `routes.txt` y `trips.txt`**: el wikitext completo (6 437 caracteres) no contiene ninguna sección para `levels.txt` ni para `pathways.txt`. Dentro de `stops.txt`, la columna «equivalente OSM» está **vacía** para `location_type=2` (Entrance/Exit), `location_type=3` (Generic Node), `location_type=4` (Boarding Area) y para `level_id`. Es decir: justo la mitad del modelo que estamos levantando —accesos, niveles y caminos internos— es territorio sin mapeo documentado. Lo que sigue se ensambló etiqueta por etiqueta.

**Segunda: se distinguen tres niveles de autoridad** y se marcan en cada afirmación. **[wiki]** = documentado en la página de la etiqueta. **[aprobado]** = pasó por votación formal. **[de facto]** = el uso domina pero no hay votación ni prosa que lo respalde. Cuando algo es lectura del investigador y no hecho documentado, se dice explícitamente.

**Tercera: dos huecos que no se pudieron cerrar.** No se consiguió el conteo de elementos `indoor=*` ya existentes en las estaciones del Metro CDMX desde este informe (Overpass limitó por tasa; los espejos de kumi.systems y private.coffee devolvieron 500/502) — el informe de herramientas ([[2026-08-26-herramientas-mapeo-kml-plantillas]]) sí lo obtuvo después: la capa interior está vacía. El segundo hueco: las verificaciones Overpass de numeración de salidas en Seúl, Madrid, Hong Kong y Pekín fallaron; sólo Tokio salió. Los conteos globales de taginfo cubren la misma pregunta con una muestra mayor.

## 1. Jerarquía de estación y parada

### 1.1 Correspondencia

| Nuestro campo/valor | OSM | Notas |
|---|---|---|
| `Station` (modelo propio, agrupa stops) | `public_transport=station` (203 457) + `railway=station` (103 861) + `station=subway` (20 534) o `subway=yes` (74 102) | **[aprobado]** PTv2 desde 2011. [Metro Mapping](https://wiki.openstreetmap.org/wiki/Metro_Mapping) prescribe nodo único; *«The location of the node is irrelevant»* — y advierte que eso genera controversia porque los renderizadores lo muestran de forma prominente |
| `Station.name` | `name` | En CDMX los nombres viven en `name` a secas: de 214 objetos `station=subway`, **`name:en` = 0** y **`name:es` = 1** |
| `LocationType 0` Stop/Platform | `public_transport=platform` (4 149 487) + `railway=platform` (194 996); `public_transport=stop_position` (1 598 405) si es el punto sobre la vía | Ver §6 |
| `LocationType 1` Station | como arriba | |
| `LocationType 2` Entrance/Exit | `railway=subway_entrance` (53 535) | Ver §4. **La tabla oficial GTFS→OSM deja esta celda vacía** |
| `LocationType 3` Generic Node | *sin equivalente* | En GTFS es el nodo de conexión de pathways. En OSM el nodo de unión entre vías no se etiqueta: existe por topología. **Concepto que sólo tiene nuestro lado** |
| `LocationType 4` Boarding Area | *sin equivalente* | GTFS lo define como sección de andén con característica especial de abordaje. Lo más cercano en OSM es `railway=platform_edge` (§6), pero no es lo mismo |
| `Stop.parent_station` | `public_transport=stop_area` (567 591) con roles | Ver §1.2 |
| `Stop.stop_code` | `ref` | **[wiki]** |
| `Stop.stop_name` | `name` | |
| `Stop.stop_desc` | `description` | |
| `Stop.stop_url` | `url` / `website` | |
| `Stop.stop_lat/lon` | geometría del objeto | La tabla oficial anota: *«not always accurate»* |
| `Route.route_short_name` = «1»…«12», «A», «B» | `ref` en la relación `type=route` + `route=subway` | |
| `Route.route_color` | `colour` (hex con `#`) | `route_text_color` **no tiene equivalente**: la tabla oficial deja la celda vacía |
| `Route.route_type=1` | `route=subway` + (`type=route`, `type=route_master`) | |
| `Route.route_long_name` | `gtfs:name` | **[wiki]** *«`name` has a different syntax»* — el `name` de una relación de ruta en OSM sigue una plantilla propia, no es el nombre largo del feed |
| `Route.route_desc` | `description` | |
| `Route.route_sort_order` | *sin equivalente* | |
| `Shape`, `Trip`, `StopTime` | *fuera de alcance de OSM* | **[wiki]** La página [GTFS](https://wiki.openstreetmap.org/wiki/GTFS) lo dice de frente: *«in many cases timetables change so often that representing them in OSM is de facto impossible»*. Los horarios se quedan en el feed |
| `Station.x_position`, `y_position`, `rotation`, `end_anchor`, `viz_params`, `miro_frame_id` | *sin equivalente, y correctamente así* | Son coordenadas del diagrama esquemático de Miro, no geografía. OSM es geográfico |

### 1.2 Las relaciones `stop_area`: qué se pierde al no usarlas

El colectivo acordó en la reunión del 19 de agosto no usar relaciones por ahora; [[adr-0004]] decide después sumar nuestros accesos a las existentes. Lo que una `stop_area` aporta, documentado: la página [Tag:public_transport=stop_area](https://wiki.openstreetmap.org/wiki/Tag:public_transport%3Dstop_area) (estatus **aprobado**) define los roles: `stop` para posiciones de parada, `platform` para andenes, y **rol vacío** para el objeto `public_transport=station`, para las entradas `railway=subway_entrance` y para amenidades. Metro Mapping añade los roles `entry_only` y `exit_only` para accesos direccionales.

La ganancia formal es **deduplicación de identidad**. En la página de `public_transport=stop_position`, los campos `name`, `ref`, `uic_ref`, `uic_name`, `operator` y `network` están marcados cada uno como *«recommended if no `public_transport=stop_area` exists, otherwise optional»*. Eso es el wiki diciendo, en lenguaje normativo, que la relación es donde vive la identidad compartida; sin ella hay que repetirla en cada miembro.

Lo que se pierde, según la guía de consumo: [Refined Public Transport/Consuming](https://wiki.openstreetmap.org/wiki/Proposal:Refined_Public_Transport/Consuming) describe el respaldo geométrico cuando no hay relación: asociar entradas dentro de ~200 m de un andén y el objeto estación dentro de ~50 m. Y advierte que ese método es *«prone to errors, especially when there is an underground PT network or an interchange»*. **Ese es exactamente nuestro caso**: estaciones profundas donde una salida puede quedar a 300 m del andén, y correspondencias tipo Pantitlán o Tacubaya donde varias líneas comparten superficie. Sin relación, el consumidor no puede saber si una salida pertenece a la Línea 1 o a la 9.

Matiz: no hay documentación de que OTP, OSRM o Valhalla consuman `stop_area`. La página de [OpenTripPlanner](https://wiki.openstreetmap.org/wiki/OpenTripPlanner) dice que usa OSM para banquetas, ciclovías y calles, y que su modelo de transporte viene de GTFS/NeTEx. Los consumidores documentados de `stop_area` son las apps de metro (Organic Maps / CoMaps vía el esquema Metro Mapping) y la guía PTv3. La frase «los routers usan stop_area» es **no probada**.

**Estado real en CDMX (Overpass, 2026-08-26): 383 relaciones `public_transport=stop_area` en el bbox, de las cuales 58 llevan `network=STC Metro`.** Aproximadamente **58 de ~195 estaciones ya tienen stop_area**. Años de última edición de esas 58: 16 en 2018, 21 en 2025, 5 en 2026. **Hay mantenimiento activo y reciente.** Si subimos accesos sin sumarlos a las relaciones existentes, dejaremos huérfanos objetos que otros mapeadores están curando.

### 1.3 PTv2 y su supuesta obsolescencia

**Nada de la jerarquía PTv2 está obsoleto.** La página [Public transport](https://wiki.openstreetmap.org/wiki/Public_transport) es explícita sobre el esquema viejo: *«The Original Public Transport Schema… is still (2024) widely in use, and most of the tags are more common than newer alternatives. Some mappers discourage using these tags, although none have been deprecated»*.

Las dos propuestas de simplificación: [Refined Public Transport](https://wiki.openstreetmap.org/wiki/Proposal:Refined_Public_Transport) («PTv3»): estatus literal **«Proposed (under way)»**, borrador de 2018-07-08, ocho años sin votarse; desaconseja las posiciones de parada pero las mantiene opcionales, y convierte la `stop_area` en el objeto central. [Drop stop positions and platforms](https://wiki.openstreetmap.org/wiki/Proposal:Drop_stop_positions_and_platforms): estatus **«Abandoned (inactive)»**.

El propio [Metro Mapping](https://wiki.openstreetmap.org/wiki/Metro_Mapping) —la guía de facto para metros, implementada por Organic Maps— proviene de una propuesta **rechazada** ([Proposed features/Metro Mapping](https://wiki.openstreetmap.org/wiki/Proposed_features/Metro_Mapping), votación cerrada 2017-11-24). La página sobrevivió como descripción de práctica: *«While all of the tagging described here is used on the map, some things are still in discussion»*. Es la mejor guía operativa y a la vez no tiene autoridad formal.

Regla de Metro Mapping fácil de violar: *«Please refrain from using the same node for both a stop_position and a station. That would prevent a possible interchange from being mapped correctly.»*

### 1.4 Cómo está mapeado hoy el Metro CDMX (medido)

Sobre **214 elementos con `station=subway`** en el bbox:

| Clave | Valor dominante | Conteo |
|---|---|---|
| `network` | `STC Metro` | **192** (ausente 15, `Metro CDMX` 6, `Línea A` 1) |
| `operator` | `Sistema de Transporte Colectivo` | **126** (ausente 84, `STC` 4) |
| `network:wikidata` | `Q735042` | 51 |
| `operator:wikidata` | — | **0** |
| `subway=yes` | | 213 |
| `wikidata` / `wikipedia` | `es:…(estación)` | ~160 |
| **`ref`** | | **0 — ausente en las 214** |
| **`check_date`** | | **0** |
| **`gtfs:stop_id`** | | **0** |

Sobre **447 nodos `railway=subway_entrance`**: `network=STC Metro` en 175, `operator` en apenas 7, y **`ref` presente en exactamente 1 acceso** (valor `H`).

Sobre **24 relaciones `route=subway`** (12 líneas × 2 sentidos): `network=STC Metro` en 24/24, `operator=Sistema de Transporte Colectivo` en 24/24, `network:wikidata=Q735042` en 24/24, `ref` y `colour` correctos en todas. Pero sólo existen **5 `route_master=subway`** (refs 12, 7, 2, 3, 6): siete líneas no tienen relación maestra.

La convención `network=STC Metro` / `operator=Sistema de Transporte Colectivo` **existe únicamente en los datos, no está documentada**: la página [ES:Metro de la Ciudad de México](https://wiki.openstreetmap.org/wiki/ES:Metro_de_la_Ciudad_de_M%C3%A9xico) es sólo una tabla de las 12 líneas con sus IDs de relación. Esa convención sí es coherente con el wiki general: [Key:operator](https://wiki.openstreetmap.org/wiki/Key:operator) dice que *«rail or public transport companies' names are abbreviated in `network=*` but spelled out in full in `operator=*`»*.

## 2. Niveles

### 2.1 La corrección conceptual que cambia el mapeo

`level` no es «el número de piso tal como está señalizado». [Key:level](https://wiki.openstreetmap.org/wiki/Key:level) (de facto, 2 401 280 usos) es explícito: *«In general, the `level` key ignores these distinctions in favor of the zero-based numbering scheme, because the `level` key was originally envisioned as a machine-readable key for 3D building rendering. Data consumers that support the Simple Indoor Tagging require values to be numeric and consecutive, even for basements and mezzanines that in reality are known by mnemonics such as 'B', 'B1', 'G', 'M', and '2M'.»*

El nombre señalizado va en **[`level:ref`](https://wiki.openstreetmap.org/wiki/Key:level:ref)** (en uso, 72 622). El ejemplo del wiki: `level=0` / `level:ref=LG`; `level=1` / `level:ref=G`; `level=2` / `level:ref=1`. Asigna enteros consecutivos por apilamiento físico y mete cada peculiaridad local en `level:ref`. Advertencia operativa: *«Tagging shops exclusively with `level:ref` can be problematic because a data consumer cannot reliably determine the relative vertical order of each floor.»* **Siempre las dos claves, juntas.**

### 2.2 Correspondencia

| Nuestro campo | OSM | Notas |
|---|---|---|
| `Level.level_index` (float; 0 suelo, negativo abajo) | `level` | Misma convención de origen y signo. Conflicto sólo en fraccionarios, §2.3 |
| `Level.level_name` (p. ej. «Andenes») | `level:ref` y/o `name` | En `indoor=level`, `name` es «Planta baja» y `level:ref` es el código de la señalética |
| `Level.level_id` | — | Identificador interno; ver §7 |
| `Level.route` (FK a Route) | *sin equivalente* | Nuestro nivel está adscrito a una línea; en OSM el nivel es del edificio/estación. **Concepto sólo nuestro** |
| El conjunto de niveles de una estación | polígono `indoor=level` (5 783) por nivel, con `level` + `level:ref` + `name` + `height` | Una fila de `levels.txt` convertida en geometría. Documentado sólo dentro de [Simple Indoor Tagging](https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging) |
| Extensión vertical de la estación | `min_level` (11 356) + `max_level` (6 104) en el contorno del edificio | **[wiki]** SIT: *«To make it easy for data consumers to find buildings with indoor coverage we suggest the tags `min_level` and `max_level`»*. No están obsoletos |
| — | `repeat_on` (9 257) | No es alternativa a min/max_level. Sirve para elementos repetidos idénticamente en varios pisos. SIT: *«This should be used sparingly»*. *«The starting level is not included in this list»* |
| — | `layer` | **[wiki]** Key:layer: *«Floors within a building should be tagged with `level` rather than layer»* y *«Negative values do not imply that object is underground, use `location=underground` for this purpose»* |

**La excepción de `layer` en metros.** Metro Mapping lista `layer=-N` como etiqueta **obligatoria** del andén: *«`layer=-N` if the platform is underground, so it is drawn underneath other features. N should be at least 3, varies by the city»*, con `level=-M` sólo *«también recomendado»*. Coexisten: `layer` resuelve el orden de dibujo entre la estación y las calles que le pasan por encima; `level` resuelve el orden **dentro** de la estación. En Marienplatz ambos conviven: `layer` en 176 de 246 elementos indoor, `level` en 220.

### 2.3 Formatos de valor y el problema del `0.5`

| Forma | Conteo | Estatus |
|---|---|---|
| `level=0` | 1 085 736 | |
| `level=-1` | 226 960 | |
| `level=-2` | 49 138 | |
| `level=-3` | 16 359 | |
| `level=-4` | 5 674 | |
| `level=0;1` (lista con punto y coma) | **42 890** | **[wiki]** idioma dominante |
| `level=-1;0` | 29 252 | |
| `level=0.5` (entreplanta) | 7 932 | **[wiki] pero explícitamente sin resolver** |
| `level=-2-0` (rango con guion) | **54** | válido pero casi sin uso |
| `level=-1--3` (rango de mayor a menor) | **0** | **malformado** — los rangos se escriben de menor a mayor |

Key:level: *«There is also an ongoing discussion on usage of fractional values, e.g. `level=0.5`… See the proposals for more examples»* — con nota editorial `Where is such proposal? Add link`. **`level=0.5` tiene 7 932 usos reales pero ninguna propuesta aprobada detrás, y contradice el requisito de «numeric and consecutive».** Nuestro caso: el piloto de San Pedro de los Pinos tiene 5 niveles con `level_index` 0, −1, −2, −3, −4, todos enteros y consecutivos; Tacubaya trae «Mezzanine −2.5» y «−1.5» en nombres de nodos → [[task-13]].

Referencia comparable: en **Marienplatz (Múnich)** los valores de `level` son cuatro enteros consecutivos subterráneos (−1 ×96, −4 ×39, −2 ×16, −3 ×15) y los objetos multinivel usan **listas con punto y coma, nunca rangos con guion y nunca fraccionarios**.

### 2.4 Esquemas muertos

[IndoorOSM](https://wiki.openstreetmap.org/wiki/Proposal:IndoorOSM) está **obsoleto**: *«Please do not use for any new projects.»* La clave `buildingpart=*` sobrevive con 7 057 usos y sin página. [Relation:building](https://wiki.openstreetmap.org/wiki/Relation:building): *«This kind of relation modeling was also used for indoor mapping to group building levels, but with the introduction of Simple Indoor Mapping in 2012 these relations are deprecated»*. **No hay relación de agrupación que construir**: la pertenencia es geométrica.

## 3. Modos de pathway (GTFS 1–7)

### 3.0 La regla que cruza todo: la dirección de la vía

Tres atributos —`incline=up/down`, `conveying=forward/backward` y `oneway:foot`— **son relativos al orden de los nodos de la vía en OSM**, mientras que en GTFS la referencia son los extremos nombrados `from_stop_id` → `to_stop_id`. Si alguien invierte la geometría de una vía en JOSM, los tres se invierten en significado y nada en OSM registra cuál extremo era el «from». **Es la vía de corrupción silenciosa más probable de toda la conversión**: la convención de dirección debe ser campo de primera clase en nuestro esquema.

### 3.1 Modo 1 — Pasillo (Walkway)

`highway=footway` (32 445 063) + `indoor=yes` + `level=*`. `footway=*` no aplica (sus valores documentados son `sidewalk`, `crossing`, `link`; `footway=corridor` tiene 609 usos).

**`highway=corridor` vs `indoor=yes`.** [Tag:highway=corridor](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dcorridor) (de facto, 78 753) no está formalmente obsoleto, pero su propia página documenta que perdió: *«as of 2026-02, `highway=footway` + `indoor=yes` = 79 222 vs `highway=corridor` = 70 010»*, *«close to 80% [of] `highway=corridor` also have `indoor=yes` added, with overlapping meaning»*, y *«as of 2025-08, at least GraphHopper and OSRM ignore it, while Valhalla seems to understand it»*. `indoor=corridor` (26 388) es en SIT el **área** encerrada, no la línea transitable.

**`tunnel` vs `covered`: incorrectos para un pasillo interior.** [tunnel=building_passage](https://wiki.openstreetmap.org/wiki/Tag:tunnel%3Dbuilding_passage) se define como pasaje que atraviesa un edificio *«but is not inside the building itself»*. [Key:covered](https://wiki.openstreetmap.org/wiki/Key:covered): *«usually open at least on one side»*. Un pasillo del Metro es espacio interior: `indoor=yes` + `level` (+ `location=underground`). Contaminación real en los datos: `conveying=yes` + `tunnel=yes` aparece 2 167 veces y `highway=corridor` + `tunnel=yes` 3 305 veces.

### 3.2 Modo 2 — Escaleras fijas

| Nuestro campo/valor | OSM | Notas |
|---|---|---|
| `pathway_mode=2` | `highway=steps` (2 113 419) | **[wiki]** |
| `stair_count` (signo = dirección) | **`step_count` = `abs(stair_count)`** (522 862) + `incline` | `step_count` es entero positivo sin signo |
| signo de `stair_count` | `incline=up` (858 211) / `incline=down` (624 261) | **[wiki]** *«As one moves forward on a way, a positive incline gets higher»* |
| *(no lo modelamos)* | `handrail` (716 835): `yes` 497 564, `no` 205 257; `handrail:left` 47 171, `:right` 47 077, `:center` 13 924 | §9 |
| *(no lo modelamos)* | `ramp` (515 078), `ramp:wheelchair` 46 504, `ramp:stroller` 37 530, `ramp:bicycle` 27 323, `ramp:luggage` 8 245 | `ramp=yes` sólo 74 672 → la mayoría son `ramp=no` explícitos |
| *(no lo modelamos)* | `width`, `surface`, `tactile_paving`, `lit` | §9 |

Guía explícita sobre tramos y descansos: *«Consider splitting long steps into sections for each flight of steps with the landing between each flight as `highway=footway`»*. `landing=*` (1 465) para contar descansos sin partir la vía. `stairwell` (3 152) no está documentado como sub-etiqueta estándar: no usar.

### 3.3 Modo 3 — Cinta transportadora

`highway=footway` + `conveying=*`. [Key:conveying](https://wiki.openstreetmap.org/wiki/Key:conveying) cubre ambos casos y los distingue el `highway=*` acompañante. `travelator` tiene 2 usos. `conveying=yes` + `highway=steps` = 13 343 frente a `conveying=yes` + `highway=footway` = 1 916.

### 3.4 Modo 4 — Escalera eléctrica

Base: `highway=steps` + `conveying=*`. **[aprobado]** [Escalators and Moving Walkways](https://wiki.openstreetmap.org/wiki/Proposal:Escalators_and_Moving_Walkways), votación cerrada 2012-09-14.

| Valor | Definición **[wiki]** | Conteo |
|---|---|---|
| `yes` | escalator / moving walkway with unspecified direction | 16 417 |
| `forward` | Movement in way direction | 13 448 |
| `backward` | Movement opposite to way direction | 3 353 |
| `reversible` | Movement either with or opposing direction of way at one moment | **2 119** |
| `no` | no es escalera eléctrica / fuera de servicio | 1 363 |

**`escalator=*` está desaconsejado**: [Key:escalator](https://wiki.openstreetmap.org/wiki/Key:escalator) lleva aviso de obsolescencia (*«The recommended replacement is: `conveying=*`»*), 125 usos.

Escaleras reversibles con horario (caso Pekín): `Key:conveying` documenta `reversible` pero no menciona `conveying:conditional`. La [página de discusión](https://wiki.openstreetmap.org/wiki/Talk:Proposed_features/Escalators_and_Moving_Walkways) tiene la sección «Escalators that change direction at set times» y remite a [Conditional restrictions](https://wiki.openstreetmap.org/wiki/Conditional_restrictions). Uso real: `conveying:conditional` 25 usos, 24 con el valor `forward @ (06:00-10:00); backward @ (10:00-24:00)`. Sugerencia: `conveying=reversible` como base y `conveying:conditional` cuando se conozca el horario; ningún router lo lee. `reversible` es una distinción que la encuesta captura o pierde en el momento de levantarla.

### 3.5 Modo 5 — Elevador

[Tag:highway=elevator](https://wiki.openstreetmap.org/wiki/Tag:highway%3Delevator): **57 357** usos, **49 154 nodos**. Tres formas documentadas: nodo (dominante); área (`highway=elevator` + `area=yes`, SIT recomienda además `indoor=room`); vía abierta, reservada a elevadores inclinados. **La conectividad se resuelve con la lista de niveles**: `level=-1;0;1;2` para no consecutivos, rango con guion para consecutivos (*«`level=-2-32`»*).

| Nuestro campo | OSM | Notas |
|---|---|---|
| `pathway_mode=5` | `highway=elevator` | Nodo (49 154) o área |
| niveles servidos | `level=-1;0;1` | |
| *(no lo modelamos)* | `wheelchair` — 17 531 elevadores lo llevan (31 %) | |
| *(no lo modelamos)* | `door:width` (1 361), `width`, `length`, `maxweight`, `capacity:persons` (70 904) | No usar `elevator:width` (46 usos) |
| *(no lo modelamos)* | `tactile_writing:braille:es` (158), `speech_output:es` (52) | §9 |
| — | `elevator=yes` (5 661) | Etiqueta distinta: indica que un *edificio* tiene elevador |

`ref:DELFI` = 0 usos, `ref:DB` = 35; no existe convención documentada para el `ref` del elevador. Ejemplo medido en Marienplatz, nodo 339957726: `highway=elevator, ref=MP05, description=Lift MP05, level=0;-1, operator=MVG, wheelchair=yes, indoor=yes, width=1.55, length=1.55, door:width=1, source=survey`.

Advertencia de rutabilidad: [Wheelchair routing](https://wiki.openstreetmap.org/wiki/Wheelchair_routing) documenta que el router evalúa *«tags belonging to line elements (ways) only»* y que las etiquetas sobre nodos, incluido `highway=elevator`, *«cannot yet be considered»*.

### 3.6 Modo 6 — Torniquete (fare gate)

| Candidato | Conteo | Veredicto |
|---|---|---|
| `barrier=turnstile` | **17 404** | de facto, la barrera física |
| `amenity=ticket_validator` | **14 709** | **[aprobado]**, la etiqueta tarifaria |
| `barrier=full-height_turnstile` | 4 064 | variante |
| `barrier=ticket_gate` | 24 | obsoleto por votación |
| `barrier=ticket_barrier` | 33 | obsoleto por votación |
| `barrier=fare_gate` | 0 | no existe |
| `public_transport=fare_gate` | 0 | no existe |

La [propuesta Ticket validator](https://wiki.openstreetmap.org/wiki/Proposal:Ticket_validator) (votada 2022-05-24, 31 a favor / 1 en contra) deprecó `ticket_barrier` y `ticket_gate` y prescribió **`barrier=turnstile` (o `barrier=gate`) + `amenity=ticket_validator`**. Propuesta para el Metro: `barrier=turnstile` + `amenity=ticket_validator` + `wheelchair=no`; la puerta ancha accesible como nodo aparte con `barrier=gate` + `amenity=ticket_validator` + `wheelchair=yes` (`wheelchair=no` ya aparece en 1 252 torniquetes del mundo). No hay página que documente cómo tratan los routers a los torniquetes; `foot=yes` es su compañero número uno (4 277).

### 3.7 Modo 7 — Puerta de salida

**No hay etiqueta dedicada.** `entrance=exit` (15 999) describe una **puerta** de un solo sentido (`door=hinged` 1 061 como compañero). `barrier=gate` (6 704 665) no documenta nada sobre un solo sentido. Sugerencia (composición de etiquetas documentadas, no un patrón documentado): `barrier=turnstile` o `barrier=gate` en el nodo + `oneway:foot=yes` en la vía, dibujada del lado pagado al lado libre.

### 3.8 Atributos del pathway

| Nuestro campo | OSM | Notas |
|---|---|---|
| `is_bidirectional` = 0 | **`oneway:foot=yes`** (clave 12 683; `=yes` 2 168) | **[wiki]** [Key:oneway:foot](https://wiki.openstreetmap.org/wiki/Key:oneway:foot): en calles `oneway=yes` es ambiguo. Práctica de facto en escaleras: `oneway=yes` a secas (sobre vías `conveying=forward`, `oneway=yes` 2 102 veces y `oneway:foot` 136). Emitir `oneway:foot=yes` y aceptar `oneway=yes` al leer |
| `is_bidirectional` = 1 | ausencia de `oneway*` | |
| `length` (metros horizontales) | **no etiquetar** | OSM deriva la longitud de la geometría; 3 coocurrencias de `length` con `conveying` en el planeta. En nuestra base está vacío |
| `traversal_time` (segundos) | `duration` — problema de formato | 46 523 usos, 40 544 en relaciones. Formato `hh:mm`; nuestros valores de 10–90 s redondean a `00:00`. No hay etiqueta bien soportada para tiempos sub-minuto. En nuestra base está vacío |
| `max_slope` (razón) | `incline=<n> %` | **[wiki]** porcentaje (`15 %`) o grados (`10°`). El wiki escribe `15 %` con espacio pero los datos dominantes van sin él (`10%` 20 124, `15%` 10 467): aceptar ambos. `yes` (8 075) y `steep` (4 776) están listados como errores |
| `stair_count` | ver §3.2 y §3.0 | |
| `pathway_description` | `description` | |
| *(GTFS tiene `signposted_as`, nosotros no)* | `destination` (976 183), `destination:ref` (487 642), relación `type=destination_sign` (178 902) | `signposted_as` tiene 0 usos en OSM. Ver §4.3 |
| `Pathway.validated` | *sin equivalente* | Estado de nuestro flujo |
| `Pathway.is_closed` | ver §5.2 | |
| `Pathway.code_identifiers` (JSON) | *sin equivalente* | Ver §7 |

## 4. Accesos

### 4.1 Correspondencia

| Nuestro campo/valor | OSM | Notas |
|---|---|---|
| `Stop` con `location_type=2` | **`railway=subway_entrance`** (53 535) | **[wiki]** aprobado, **sólo nodo**, sobre la vía peatonal que baja. No es el punto donde se valida el boleto |
| `has_entry=True`, `has_exit=True` | `entrance=yes` (2 992 920) | |
| `has_entry=True`, `has_exit=False` | **`entrance=entrance`** (2 403) | *«one-way in»* |
| `has_entry=False`, `has_exit=True` | **`entrance=exit`** (15 999) | *«one-way out»* |
| nombre de la salida («Andador Balderas») | `name` | **[wiki]** *«Name of the exit if is known. Not the name of the station»* |
| letra de la salida («A») | **`ref=A`**, no `name=Salida A` | **[wiki]** *«Some subway networks use numbers or codes to identify exits, e.g. '2' or 'B1'»* |
| `wheelchair_boarding` | `wheelchair` | §5.1 |
| `is_double` | sin equivalente en OSM: se generan dos nodos con el mismo `ref` | §4.4 |
| `is_closed` | §5.2 | |
| `miro_id` | §7 | |

**`ref` gana a `local_ref`.** Sobre nodos `railway=subway_entrance`: `ref` en 29 655 (55,4 %), `name` en 25 195 (47,1 %), `local_ref` fuera del top-30 de coocurrencias (< ~1,9 %). Tokio (1 552 accesos): `ref` 1 056 contra `local_ref` 14. Los valores de `ref` más comunes incluyen números y **letras** (`A` 2 672, `B` 2 531, `C` 2 049, `D` 1 779). [Key:local_ref](https://wiki.openstreetmap.org/wiki/Key:local_ref) tiene su alcance en andenes y posiciones de parada, no accesos.

Contracorriente viva: en [un hilo del foro de Viena de mayo de 2026](https://community.openstreetmap.org/t/ref-bei-railway-subway-entrance/143595) un mapeador borró masivamente los `ref` de accesos del U-Bahn porque contenían números de línea. La lección: **`ref` debe identificar la salida, jamás la línea**.

### 4.2 Direccionalidad: `entrance=*` y no `oneway`

En la [página de discusión de `railway=subway_entrance`](https://wiki.openstreetmap.org/wiki/Talk:Tag:railway%3Dsubway_entrance) (2013): *«oneway=yes on a way… doesn't allow to distinguish entrance from exit»*. `oneway` codifica dirección pero no rol. Recomendación: `entrance=entrance` / `entrance=exit` en el nodo, y opcionalmente `oneway:foot=yes` en la vía conectora. `entrance=exit` se usa 6,7 veces más que `entrance=entrance`.

### 4.3 Señalética direccional (`signposted_as`)

GTFS tiene `signposted_as` y `reversed_signposted_as` en `pathways.txt`; nuestro modelo no, y `StairReport` guarda prosa libre en `route_start`, `path_start`, `path_end`, `route_end`. En OSM: `destination=*` y la relación **`type=destination_sign`** (178 902, «in use»), roles `from`, `to`, `intersection`, `sign`. [Guidelines for pedestrian navigation](https://wiki.openstreetmap.org/wiki/Guidelines_for_pedestrian_navigation) la recomienda para accesos con nombres direccionales (ejemplo Boulainvilliers, París). Requiere relaciones.

### 4.4 `is_double`

No existe discusión sobre accesos gemelos en la página de `railway=subway_entrance`, ni propuesta de agrupación de accesos. [Relation:site](https://wiki.openstreetmap.org/wiki/Relation:site) no documenta agrupación de accesos. `stop_area` agrupa accesos con la estación, no entre sí. **Dos nodos compartiendo el mismo `ref` es la única señal expresable**; no viola [One feature, one OSM element](https://wiki.openstreetmap.org/wiki/One_feature,_one_OSM_element) porque las dos escaleras son dos rasgos físicos distintos. `is_double` es en nuestro lado una señal de generación: un stop → dos nodos OSM. Conteo en la base restaurada: 28 de 445 accesos con `is_double=True`.

## 5. Accesibilidad y estado

### 5.1 Accesibilidad

| Nuestro campo/valor | OSM | Notas |
|---|---|---|
| `wheelchair_boarding = 1` | `wheelchair=yes` (2 428 343) | |
| `wheelchair_boarding = 2` | `wheelchair=no` (1 005 640) | Escalón de entrada superior a 7 cm |
| `wheelchair_boarding = 0` | **omitir la etiqueta** | **Nunca `wheelchair=no`** |
| escalón ≤ 7 cm, áreas parciales | `wheelchair=limited` (487 814) | |
| `StairReport.is_accessible` | `wheelchair` en el objeto | |
| — | `wheelchair=designated` (20 632) | elevadores diseñados sólo para silla de ruedas |
| `StairReport.details` (prosa) | `wheelchair:description` (73 972) / `:es` (48) | |

**La trampa del `0`.** [Key:wheelchair](https://wiki.openstreetmap.org/wiki/Key:wheelchair): *«There is currently no default value for wheelchair access»*. [Limitations](https://wiki.openstreetmap.org/wiki/Limitations): *«there is no uniform way to express that a value exists but is unknown»*. Convertir GTFS `0` en `wheelchair=no` transforma «nadie ha revisado» en la afirmación de que una persona en silla de ruedas no puede entrar. La página GTFS del wiki no menciona `wheelchair_boarding`; la tabla es la lectura estándar de ambas especificaciones. Precedente: [Wheelmap](https://wiki.openstreetmap.org/wiki/Wheelmap) escribe a OSM hechos estables de accesibilidad vía la cuenta `wheelmap_visitor`.

### 5.2 Cierres y ciclo de vida (`is_closed`)

[Lifecycle prefix](https://wiki.openstreetmap.org/wiki/Lifecycle_prefix): `disused:` = *«Not currently in use, but could be reinstated easily»*; `abandoned:` = *«would require considerable effort to restore»*; `construction:`, `demolished:`, `razed:`, `proposed:`, `was:`. Conteos: `disused:highway` 58 414, `construction:highway` 3 523, `disused:highway=elevator` = 96 en todo el mundo. `disused:highway=elevator` borra el objeto para todo consumidor; `highway=elevator` + `access=no` mantiene el objeto y afirma permiso, no mecánica. Ninguna sirve para «está descompuesto esta semana». Nuestro `is_closed` (clausurado: x en Miro o gris claro) sí encaja con `disused:` si es clausura de verdad. Clausura ≠ avería.

### 5.3 El estado de operación: `is_working` y `status_maintenance`

**`operational_status` existe, es popular y está explícitamente desaconsejado.** [Key:operational_status](https://wiki.openstreetmap.org/wiki/Key:operational_status), 202 147 usos: *«Observation of the current functional status of a mapped feature - now discouraged»*, porque *«Expecting that all data consumers will check and exclude `operational_status=[broken]` … is not reasonable»*. Una etiqueta de estado es invisible para todo consumidor que no sepa buscarla: la escalera rota sigue ruteando como funcional. Valores reales: `operational` 149 462, `open` 24 610, `ok` 5 869, `functional` 2 264, `yes` 2 051, `active` 697.

Para «escalera descompuesta» la gente usa: nada. `service:status` = 0. `broken` = 25. `out_of_order` = 2. La página de `highway=elevator` no contiene etiquetado para elevador fuera de servicio. La [propuesta Lifts](https://wiki.openstreetmap.org/wiki/Proposal:Lifts) está inactiva desde 2024.

Citas que sostienen la decisión: [Good practice](https://wiki.openstreetmap.org/wiki/Good_practice): *«Don't map temporary events and temporary features — Our map data is often downloaded and used offline on various devices for several weeks or months.»* [Verifiability](https://wiki.openstreetmap.org/wiki/Verifiability): *«A tag/value combination and geometry is verifiable if and only if independent users observing the same feature would make the same observation every time.»* [Limitations](https://wiki.openstreetmap.org/wiki/Limitations): *«Not everything is mappable in OSM […] Certain useful but quickly changing data like live traffic info is out of scope of OSM».* Toda la familia `temporary:` está muerta: [Proposal:Temporary](https://wiki.openstreetmap.org/wiki/Proposal:Temporary) «Obsoleted»; [Temporary (conditional)](https://wiki.openstreetmap.org/wiki/Proposal:Temporary_(conditional)) «Draft» desde 2016; [Key:temporary](https://wiki.openstreetmap.org/wiki/Key:temporary) (11 493) *«mapping temporary features is strongly discouraged»*; `end_date` *«discouraged»*.

### 5.4 La línea, aplicada a nuestro modelo

| Legítimo subir (físico, verificable, estable) | Ilegítimo / desaconsejado (volátil) |
|---|---|
| que el acceso existe, en estas coordenadas | `StairReport.is_working` |
| su `ref` es «A», su `name` es «Andador Balderas» | `StairReport.status_maintenance` (full/medium/minor/other) |
| que es sólo de salida (`entrance=exit`) | `StairReport.other_status_maintenance` |
| que existe una escalera eléctrica, con `conveying=*` y `step_count=N` | cuántas de N escaleras están corriendo hoy |
| que tiene pasamanos (`handrail=yes`) | |
| `tactile_paving=yes/incorrect/partial` | |
| `wheelchair=yes/limited/no` con el criterio de 7 cm | |
| cuándo un ciudadano lo verificó por última vez | |

La prueba: *¿un encuestador independiente que llegue el mes que viene registraría el mismo valor?* Matiz sobre `direction_observed` (`up`/`down`): si la escalera eléctrica tiene sentido fijo, la dirección observada va a `conveying=forward|backward`; si es reversible, el hecho es `conveying=reversible`. El formulario tendría que distinguir «así está ahora» de «así está siempre».

### 5.5 Las fechas

| Nuestro campo | OSM | Notas |
|---|---|---|
| `StairReport.date_reported` / `date_received` | **`survey:date=YYYY-MM-DD`** (2 226 762) | **[wiki]** *«Date of last time the feature was surveyed»*; implica verificación presencial. Ojo: hoy ambos campos usan `auto_now=True` y se reescriben en cada `save()` ([[task-12]]) |
| verificación de un atributo concreto | `check_date` (3 474 901) y `check_date:<clave>` | |
| verificación de accesibilidad | **`check_date:wheelchair`** (7 468) | |

Formato ISO 8601 `YYYY-MM-DD`; `2024-11-7` (sin ceros) tiene 13 298 usos y los validadores lo marcan. Evitar `survey_date`, `last_checked`, `lastcheck`, `updated`.

### 5.6 `EvidenceImage`

[Key:image](https://wiki.openstreetmap.org/wiki/Key:image) (425 395): de facto con propuestas rechazadas; sólo una imagen por rasgo, spam, licencias poco claras, enlaces rotos, privacidad. Alternativas recomendadas por el wiki: `wikimedia_commons` (394 863), `mapillary` (457 307), `panoramax` (127 871). Nuestras fotos son prueba de un reporte fechado: su lugar es nuestra base.

### 5.7 La arquitectura que se deriva, y sus precedentes

La división GTFS/OSM es el precedente establecido: geografía estable en OSM, horarios volátiles fuera, unidos por un identificador estable. [Limitations](https://wiki.openstreetmap.org/wiki/Limitations) § *No persistent IDs*: *«OpenStreetMap doesn't have IDs that are guaranteed to be permanent.»* No llavear nuestra base con IDs de nodo de OSM: mantener nuestro ID estable, guardar el OSM ID como enlace blando ([[task-17]]) y tener re-emparejamiento por `ref` + estación + geometría. Precedentes de estado en vivo fuera de OSM: Deutsche Bahn FaSta, BrokenLifts (VBB, 2011), Elescore, y [`db-elevators`](https://github.com/juliuste/db-elevators), cuyas asociaciones con OSM viven en un ndjson fuera de OSM.

## 6. Andenes

### 6.1 Correspondencia y geometría

| Concepto | OSM | Notas |
|---|---|---|
| Andén (`location_type=0`) | `railway=platform` (194 996) **+** `public_transport=platform` (4 149 487) | 183 377 objetos llevan ambas (94 % de los `railway=platform`). Metro Mapping las lista como obligatorias las dos |
| como área | **preferido** | `railway=platform` **[wiki]**: *«Draw an area around the perimeter of the platform. This is the preferred, more detailed method»* |
| `area=yes` | requerido por `railway=platform`, no por `public_transport=platform` | Práctica: poner las tres |
| Borde de andén | `railway=platform_edge` (14 119; 14 114 vías) | *«Such ways must share nodes with the platform outline»* |
| Andén central vs lateral | **sin etiqueta** | §6.2 |
| `layer=-N` | obligatorio en Metro Mapping para andenes subterráneos | §2.2 |

### 6.2 Central vs lateral

`Key:platform:type` no existe como página; `platform:type=island` 37 usos, `side` 3. OSM captura la distinción estructuralmente: un andén central es un área `railway=platform` con dos vías `railway=platform_edge` (cada una con su `ref`); uno lateral tiene una. El tipo es derivable del conteo de bordes, nunca declarado.

### 6.3 Conectar escaleras al polígono del andén

[Guidelines for pedestrian navigation](https://wiki.openstreetmap.org/wiki/Guidelines_for_pedestrian_navigation): *«Routing through areas only is hardly possible… junctions between lines and areas are essential.»* *«The connection between a way and an area is a node shared between the two objects.»* *«areas with the key `area:highway`… are not meant to be used for routing.»* Soporte de ruteo sobre áreas ([Key:area#Routers](https://wiki.openstreetmap.org/wiki/Key:area#Routers)): *«Most routers naïvely route around the perimeter»*; AccessMap, OpenTripPlanner y MOTIS calculan grafos de visibilidad; OSRM trabaja en ello desde septiembre de 2025. *«Do not alter your mapping to accommodate such routers.»* Recomendación operativa: andén como polígono **y** líneas `highway=footway` separadas que lo crucen compartiendo nodos con el contorno y con cada `highway=steps` / `highway=elevator`; nunca añadir `highway=footway` al objeto andén (*«May break some GPS routers»*).

### 6.4 Práctica Múnich

Marienplatz está en [Indoor Mapping#Examples](https://wiki.openstreetmap.org/wiki/Indoor_Mapping#Examples); Odeonsplatz no. Páginas de MENTZ GmbH: [Modellierungsvorschläge Indoor](https://wiki.openstreetmap.org/wiki/MENTZ_GmbH/Modellierungsvorschläge_Indoor) (pasillos `highway=footway` + `level` + `indoor=yes`; vestíbulos `highway=pedestrian` + `indoor=corridor` + `area=yes`; escalones con `incline` y `level` en ambos extremos) y [Beispiele von Bauwerken](https://wiki.openstreetmap.org/wiki/MENTZ_GmbH/Beispiele_von_Bauwerken) (registro estación por estación con estatus).

Marienplatz medido (246 elementos con `indoor=*`): `indoor=yes` 197, `room` 35, `no` 6, `corridor` 5, `wall` 1; `level` en 220 (89 %); `highway=steps` 61, 40 con `conveying` (`forward` 28, `reversible` 5, `backward` 4, `yes` 3); `highway=elevator` 6, todos nodos; `layer` 176, `tunnel` 155, `wheelchair` 54, `incline` 46, `tactile_paving` 38, `check_date` 36. Odeonsplatz: 86 elementos, tres niveles subterráneos, 9 de 12 vías de escalones con `conveying`.

Hallazgo incómodo: 197 de 246 elementos de Marienplatz son `indoor=yes`, que no es un valor de SIT y que [indoorequal](https://wiki.openstreetmap.org/wiki/Indoor%3D), el visor recomendado, no renderiza (*«Only Simple Indoor Tagging is supported»*). [[adr-0004]] elige SIT puro.

## 7. Identificadores para el viaje de ida y vuelta

### 7.1 La familia `gtfs:*`

La página [GTFS](https://wiki.openstreetmap.org/wiki/GTFS) es la página-rasgo de la propuesta [GTFS Tagging Standard](https://wiki.openstreetmap.org/wiki/Proposal:GTFS_Tagging_Standard), **aprobada**. Forma aprobada: sufijo de código de feed: *«Add the feed code as a suffix the keys… Start the feed code with the ISO 3166-2 region code… Do not include colons (:) in the feed code»*. `gtfs:feed` desnudo está desaconsejado; también obsoletas `gtfs:name`, `gtfs:id`, `gtfs:short_name:*`, `gtfs:long_name:*`. Recomienda *«use both standard tags and GTFS tags, even if they are exactly the same»*.

| Clave | Conteo |
|---|---|
| `gtfs:stop_id` (desnuda) | 162 785 |
| `gtfs:feed` (obsoleta) | 59 141 |
| `gtfs:route_id` | 43 028 |
| `gtfs:stop_code` | 42 832 |
| `gtfs:location_type` | 4 491 |
| `ref:gtfs` | 87 |
| **`gtfs:pathway_id`** | **0** |
| **`gtfs:pathway_mode`** | **0** |
| **`gtfs:level_id`** | **0** |
| `gtfs:stop_id:IL-MOT` (sufijado) | 30 931 |
| `gtfs:stop_id:FR-SNCF` | 3 972 |

Para nosotros sería `gtfs:stop_id:MX-CMX-<feed>` (ISO 3166-2 de la Ciudad de México: `MX-CMX`). **`gtfs:pathway_id` y `gtfs:level_id` tienen cero usos en el mundo**: si los ponemos, seríamos los primeros — «inventar y documentar». México usa el namespace heredado `gtfs_*` (6 979 usos de `gtfs_id`) y `gtfs:*` tiene 0 usos en México ([taginfo México](https://taginfo.geofabrik.de/north-america:mexico/)); [[adr-0004]] elige `gtfs:*`.

### 7.2 Espacios de nombres `ref:*`

[Key:ref](https://wiki.openstreetmap.org/wiki/Key:ref) documenta `ref:<operador>` (`ref:De_Lijn`), `ref:<país>:<esquema>` (`ref:GB:uprn`), `ref:<base_de_datos>` (`ref:nrhp`). `ref:STC` tiene 0 usos: acuñación legítima pero no atestiguada. [Any tags you like](https://wiki.openstreetmap.org/wiki/Any_tags_you_like): *«please document them here on the OpenStreetMap wiki»*. [Namespace](https://wiki.openstreetmap.org/wiki/Namespace): *«just namespace a key to avoid clashing with other data instead of trying to integrate existing schemes, this is bad habit.»*

### 7.3 `miro_id`, `pathway_id`, `code_identifiers`: el caso `bandatos:*`

Claves de ID externo masivas (`tiger:cfcc` 12 359 412, `ref:bag` 11 458 647, `ref:GB:uprn` 6 764 092, `ref:IFOPT` 328 362) son identificadores de registros públicos de autoridades externas, no llaves primarias del proyecto que mapea. Import Guidelines: *«Your import shall use tags which are familiar to the OSM community, rather than inventing tags.»* Un `miro_id` no es verificable por ningún otro mapeador.

| Nuestro campo | Recomendación |
|---|---|
| `Stop.stop_id`, `Level.level_id`, `Pathway.pathway_id` | Nuestra base; si se publica un feed GTFS documentado, `gtfs:stop_id:MX-CMX-<feed>` |
| `Stop.miro_id`, `Pathway.miro_id`, `Station.miro_frame_id` | Nuestra base, nunca OSM |
| `code_identifiers` (JSON) | Nuestra base; los códigos de señalética STC verificables en campo sí como `ref` |
| `Stair.number` | `ref` si está señalizado |
| `Stair.original_direction`, `original_location` | `destination` / `destination_sign` si es señalética |
| ID de OSM (viaje de vuelta) | Columna nueva como enlace blando ([[task-17]]) |
| `Stair.route_blur`, `Stair.validated`, `Pathway.validated` | Estado de nuestro flujo |

## 8. Etiqueta de importación y edición organizada

### 8.1 ¿Es esto una importación?

[Import](https://wiki.openstreetmap.org/wiki/Import): *«the process of uploading external data to OSM»*. [Automated edits](https://wiki.openstreetmap.org/wiki/Automated_edits) se definen como cambios *«with no or very limited human oversight»*; un flujo donde una persona coloca y verifica cada objeto en JOSM no es edición automatizada. Las Import Guidelines no contienen umbral numérico; [Import/Catalogue](https://wiki.openstreetmap.org/wiki/Import/Catalogue) habla de *«more than a few hundred nodes»* para catalogar. [Armchair mapping](https://wiki.openstreetmap.org/wiki/Armchair_mapping) llama al mapeo por levantamiento *«the heart and soul of OpenStreetMap»*: nuestros datos son levantamiento propio. Aun así, el volumen (~195 estaciones, ~450 accesos) va a parecer importación, y la duplicación por plantilla introduce geometría no observada. Lo barato es escribir la página y publicar en el foro → [[task-11]].

### 8.2 Organised Editing Guidelines

[Organised Editing Guidelines](https://wiki.openstreetmap.org/wiki/Organised_Editing_Guidelines), aprobadas por la OSMF el 2018-11-15, aplican a grupos de voluntarios: página wiki del grupo, lista de cuentas, contacto, etiquetado de changesets. DWG: *«will intervene for edits the community has issues with, and will not intervene for merely not following the guidelines.»*

### 8.3 Pasos obligatorios de una importación

De [Import/Guidelines](https://wiki.openstreetmap.org/wiki/Import/Guidelines): licencia compatible con ODbL; plan en el wiki (*«You must write a plan for your import in the OSM wiki»*, esqueleto en [Import/Plan Outline](https://wiki.openstreetmap.org/wiki/Import/Plan_Outline)); aval local (*«You must not import the data without local buy-in»*); **el canal ya no es la lista de correo**: *«You must submit a new post to the Community Forum»* con etiquetas `import` e `import-proposal` ([Imports Mailing List Migration](https://wiki.openstreetmap.org/wiki/Proposal:Imports_Mailing_List_Migration)); la [versión en español](https://wiki.openstreetmap.org/wiki/ES:Import/Guidelines) está desactualizada; espera de 14 días; cuenta `<username>_Import`; alcance cerrado; conflación obligatoria; capacidad de reversión. En [Import/Catalogue](https://wiki.openstreetmap.org/wiki/Import/Catalogue) hay una importación mexicana colindante: SIGCDMX Mexico City, en curso desde 2025-08.

### 8.4 `source` y etiquetas de changeset

[Key:source](https://wiki.openstreetmap.org/wiki/Key:source): *«the `source=*` tag should typically be added… to the changeset»*. Para nosotros: `source` en el changeset, `survey:date` en el elemento. Etiquetas documentadas de [Changeset](https://wiki.openstreetmap.org/wiki/Changeset): `comment`, `created_by`, `imagery_used`, `source`, `bot`, `review_requested`, `hashtags`. `import=yes` no está documentado; la convención real es una bandera por proyecto (`seattleimport=yes`).

### 8.5 Herramienta

Plugin [indoorhelper](https://wiki.openstreetmap.org/wiki/JOSM/Plugins/indoorhelper) de JOSM: validación SIT y botón «Insert level».

## 9. Lo que OSM modela y nuestro esquema no

| Etiqueta | Conteo | Una línea |
|---|---|---|
| `tactile_paving` | 6 254 747 | Guía podotáctil. `yes`/`no`/`contrasted`/`incorrect`/`partial`. En escalones: *«Mark top and bottom; use 'partial' if only at top»*; en elevadores: *«ON EACH LEVEL»*. El de mayor valor |
| `lit` | 15 284 063 | Iluminación |
| `surface` | 80 565 189 | Material del piso |
| `width` | 3 882 141 | Ancho; lo consumen los routers |
| `kerb` | 3 062 539 | Guarnición en la transición a la calle |
| `handrail` | 716 835 | Pasamanos |
| `step_count` | 522 862 | Ya lo tenemos como `stair_count` |
| `door` | 473 514 | `door=no` es significativo en accesos de metro |
| `smoothness` | 6 967 158 | Con cuidado: Verifiability lo cita como caso de mala verificabilidad |
| `automatic_door` | 14 727 | |
| `entrance:width` / `door:width` | 7 332 / 1 361 | |
| `amenity=bicycle_parking` | 930 021 | |
| `bench` | 1 876 723 | |
| `amenity=toilets` | 518 916 | Con `toilets:wheelchair`, `changing_table`, `fee` |
| `amenity=drinking_water` | 365 471 | |
| `emergency=defibrillator` | 173 038 | |
| `information=map` | 144 111 | `information=tactile_map` para táctiles |
| `vending=public_transport_tickets` | 34 096 | |
| `payment:cash` | 456 496 | Para Movilidad Integrada haría falta documentar un valor local |
| `tactile_writing:braille:es` | 158 | Más usada que la clave genérica (411) |
| `speech_output:es` | 52 | |
| `security` | 736 | Saltárselo |

## Observaciones del investigador

Juicio del ejecutor Opus, no hallazgo documentado.

- Las alineaciones limpias son la mayoría del modelo: `level_index`→`level`+`level:ref`, los siete modos, `wheelchair_boarding`→`wheelchair`, `has_entry`/`has_exit`→`entrance=*`, andén→`railway=platform`+`public_transport=platform`+`area=yes`, fechas→`survey:date`. La ausencia de una tabla oficial es un vacío de documentación, no de compatibilidad.
- Lo que no tiene destino: `traversal_time` (`duration` en `hh:mm` redondea a cero), `length` (OSM la deriva) e `is_double` (se resuelve generando dos nodos). Ninguno de los dos primeros está poblado en nuestra base.
- OSM no tiene —y decidió no tener— etiqueta para «está descompuesto». `is_working` + `status_maintenance` se quedan en nuestra base; la arquitectura resultante es la de DB FaSta, BrokenLifts y `db-elevators`.
- `bandatos:*` es la forma que el wiki desaconseja; la salida limpia es `ref` para lo señalizado y el OSM ID como enlace blando de nuestro lado.
- `wheelchair_boarding=0` es la trampa silenciosa más peligrosa del conversor.
- La dirección de la vía es la segunda trampa: `incline`, `conveying` y `oneway:foot` relativos al orden de nodos.
- El estado real del Metro en OSM (sin `ref`, sin `check_date`, siete líneas sin `route_master`, 58 stop_areas vivas) es un hueco enorme y bien definido, con comunidad activa.
- Dos tensiones que no cierra el investigador: usar o no `stop_area` (resuelto en [[adr-0004]]: sumar a las existentes) y SIT puro vs `indoor=yes` a la Múnich (resuelto en [[adr-0004]]: SIT puro).
