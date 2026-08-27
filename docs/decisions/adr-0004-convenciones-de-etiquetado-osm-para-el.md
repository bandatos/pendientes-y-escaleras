---
type: decision
id: adr-0004
title: "Convenciones de etiquetado OSM para el Metro: gtfs:*, Simple Indoor Tagging, level entero"
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["api/"]
---

# Convenciones de etiquetado OSM para el Metro: gtfs:*, Simple Indoor Tagging, level entero

## Contexto

No existe una tabla oficial GTFS-Pathways → OSM (`gtfs:pathway_id` y `gtfs:level_id` tienen cero usos en el mundo); la que usemos la estamos proponiendo. Había que fijar convenciones antes de generar un solo archivo.

## Resultado

- **Ids GTFS:** prefijo `gtfs:*` con sufijo de feed (estándar aprobado del wiki, p. ej. `gtfs:stop_id:MX-CMX-…`), no el `gtfs_*` que usa México sin documentación.
- **Esquema interior:** Simple Indoor Tagging puro (`indoor=room|corridor|area|level`), no el `indoor=yes` genérico que dominó en Múnich y que el visor recomendado no renderiza.
- **Niveles:** `level` entero consecutivo por apilamiento físico + `level:ref` con lo señalizado; siempre las dos. Sin fraccionarios ([[task-13]]). `layer=-N` en andenes subterráneos según Metro Mapping.
- **Andén:** polígono `railway=platform` + `public_transport=platform` + `area=yes`, conectado a cada escalera/elevador por nodo compartido (borde o interior); línea central `highway=footway` solo cuando la escalera cae en medio (andén central). Pasillos siempre como líneas `highway=footway` + `indoor=yes` + `level`, nunca `highway=corridor` (OSRM/GraphHopper lo ignoran) ni `tunnel=yes`.
- **Modos:** escalera `highway=steps` + `step_count` + `incline`; eléctrica `+ conveying=forward|backward|reversible`; elevador `highway=elevator` nodo con `level=-2;0`; torniquete `barrier=turnstile` + `amenity=ticket_validator`; accesos `railway=subway_entrance` + `entrance=entrance|exit|yes` + `ref` con la letra.
- **Dirección:** `incline`, `conveying` y `oneway:foot` dependen del orden de nodos de la vía; nuestra convención `from_stop → to_stop` se guarda como campo explícito y el generador la respeta.
- **Relaciones:** no creamos `stop_area` nuevas, pero sí sumamos nuestros accesos a las 58 existentes (se editan activamente; dejarlos fuera los deja huérfanos).

### Consecuencias

- **Bueno:** todo lo anterior está documentado en el wiki con conteos altos; validable con indoorhelper.
- **Malo:** somos los primeros en `gtfs:pathway_id`; hay que documentarlo en el wiki ([[task-11]]) y validarlo con Pablo, que ya mapea el Metro.

## Más información

[[2026-08-26-sesion-mapeo-osm]].
