---
type: decision
id: adr-0009
title: Convención de rótulos en el tablero de Miró y campo `entrance`
state: accepted
date: 2026-09-01
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
affects: ["api/utils/miro/parsers.py", "api/utils/miro/stop_mixin.py", "api/utils/miro/builder.py", "api/stop/models.py", "api/CLAUDE.md", "api/.claude/skills/miro-api/SKILL.md"]
related: ["[[adr-0003]]", "[[adr-0004]]", "[[adr-0008]]", "[[task-18]]"]
---

# Convención de rótulos en el tablero de Miró y campo `entrance`


## Contexto y planteamiento del problema

El tablero de Miró es la fuente del inventario de accesos, andenes, niveles y pathways; lo editan varias manos y el importador (`MiroSchemaBuilder`) lee solo texto de las figuras. Hasta esta sesión la marca de acceso doble se escribía «(IZQ & DER)» entre paréntesis, con lo que caía también en `stop_desc`; `[CLAUSURADA]` era la única marca entre corchetes; no había forma de decir que un acceso es solo de salida ni que un andén es solo de llegada; y los frames se emparejaban con `Stop.stop_name` por igualdad exacta, con lo que siete estaciones no se importaban. El campo `Stop` tenía `has_entry` y `has_exit` sin cablear a nada. Detalle y cifras en [[2026-09-01-sesion-miro-corchetes-entrance]].

## Criterios de decisión

- Que lo que se clasifica nunca contamine nombre ni descripción.
- Que la base exporte a OSM sin traducir, siguiendo [[adr-0004]].
- Un solo lugar por cada dato y un solo campo por cada concepto.
- Tolerancia a la ortografía de varias manos.

## Opciones consideradas

- **Marcas entre paréntesis** (lo que había): rechazada, los paréntesis alimentan `stop_desc`.
- **`has_entry` / `has_exit` como dos booleanos**: rechazada, dos campos para un concepto y sin vocabulario OSM.
- **Derivar la dirección de un acceso de las flechas de sus pathways**: no sustituye la marca (pasillos y elevadores son bidireccionales por regla y no permiten derivarla); queda como auditoría futura de congruencia.
- **Leer el color gris de relleno como clausura**: rechazada; el gris es ayuda visual, el importador no lee estilo de figuras.

## Resultado

1. **Corchetes clasifican, paréntesis describen.** Los corchetes nunca llegan a `stop_name` ni a `stop_desc`; una marca entre paréntesis no se interpreta. Marcas reconocidas, sin distinguir mayúsculas: `[IZQ/DER]` o `[IZQ & DER]` (solo en ese orden) → `is_double`; `[CLAUSURADA]`, `[CLAUSURADO]`, `[INHABILITADA]`, `[INHABILITADO]` → `is_closed`; `[salida]` / `[entrada]` → `entrance`. Un corchete no reconocido se descarta.
2. **«Acceso» es el nombre neutro** de un acceso bidireccional; «entrada» y «salida» se reservan para la marca (guía, no regla estricta).
3. **`Stop.entrance`** reemplaza a `has_entry` / `has_exit` con el vocabulario OSM `entrance=*`: `yes`, `entrance` (solo se entra), `exit` (solo se sale); `NULL` en nodos genéricos y estaciones. En andenes: `exit` = solo se baja (solo llegadas), `entrance` = solo se aborda (solo salidas); OSM lo expresa como rol `platform_exit_only` / `platform_entry_only` en la relación de ruta y GTFS como `drop_off` / `pickup` en `stop_times`, así que el exportador traduce y el dato es uno.
4. **Reglas de andenes**, derivadas del tablero por línea dentro de la estación: con 3 andenes en una línea, el que dice «central» es `exit` y los laterales `entrance`; terminal (2 andenes), el andén cuya dirección es la propia estación es `exit` y el otro `entrance`; 1 o 2 andenes no terminales, `yes`. La palabra «central» se queda en el nombre porque así ubica la gente el andén.
5. **Andenes de otros sistemas** (Trolebús Elevado «STE-L10») dibujados dentro del frame de una estación se ignoran.
6. **Frames «(en proceso)»** son mapeo inconcluso: se listan aparte y nunca se importan.
7. **Emparejamiento frame ↔ estación**: `Stop.short_name`, luego `stop_name`, luego comparación sin acentos ni mayúsculas. `short_name` se llena solo cuando el título de Miró difiere del nombre GTFS (Etiopía, Ferrería, Azcapotzalco, Viveros, M.A. de Quevedo).

### Consecuencias

- **Bueno:** `stop_desc` queda limpio; la base ya tiene 14 accesos unidireccionales y 34 andenes de un solo sentido; 105 estaciones importan en lugar de 98; el dato viaja a OSM sin traducir.
- **Malo:** cualquier marca nueva exige tocar `utils/miro/parsers.py`; la regla de andenes depende de que el tablero rotule bien las direcciones; la exclusión de otros sistemas es por prefijo y deja pasar accesos del Trolebús y el Cablebús ([[task-24]]).

### Cómo se comprueba

Migraciones `0010_stop_entrance_short_name` y `0011_stop_short_names_and_whitespace` aplicadas; la corrida completa de `preview_miro_schema --all-stations --reset` del 1 de septiembre de 2026 reportó 105 estaciones, 20 «en proceso» y 3 sin coincidencia (las leyendas); `Stop.objects.filter(entrance='exit', location_type_id=2).count() == 10`.

## Más información

[[2026-09-01-sesion-miro-corchetes-entrance]], [[adr-0003]], [[adr-0004]], [[adr-0008]], [[task-18]], [[task-7]].
