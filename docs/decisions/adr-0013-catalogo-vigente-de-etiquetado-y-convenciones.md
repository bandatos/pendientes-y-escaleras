---
type: decision
id: adr-0013
title: "Catálogo vigente de etiquetado y convenciones del generador de .osm: consolida adr-0004 y adr-0010 con lo decidido en adr-0011 y adr-0012"
state: accepted
date: 2026-09-02
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
supersedes: "[[adr-0010]]"
affects: ["api/utils/osm/tags.py", "api/utils/osm/builder.py", "api/utils/osm/validate.py", "api/utils/osm/template.py", "api/utils/osm/document.py", "data/osm/templates/"]
related: ["[[adr-0011]]", "[[adr-0012]]", "[[adr-0004]]", "[[adr-0006]]", "[[task-11]]", "[[task-13]]", "[[task-18]]", "[[task-19]]", "[[task-27]]"]
---

# Catálogo vigente de etiquetado y convenciones del generador de .osm: consolida adr-0004 y adr-0010 con lo decidido en adr-0011 y adr-0012

## Contexto y planteamiento del problema

La auditoría de decisiones del cierre de [[2026-09-02-sesion-integracion-osm-y-niveles]] encontró que [[adr-0004]] y [[adr-0010]] eran los dos ADR más contradichos del repo: cinco reglas del primero y seis del segundo ya no describen lo que el generador hace, y ambos anuncian en el título o en el cuerpo reglas revertidas («Simple Indoor Tagging puro», «`level:ref` siempre», «eléctricas siempre `conveying=forward`» junto a «bidireccional = `conveying=reversible`» en la misma viñeta). Las enmiendas se habían ido acumulando por texto en [[adr-0011]] y [[adr-0012]] sin que los ADR viejos dejaran de estar vigentes, así que quien abría el más general leía la regla al revés. Ricardo eligió consolidar: un ADR nuevo que reemplace a los dos, acarree sus reglas vivas y deje explícito lo que sigue abierto.

## Criterios de decisión

- Un solo lugar donde leer el catálogo de etiquetas y convenciones que el generador aplica hoy, verificable contra `api/utils/osm/tags.py`.
- No perder ninguna regla que siga viva en los ADR reemplazados, aunque todavía no esté implementada.
- Dejar nombradas, no escondidas, las preguntas que los ADR viejos dejaron sin contestar.

## Opciones consideradas

- **Notas de enmienda en cada ADR viejo** — barato, pero los títulos seguirían anunciando reglas falsas y el lector tendría que reconstruir el catálogo a partir de cuatro documentos.
- **Reemplazar adr-0010 por adr-0011 y adr-0012 sin ADR nuevo** — obliga a reabrir adr-0011 para acarrear las reglas de adr-0010 que no cubre (niveles con punto y coma, `oneway:foot`, emparejamiento por sufijo, torniquetes, traza).
- **ADR de catálogo vigente que reemplace a adr-0004 y adr-0010** — lo elegido.

## Resultado

Este ADR reemplaza a [[adr-0010]], que a su vez queda como reemplazo formal de [[adr-0004]] (el esquema del documenter admite un solo `supersedes` por decisión, así que el linaje es 0004 → 0010 → 0013). Rige junto con [[adr-0011]] (integración con objetos existentes) y [[adr-0012]] (sentido de las eléctricas), que no se tocan. Lo que sigue es el catálogo completo; donde una regla viene de otro ADR se cita.

### Archivo

- Lo nuestro sale con ids negativos únicos y cabecera `upload='never'`; los objetos existentes de OSM entran con su id positivo, `version` y metadatos según [[adr-0011]].
- Etiquetas de traza `note:stop_id`, `note:pathway_id` y `note:miro_id` para la revisión local, retiradas con `--no-trace` antes de cualquier subida.
- Sin nodo de estación ni relación `stop_area` nuevos: ambos existen ya en OSM para las estaciones trabajadas.

### Niveles

- `level` entero consecutivo por apilamiento físico. Un `level_index` no entero detiene la exportación nombrando el stop; nunca se redondea. La renumeración de los fraccionarios es de [[task-13]].
- Niveles múltiples con punto y coma ascendente, `level=-2;-1`; nunca rango con guion.
- Sin `level:ref`: el rótulo de la señalética es del nivel, no del elemento, y el mecanismo del mapeo indoor para nombrar un nivel es un polígono `indoor=level`, que no se dibuja.
- `layer=<level>` y `location=underground` en andenes subterráneos, según Metro Mapping; nunca `tunnel=yes` en pasillos interiores, que van con mapeo indoor y `level`.

### Circulación

- Pasillos y vestíbulos como líneas `highway=footway` + `indoor=yes` + `level`; nunca `highway=corridor`, que OSRM y GraphHopper ignoran.
- Andén: polígono `railway=platform` + `public_transport=platform` + `area=yes` + `subway=yes` + `level` + `name` con el nombre de la estación; laterales con `destination`; subterráneos con `layer` y `location=underground`. Su senda `highway=footway` + `indoor=yes` + `level` recorre el andén de punta a punta y sus extremos son vértices del polígono ([[adr-0011]]).
- Escaleras fijas: `highway=steps` + `indoor=yes` + `level=a;b` + `incline`. Bidireccionales dibujadas de abajo hacia arriba con `incline=up`; unidireccionales en el sentido de la flecha de Miró con `incline` según la diferencia de nivel en ese sentido. `step_count` se omite mientras no se conozca.
- Escaleras eléctricas: lo mismo más `conveying`, según [[adr-0012]]: unidireccional dibujada en el sentido de viaje con `conveying=forward`; bidireccional de abajo hacia arriba con `conveying=reversible`.
- Todo pathway con `is_bidirectional=0` lleva `oneway:foot=yes`, nunca `oneway`: `conveying` describe la máquina y `oneway:foot` el paso permitido, y los routers peatonales solo leen el segundo.
- `wheelchair=no` en toda `highway=steps`, fija o eléctrica; confirmado por Ricardo tras saber que la regla se había ampliado más allá de las fijas. `wheelchair` desde `wheelchair_boarding` no se emite hasta que sea dato medido.
- Elevador: nodo `highway=elevator` con `level=a;b` en lista con punto y coma. Pendiente de implementar: hoy el exportador se niega ante un elevador (`UnsupportedModeError`).
- Torniquetes: nodo `barrier=turnstile` + `amenity=ticket_validator` insertado desde la plantilla sobre el pasillo del vestíbulo; el grafo no los tiene como aristas.

### Accesos

- Nodo `railway=subway_entrance` + `entrance=<Stop.entrance>` + `level=0` + `description=<stop_name>`. Nada en `name`: el wiki prohíbe ahí el nombre de la estación y las descripciones; la letra señalizada irá en `ref` cuando [[task-18]] la dé.
- Un acceso con `osm_id` adopta el nodo existente y le agrega estas etiquetas ([[adr-0011]]).

### Plantillas

- Emparejamiento plantilla ↔ grafo estructural, por sufijo del `stop_id` (`P-01`, `N-03`, `E-01`) más un índice ordinal entre pathways paralelos con mismo origen, destino y modo; nunca por `miro_id` ([[adr-0006]]).

### Pendiente y explícito

- `gtfs:*` con sufijo de feed, según el estándar del wiki y no el `gtfs_*` sin documentar: no se emite hasta que [[task-27]] fije el sufijo.
- Relaciones `stop_area`: [[adr-0004]] decidió sumar nuestros accesos a las existentes y la reunión del 19 de agosto sugirió no usar relaciones; el exportador no emite relaciones y la pregunta queda diferida a [[task-11]], donde se lleva al colectivo antes de subir.
- El catálogo vive en `api/utils/osm/tags.py`; moverlo a configuración versionada es [[task-19]].

### Consecuencias

- **Bueno:** un solo documento vigente para etiquetas y convenciones; los dos ADR reemplazados dejan de contradecir al código sin perder su historia.
- **Malo:** cada cambio futuro de etiqueta obliga a superseder este ADR o a anotarlo, porque el catálogo ya no vive repartido; y dos reglas se declaran vigentes sin implementación (elevador, `gtfs:*`), lo que exige leer las tareas para saber qué corre hoy.

### Cómo se comprueba

`api/utils/osm/validate.py` corre en cada exportación: toda vía nuestra con `level`, `incline` y `conveying` coherentes con el orden de niveles, BFS desde cada acceso hasta cada senda de andén, ningún nodo nuestro a menos de 0,3 m de otro. Un `grep` de `level:ref` y de `"name"` en `entrance_tags` sobre `tags.py` no devuelve nada; `steps_tags` emite `wheelchair=no`.

## Más información

[[2026-09-02-sesion-integracion-osm-y-niveles]], [[adr-0011]], [[adr-0012]], `data/osm/README.md`.
