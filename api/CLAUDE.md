# api — Django REST Framework

API de reportes ciudadanos sobre el estado de escaleras y elevadores en las estaciones del Metro (STC-Metro). El esquema de datos sigue el estándar GTFS (rutas, paradas, niveles, pathways).

## Comandos

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser

# Carga inicial — el orden importa
.venv/bin/python manage.py import_routes
.venv/bin/python manage.py import_stops
.venv/bin/python manage.py create_stations
.venv/bin/python manage.py import_stairs
.venv/bin/python manage.py recover_viz_features media/estaciones-match-stops.csv

.venv/bin/python manage.py collectstatic   # necesario antes de runserver
.venv/bin/python manage.py runserver

.venv/bin/pytest                           # settings: core.settings (ver pytest.ini)
```

## Base de datos

Se conmuta con `POSTRGRESQL_DB` en `.env` (el typo del nombre es real, respétalo):

- Vacío → SQLite en `DATABASE_NAME` (`django.contrib.postgres` se agrega solo cuando hay Postgres; no hay que tocar `INSTALLED_APPS`).
- `True` → PostgreSQL con los datos de conexión del `.env`; `DATABASE_SCHEMA` alimenta la opción `search_path`.

La base de desarrollo es PostgreSQL `escaleras-local`; se restaura con `psql escaleras-local < ~/databases/escaleras-local-<fecha>.sql` (respaldos fuera del repo). `dump.json` es histórico y trae acentos rotos: no lo uses como fuente.

## Arquitectura

Apps: `stop` (rutas, paradas, estaciones y niveles GTFS), `stair` (`Stair` legado + `Pathway` GTFS), `report` (`StairReport`, `EvidenceImage`), `profile_auth` (`User` propio con banderas de editor), `api` (vistas DRF, serializers y urls — sin modelos).

Patrones no obvios:

- **Doble modelo de escalera**: `Stair` es el legado de STC-Metro y `Pathway` su reemplazo compatible con GTFS. Un `StairReport` puede referenciar cualquiera de los dos.
- **`GET /api/catalogs/`**: endpoint masivo que anota cada escalera con el estado de su último reporte vía `OuterRef`/`Subquery`. Es lo que el frontend usa para inicializar su estado.
- **Export xlsx**: `StairReportViewSet` monta `ExportXlsMixin` de `yeeko_xlsx_export` (se instala desde GitHub). Las columnas se declaran en `xls_attrs`.
- **`INSTALLED_APPS` condicional**: `django.contrib.postgres` y `storages` se agregan en tiempo de ejecución en `core/settings/__init__.py` según variables de entorno. El almacenamiento cae a filesystem local si `AWS_STORAGE_BUCKET_NAME` no está definido.

### Módulo Miro (`utils/miro/`)

Convierte frames de Miro en registros `Stop`, `Level` y `Pathway` mediante `MiroSchemaBuilder`. Para las estructuras de la API, el mapeo color → `PathwayMode`, las convenciones de formas y las reglas de parseo, usa el skill `miro-api`.

```bash
.venv/bin/python manage.py preview_miro_schema <frame_title> [--from-db] [--output PATH] [--reset]
.venv/bin/python manage.py preview_miro_schema --all-stations
```

Pese al nombre, **persiste**: escribe `Level`, `Stop` y `Pathway` en la base (el HTML es un subproducto). `--from-db` es el único modo de solo lectura; `--all-stations` omite las estaciones que ya tienen `miro_id` salvo con `--reset`, que borra y reimporta. El frame se elige por título exacto contra `Stop.stop_name`.

- **`Stop.is_double`**: un nodo de Miro con «(IZQ & DER)» representa dos salidas físicas gemelas que solo se bifurcan al final; el builder crea **un solo** `Stop` con la bandera, y en OSM serán dos nodos con el mismo `ref`. Distinto de `stop_code` A/B: ahí Miro dibuja dos nodos unidos por un conector punteado con diamantes.

## Convenciones

Los mensajes de error de la API van en español: el frontend que los muestra es de cara al usuario.
