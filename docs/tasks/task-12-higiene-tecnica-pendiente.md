---
type: task
id: task-12
title: Higiene técnica pendiente
state: open
date: 2026-08-26
owner: ai
---

# Higiene técnica pendiente

Lista de deuda técnica detectada en la sesión del 26 de agosto de 2026 sobre la herramienta de mapeo a OSM:

- `api/utils/miro/scratch/test_build.py` es un script que pytest recolecta y que ejecutaría `MiroSchemaBuilder(...).run(reset_bd=True)` contra Miro (hoy lo frena pytest-django por casualidad): mover o renombrar para que pytest deje de recolectarlo.
- `api/api/tests.py` tiene 16 tests que nacieron rotos por referenciar un campo `Stair.name` inexistente.
- `collectstatic` falla porque las llaves S3 del `.env` dan 403 (en local conviene vaciar `AWS_STORAGE_BUCKET_NAME`).
- 10 registros `Level` huérfanos sin `stops`.
- Erratas restantes en la columna `name` de `api/media/estaciones-match-stops.csv` (Itzapalapa, Periferico Oeste, San Pedros de los Pinos, Atlalico, Linda Vista, Boulevard Puerto Aero, La Villa Basílica, Viveros - Derechos Humanos); ya no afectan la carga porque se resuelve por `stop_id`, pero conviene limpiarlas.
- `stop_id` de Moctezuma L1 lleva guion bajo en el GTFS.
- El comparador de títulos Miro↔BD no normaliza acentos.
- Los conectores punteados de accesos gemelos se cuentan como «saltados» en el log de importación.
- `DATABASE_NAME` sirve de nombre de archivo SQLite y de base Postgres a la vez, y el archivo SQLite puede quedar fuera de `.gitignore`.
- `StairReportViewSet.ordering` referencia `main_route__route_short_name`, un campo inexistente.
- `StairReport.date_reported` y `date_received` usan `auto_now=True`: se reescriben en cada `save()` y no conservan la fecha real del levantamiento, que [[adr-0003]] necesita para `survey:date`.

## Criterios de aceptación

- [ ] `test_build.py` ya no es recolectado por pytest
- [ ] Los 16 tests rotos de `api/api/tests.py` están corregidos o eliminados con justificación
- [ ] `collectstatic` corre en local sin error 403
- [ ] Los 10 `Level` huérfanos están resueltos o documentados como esperados
- [ ] Las erratas de `estaciones-match-stops.csv` están corregidas
- [ ] El `stop_id` de Moctezuma L1 está verificado contra el GTFS
- [ ] El comparador de títulos Miro↔BD normaliza acentos
- [ ] Los conectores punteados de accesos gemelos no se cuentan como saltados
- [ ] `DATABASE_NAME` no mezcla su uso entre SQLite y Postgres sin control de `.gitignore`
- [ ] `StairReportViewSet.ordering` no referencia campos inexistentes
- [ ] `date_reported`/`date_received` conservan la fecha del levantamiento (no `auto_now`)
