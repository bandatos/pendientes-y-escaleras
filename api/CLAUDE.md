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

- Vacío → SQLite. Además hay que comentar `'django.contrib.postgres'` en `INSTALLED_APPS`, porque solo se agrega dinámicamente cuando `POSTRGRESQL_DB=True`.
- `True` → PostgreSQL con los datos de conexión del `.env`; `DATABASE_SCHEMA` alimenta la opción `search_path`.

## Arquitectura

Apps: `stop` (rutas, paradas, estaciones y niveles GTFS), `stair` (`Stair` legado + `Pathway` GTFS), `report` (`StairReport`, `EvidenceImage`), `profile_auth` (`User` propio con banderas de editor), `api` (vistas DRF, serializers y urls — sin modelos).

Patrones no obvios:

- **Doble modelo de escalera**: `Stair` es el legado de STC-Metro y `Pathway` su reemplazo compatible con GTFS. Un `StairReport` puede referenciar cualquiera de los dos.
- **`GET /api/catalogs/`**: endpoint masivo que anota cada escalera con el estado de su último reporte vía `OuterRef`/`Subquery`. Es lo que el frontend usa para inicializar su estado.
- **Export xlsx**: `StairReportViewSet` monta `ExportXlsMixin` de `yeeko_xlsx_export` (se instala desde GitHub). Las columnas se declaran en `xls_attrs`.
- **`INSTALLED_APPS` condicional**: `django.contrib.postgres` y `storages` se agregan en tiempo de ejecución en `core/settings/__init__.py` según variables de entorno. El almacenamiento cae a filesystem local si `AWS_STORAGE_BUCKET_NAME` no está definido.

### Módulo Miro (`utils/miro/`)

Convierte frames de Miro en registros `Stop`, `Level` y `Pathway` mediante `MiroSchemaBuilder`. Para las estructuras de la API, el mapeo color → `PathwayMode`, las convenciones de formas y las reglas de parseo, usa el skill `miro-api`.

Vista previa sin escribir en la base:

```bash
.venv/bin/python manage.py preview_miro_schema <frame_title> [--from-db] [--output PATH]
```

## Convenciones

Los mensajes de error de la API van en español: el frontend que los muestra es de cara al usuario.
