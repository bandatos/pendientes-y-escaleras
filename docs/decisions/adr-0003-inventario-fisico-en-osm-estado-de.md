---
type: decision
id: adr-0003
title: Inventario físico en OSM, estado de funcionamiento en nuestra base, unidos por identificador
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["api/stop/models.py", "api/stair/models.py", "api/report/models.py"]
---

# Inventario físico en OSM, estado de funcionamiento en nuestra base, unidos por identificador

## Contexto

OSM no tiene —y decidió no tener— etiqueta para «esta escalera está descompuesta»: `operational_status` está desaconsejada por su propia página (un consumidor que no la conoce sigue ruteando la escalera rota como buena) y toda la familia `temporary:` está obsoleta o sin votar desde hace una década. Su guía de buenas prácticas pide no mapear lo que cambia en semanas, y su criterio de verificabilidad exige que dos mapeadores independientes observen lo mismo. Además OSM no garantiza ids permanentes.

## Resultado

- A OSM sube lo físico y verificable: existencia, tipo, nivel, sentido, `ref` con el código físico señalizado del STC, accesibilidad medida, y las fechas de verificación (`survey:date`, `check_date:wheelchair`), que son nuestra contribución única.
- `StairReport.is_working`, `status_maintenance` y las fotos se quedan en nuestra base. Es la misma arquitectura de Deutsche Bahn FaSta / BrokenLifts: inventario en OSM, estado afuera.
- La unión es por identificador: campo nuevo `osm_id` en `Stop` y `Pathway` como enlace blando, con re-emparejamiento por `ref` + estación + geometría cuando se rompa. `miro_id`, `pathway_id` y nuestros ids de fila nunca suben a OSM (un namespace `bandatos:*` es lo que el wiki llama mala práctica).
- `wheelchair_boarding = 0` («sin información») jamás se convierte en `wheelchair=no`: se omite la etiqueta.

### Consecuencias

- **Bueno:** cumplimos la doctrina de OSM sin perder nuestro dato de estado; la app sigue siendo la fuente del estado en vivo.
- **Malo:** hace falta migración para `osm_id` ([[task-17]]). `traversal_time` y `length` no se exportan, pero no es pérdida: solo existen por GTFS y nunca los llenamos (vacíos en todos los pathways). `is_double` tampoco es pérdida: es una señal de generación —un stop produce dos nodos OSM con el mismo `ref`—, no un dato de GTFS.
- **Advertencia:** `StairReport.date_reported` y `date_received` usan `auto_now=True` y se reescriben en cada `save()`, así que hoy no sirven como fecha de levantamiento para `survey:date` / `check_date:wheelchair`. Hay que corregirlo antes de exportar ([[task-12]]).

## Más información

[[2026-08-26-sesion-mapeo-osm]], [[task-11]], [[task-17]].
