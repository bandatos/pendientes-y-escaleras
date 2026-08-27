---
type: task
id: task-7
title: Correcciones en el tablero de Miro para que crucen todos los frames
state: open
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

## Criterios de aceptación

- [ ] Los seis frames quedan renombrados y coinciden con `Stop.stop_name`
- [ ] El doble espacio de «Viveros y Derechos Humanos» está corregido en el CSV de origen o por migración de datos, no a mano en la base
- [ ] Azcapotzalco está confirmado como UAM Azcapotzalco o corregido
- [ ] Los cinco nodos con prefijo `L1-` mal puesto quedan conectados al grafo
- [ ] Los cuatro accesos duplicados de Tacubaya están renombrados según Parque Lira / Erasmo Castellanos
- [ ] La figura de Mixcoac (miro_id 3458764661687232696) tiene un color mapeado a un PathwayMode válido
- [ ] Se corrió `preview_miro_schema --all-stations` (con `--reset` en lo tocado) después de las correcciones
- [ ] Se revisó el estado de los 20 frames «(en proceso)»
