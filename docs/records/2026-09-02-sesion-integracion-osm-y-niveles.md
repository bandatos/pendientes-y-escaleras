---
type: record
id: 2026-09-02-sesion-integracion-osm-y-niveles
title: "Sesión del 2 de septiembre (tarde): integración del .osm con OSM, senda del andén, áreas de estación, task-17 y corrección del parser de niveles"
date: 2026-09-02
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
---

# Sesión del 2 de septiembre de 2026 (tarde): integración del .osm con OSM, senda del andén, áreas de estación, task-17 y corrección del parser de niveles

Segunda sesión del día, en modo duo (coordinador Fable 5.1, ejecutores Opus 5), sobre la rama `first-stations-josm`. Bitácora `session_01Hpdsm3RR7obQnGYi72cSa2`. Continúa el trabajo de [[2026-09-02-sesion-primeras-dos-estaciones-josm]]: Ricardo revisaba en JOSM los .osm de Portales y San Pedro de los Pinos y pidió que se integraran con lo ya mapeado en OSM, que el área de la estación entrara al archivo, que la línea de circulación del andén fuera de punta a punta y tocara el polígono, y una auditoría de etiquetas.

## Diagnóstico de arranque

Tres ejecutores en paralelo (contexto del repo, auditoría de etiquetas contra la wiki de OSM, relevamiento Overpass a 50 y 80 m de cada estación). Hallazgos que cambiaron el rumbo: los accesos emitidos eran duplicados geométricos a 2–7 cm de los nodos `railway=subway_entrance` existentes (tres de cuatro; el oriente de San Pedro no existe en OSM); los tres nodos existentes están aislados, sin compartir nodo con ninguna calle ni banqueta; en ninguna de las dos estaciones hay nada indoor ni con `level` en OSM; las rutas de L2 y L7 usan el nodo de estación con rol `stop`, así que agregar andenes no exige editar rutas; Portales tiene contorno de edificio (`building=train_station`, 21 vértices) que es la misma figura del KML desplazada 6 m (73 % de superposición); San Pedro tiene dos relaciones `stop_area` de nombre casi igual (Metro y trolebús). La auditoría de etiquetas dio «ok» a andén, escaleras, eléctricas, accesos y torniquetes, y abrió las elecciones que Ricardo resolvió en [[adr-0011]].

## Decisiones de Ricardo

- Camino C de integración: el archivo embebe solo aquello a lo que lo nuestro debe pegarse (accesos enlazados, banquetas cercanas, contorno de estación); el resto lo baja JOSM. Registrado en [[adr-0011]], que enmienda [[adr-0010]] y [[adr-0005]].
- Los nodos de acceso existentes se adoptan y se modifican (etiquetas y posición), contra la regla de [[adr-0010]] de no tocar objetos existentes hasta [[task-11]].
- El polígono del KML es dato a subir, no referencia visual: enmienda de [[adr-0005]]. Portales lleva esta vez ambas áreas, la del KML y el contorno de OSM, para que Ricardo elija en JOSM.
- Senda del andén: de punta a punta, extremos insertados como vértices de los lados cortos del andén (polígono de 4 a 6 nodos); San Pedro conserva su corrimiento de 1,5 m hacia la vía. El nombre «Senda peatonal» es solo el rótulo de JOSM para `highway=footway`; las etiquetas se quedan.
- Accesos de San Pedro: edificio de 12 m con tres puertas juntas en un lado y las dos escaleras arrancando del lado opuesto; explanada `highway=pedestrian` + `area=yes` cuyo borde llega a la banqueta; tramos rectos del acceso a cada banqueta de la esquina.
- Etiquetas: el nombre del acceso pasa a `description`; se retira `level:ref`; `wheelchair=no` en toda `highway=steps`; `destination` en andenes laterales se conserva; `wheelchair` desde `wheelchair_boarding` no se emite hasta que sea dato medido; `tunnel=yes` no aplica a pasillos interiores (mapeo indoor con `level`); un `level_index` no entero detiene la exportación nombrando el stop.
- Sentido de las eléctricas: [[adr-0012]]; resuelve [[fb-2]] y el inciso (a) de [[task-24]].
- task-17 confirmada y ejecutada: `osm_type`/`osm_id` en `Stop` y `Pathway`, CSV `data/osm/osm-links.csv` y command `link_osm_ids`; `import_stops` lo llama al final.
- Mixcoac y Chabacano: sus mezzanines intermedios no reciben nivel propio.
- Xola y San Joaquín siguen fuera; TESTING.md ofrecido y declinado por ahora; sin tests.

## Lo hecho en código y datos

- `api/utils/osm/`: nuevos `overpass.py` (consulta y caché versionado en `data/osm/context/`), `kml.py` (polígono de estación) y `diff.py`; objetos ajenos con id positivo y `version` en `document.py`; validador que los exime; senda soldada al andén; edificios, puertas y explanadas; tramos a banquetas terminando en vértices existentes; command `diff_station_osm` para leer la edición de Ricardo en metros locales de la plantilla. Ambos .osm regenerados y validados sin errores; README de `data/osm/` actualizado.
- Parser de niveles de Miró (`api/utils/miro/parsers.py`, `level_mixin.py`): «Nivel Andenes superficie 0» no se leía porque «Andenes» y «superficie» eran alternativas excluyentes, así que El Rosario, Universidad y Constitución de 1917 no tenían nivel 0 y sus stops caían al +1; «L12 Nivel -3 Andenes» (Ermita) perdía la marca de andenes. Corregido; de 96 textos del tablero cambian exactamente esos cinco.
- Base local `escaleras-local`: reimportadas sin `--reset` El Rosario, Universidad, Constitución de 1917, Ermita, Morelos y Jamaica (las dos últimas con la flecha de nivel corregida por Ricardo en Miró). Escaleras con ambos extremos al mismo nivel: de 132 a 64 filas ([[task-31]], CSV en `data/analysis/escaleras-mismo-nivel.csv`).
- Cuatro eléctricas al mismo nivel (Mixcoac 1, Chabacano 3), todas vestíbulo ↔ mezzanine.
- Regla de pares en L7, corrida una vez: 86 pares de nodos con eléctricas; 38 con bidireccional + sube; 36 solitarias balanceadas en Aquiles Serdán, Camarones y Refinería (Ricardo: están bien, no son bidireccionales, la de subida y la de bajada llegan a descansos distintos); 7 solitarias que solo suben sin gemela ([[task-34]]).

## Pendientes que dejó la sesión

San Pedro: lado de las puertas de cada edificio (el poniente quedó al sur por falta de banqueta en OSM), cuál puerta está clausurada, podar tramos sobrantes; Portales: elegir área; Candelaria: conector de Miró que va de «L4 Vestíbulo principal» a sí mismo; Consulado: «Pasillo superior dir. Santa Anita NTE» ↔ andén en +2. Todo en [[task-26]] y [[task-31]]. Filas de `Level` huérfanas: [[task-33]]. Respaldo de pathways e ids de producción en Miró: [[task-32]]. `import_stops` no se corrió (borra todas las paradas). La auditoría de ADR que Ricardo aprobó para el final de la sesión se lanzó después de este cierre y no antes, contra la secuencia que él fijó; sus resultados están en la sección siguiente.

## Cierre: crítico y auditoría de ADR

El crítico corrió junto con la auditoría de ADR, ambos de solo lectura, antes del commit. Lo que corrigió sin preguntar: la «banqueta sin nombre» de Portales resultó ser el puente peatonal que OSM ya tiene (way 43763067, `bridge=yes`, `layer=2`); el validador vuelve a comparar nuestros nodos contra los existentes de OSM y ningún nodo nuestro queda a menos de 0,3 m de uno ajeno (el nodo de la explanada que caía a 2 cm de un vértice de banqueta se reemplazó por el vértice); la plantilla de Tlalpan regresó a un área de estación por defecto y Portales conserva las dos solo por `--station-area both` en la línea de comando; el código muerto de la regla de pares salió de `api/utils/miro/pathway_mixin.py`; el CSV de escaleras al mismo nivel se regenera con el command `same_level_pathways`; el respaldo de tramos a calles con `sidewalk=*` se eliminó. Un primer intento de excluir puentes y túneles como candidatos de conexión se revirtió por instrucción de Ricardo: muchos accesos del Metro no están a nivel de calle; lo de Portales lo resuelve él en la próxima sesión.

Ya de noche, Ricardo enmendó el alcance del contexto embebido de [[adr-0011]]: además de lo conectable, el archivo lleva congeladas —id y versión reales, sin tocar, sin conectar, nunca destino de tramos— las calles (`highway` de `motorway` a `service` con sus `_link`), las vías urbanas (`railway=subway|light_rail|tram`) y el transporte público (`public_transport=*`, `highway=bus_stop`, `railway=tram_stop`, `amenity=bus_station`) a 50 m de cualquier nodo nuestro, con la consulta a Overpass todavía a 150 m y los tramos de conexión reservados a las vías peatonales; el motivo es que el mapeador vea la estación dentro de su manzana en JOSM y no flotando. Portales quedó con 12 calles (Calzada de Tlalpan, Calzada Santa Cruz, Avenida Víctor Hugo, Calle Albert, Calle Hamburgo) y las vías de la Línea 2; San Pedro de los Pinos con 12 calles (Avenida Revolución, Avenida 1, Avenida 1º de Mayo, Calles 2, 4, 7, 9 y 13), la vía de la Línea 7 y la plataforma del Trolebús Elevado.

Decisiones de Ricardo en el cierre: los tramos vestibulares de Portales que duplican el puente de OSM se quedan como están y el puente no entra al archivo; `wheelchair=no` se mantiene en fijas y eléctricas, tras saber que la regla se había ampliado más allá de lo que aprobó; y la reparación de los ADR va por un ADR de catálogo vigente.

Auditoría de ADR: siete se mantienen (0001, 0003, 0006, 0007, 0008, 0009, más 0011 y 0012 de hoy); [[adr-0002]] y [[adr-0005]] reciben nota de enmienda (espejo de Overpass y conflación; el KML como dato a subir, con el rumbo desde `shapes.txt` vigente y sin implementar); [[adr-0004]] y [[adr-0010]] quedan reemplazados por [[adr-0013]], que acarrea sus reglas vivas y deja explícita la pregunta de las `stop_area`, diferida a [[task-11]]. El linaje formal es 0004 → 0010 → 0013 porque el esquema admite un solo `supersedes` por decisión.

Otros cierres: [[task-17]] con sus dos primeros criterios cumplidos y el tercero anotado en [[task-11]]; [[task-26]] con las seis puertas contra las tres salidas relevadas y el puente de Portales. Respaldo de la base local tomado después de las reimportaciones, en `~/databases/escaleras-local-2026-09-02-post-reimport.sql`; Ricardo había pedido el respaldo antes y las importaciones corrieron sin él, aunque son idempotentes y sin `--reset`.

## Feedback capturado

Nueve nodos globales en `~/.claude/system/feedback/`, todos pendientes de curaduría: los subagentes deben listar lo que necesita el llamado de Ricardo; no escribirle mientras corre un agente lanzado en el mismo turno; el consolidado lleva solo lo nuevo; documenter debe admitir otros owners (Pablo); las listas de archivos de un plan se explican por lo que le dan; esfuerzo de razonamiento medio, no alto; la auditoría de ADR corrió después del cierre documental contra la secuencia fijada; el brief del fork de cierre prohibió editar bajo `~/.claude` cuando los nodos de feedback global viven ahí; no excluir puentes ni túneles al buscar vías peatonales cerca de un acceso del Metro.
