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

Pese al nombre, **persiste**: escribe `Level`, `Stop` y `Pathway` en la base (el HTML es un subproducto). `--from-db` es el único modo de solo lectura; `--all-stations` omite las estaciones que ya tienen `miro_id` salvo con `--reset`, que borra y reimporta. El emparejamiento frame ↔ estación se describe abajo.

- **Corchetes vs. paréntesis en los nodos de Miro**: los corchetes clasifican y nunca llegan a `stop_name` ni a `stop_desc`; los paréntesis describen y alimentan `stop_desc`. Una marca de clasificación entre paréntesis no se interpreta: queda como texto de descripción. Marcas reconocidas (mayúsculas indistintas): `[IZQ/DER]` o `[IZQ & DER]` → `is_double`; `[CLAUSURADA]`, `[CLAUSURADO]`, `[INHABILITADA]`, `[INHABILITADO]` → `is_closed`; `[salida]` / `[entrada]` → `entrance`. Cualquier otro corchete se descarta sin aviso: si aparece uno nuevo, agrégalo a `utils/miro/parsers.py`.
- **`Stop.is_double`**: un nodo de Miro con «[IZQ/DER]» representa dos salidas físicas gemelas que solo se bifurcan al final; el builder crea **un solo** `Stop` con la bandera, y en OSM serán dos nodos con el mismo `ref`. Distinto de `stop_code` A/B: ahí Miro dibuja dos nodos unidos por un conector punteado con diamantes (ese conector no es un pathway; el importador lo usa solo para el `stop_code`).
- **`Stop.entrance`** usa el vocabulario OSM `entrance=*` tal cual (`yes`, `entrance`, `exit`) para poder exportarlo sin traducir. En accesos: `[salida]` → `exit`, `[entrada]` → `entrance`, sin marca → `yes`; el nombre neutro es «Acceso». En andenes se deriva del tablero, no de una marca: `exit` = solo se baja (solo llegadas), `entrance` = solo se aborda (solo salidas). Reglas: estación no terminal con 3 andenes en una línea → el que dice «central» es `exit` y los laterales `entrance`; terminal (2 andenes) → el andén cuya dirección es la propia estación es `exit`, el otro `entrance`; 1 o 2 andenes no terminales → `yes`. La palabra «central» se queda en el nombre porque así ubica la gente el andén. Nodos genéricos → `NULL`.
- **Andenes de otros sistemas** (Trolebús Elevado `STE-L10`, etc.) dibujados dentro del frame de una estación se ignoran: no son parte de este inventario y romperían el conteo de andenes.
- **Frames y estaciones**: un frame se empareja con `Stop.short_name`, luego `stop_name`, luego comparación sin acentos ni mayúsculas. `short_name` se llena solo cuando el título de Miro difiere del nombre GTFS (Etiopía, Ferrería, Azcapotzalco, Viveros, M.A. de Quevedo). Los frames con sufijo «(en proceso)» son mapeo inconcluso: se listan aparte y nunca se importan.
- **Conectores entre estaciones** (Paseo de los Libros, andador Chabacano–San Antonio Abad) no resuelven porque el importador trabaja frame por frame; aparecen como «stop not found» en el resumen. Pendiente en `docs/tasks/task-21`.
- **`Stop.short_name`** se llena desde `utils/miro/short_names.py` tanto en `import_stops` como en la migración de datos: `import_stops` borra y recrea todas las paradas, así que cualquier valor que solo viva en una migración se pierde en la siguiente carga.

Herramientas auxiliares del tablero:

```bash
.venv/bin/python manage.py dump_miro_raw [--output PATH]        # vuelca todos los frames a JSON, solo lectura
.venv/bin/python manage.py apply_miro_edits --edits PATH [--apply]  # edita textos/títulos en Miro; sin --apply solo simula
```

`apply_miro_edits` escribe en un tablero compartido: siempre revisa la simulación antes de `--apply`; el command vuelve a leer cada ítem y omite los que ya cambiaron. El formato del JSON de entrada está en `utils/miro/apply_miro_edits.example.json`.

## Convenciones

Los mensajes de error de la API van en español: el frontend que los muestra es de cara al usuario.
