---
type: task
id: task-7
title: Correcciones en el tablero de Miro para que crucen todos los frames
state: closed
date: 2026-08-26
owner: ricardo
---

# Correcciones en el tablero de Miro para que crucen todos los frames

Al construir la herramienta para mapear en OpenStreetMap lo que está en Miro y en la base de datos (sesión del 26 de agosto de 2026) aparecieron desajustes entre los nombres de frame en Miro y `Stop.stop_name` en la base, más errores de captura que dejan nodos sueltos del grafo.

## Renombrar frames para que coincidan con `Stop.stop_name`

- `Escuadron 201` → `Escuadrón 201`
- `Tezozomoc` → `Tezozómoc`
- `M.A. de Quevedo` → `Miguel Ángel de Quevedo`
- `Etiopía` → `Etiopía y Plaza de la Transparencia`
- `Ferrería` → `Ferrería y Arena Ciudad de México`
- `Viveros` → `Viveros y Derechos Humanos` (en la base este nombre tiene además un doble espacio: corregirlo en el CSV de origen o con una migración de datos, nunca a mano en la base)
- `Azcapotzalco`: confirmar si corresponde a «UAM Azcapotzalco» (L6)

## Corregir el prefijo `L1-` mal puesto

Cinco andenes quedan hoy sueltos del grafo por llevar el prefijo de línea equivocado: los segundos andenes de Bondojito, Canal del Norte, Fray Servando y Talismán (familia F, L4), y un nodo de Morelos.

## Tacubaya: accesos duplicados

Hoy hay «L1 Acceso suroriente» ×2 y «L1 Acceso nororiente» ×2. Según Wikipedia corresponden a Parque Lira y Erasmo Castellanos: renombrar cada par para distinguirlos.

## Mixcoac

Una figura (miro_id 3458764661687232696) tiene un color que no cae en el mapeo color → PathwayMode: identificarlo y corregirlo.

## Reimportar

Tras corregir, reimportar con `preview_miro_schema --all-stations` (con `--reset` para las estaciones tocadas).

## Frames pendientes

20 frames siguen marcados «(en proceso)» en Miro.

## Resolución (1 de septiembre de 2026)

Sesión registrada en [[2026-09-01-sesion-miro-corchetes-entrance]]; la convención resultante es [[adr-0009]].

- Los frames ya no se renombran: `Stop.short_name` guarda el nombre corto del tablero (Azcapotzalco, Etiopía, Ferrería, Viveros, M.A. de Quevedo) y el emparejamiento normaliza acentos, con lo que «Escuadron 201» y «Tezozomoc» habrían coincidido igual; de todos modos se les puso la tilde por API. Azcapotzalco quedó confirmado como «UAM Azcapotzalco».
- El doble espacio de Viveros (y el de «Niños Héroes y Poder Judicial CDMX», que tenía el mismo) se corrigió en la canónica `data/gtfs/`, en las copias, en `import_stops` (colapsa espacios) y por migración de datos `0011`.
- Prefijo `L1` corregido por API en los cinco nodos previstos más Candelaria (mismo defecto, no listado); Morelos pasó a `LB`, no a L4: el nodo está en la banda de LB y sus conectores van a vestíbulos de LB.
- La figura de Mixcoac no era un error: es el conector punteado con diamantes que marca accesos A/B y que el importador usa para `stop_code`. Que el resumen lo cuente como «omitido» es cosa de [[task-12]].
- Se reimportó tres veces con `--all-stations --reset`; 105 frames importan.
- Lo que sigue pendiente se trasladó a [[task-24]]: los accesos duplicados de Tacubaya (ahora ×3 y ×3), las 20 frames «(en proceso)» y el frame «Copy of Tezonco».

## Criterios de aceptación

- [x] Los seis frames coinciden con la base (por `short_name` y normalización, no por renombrado)
- [x] El doble espacio de «Viveros y Derechos Humanos» está corregido en el CSV de origen o por migración de datos, no a mano en la base
- [x] Azcapotzalco está confirmado como UAM Azcapotzalco o corregido
- [x] Los cinco nodos con prefijo `L1-` mal puesto quedan conectados al grafo
- [ ] Los accesos duplicados de Tacubaya están renombrados según Parque Lira / Erasmo Castellanos (trasladado a [[task-24]])
- [x] La figura de Mixcoac (miro_id 3458764661687232696) resultó válida: marcador A/B, no pathway
- [x] Se corrió `preview_miro_schema --all-stations` (con `--reset` en lo tocado) después de las correcciones
- [ ] Se revisó el estado de los 20 frames «(en proceso)» (trasladado a [[task-24]])
