# CLAUDE.md

**escaleras_survey_ws** ("Serpientes y Escaleras") — Django REST
Framework API for citizen reports on escalator/stair status in Mexico
City Metro (STC-Metro) stations. Models follow the GTFS standard.

Python 3.13+. Local dev server runs on port **8013**.

## Setup

```bash
pip install -r requirements.txt
cp .env.template .env
python manage.py migrate
python manage.py createsuperuser

# Seed data — order matters
python manage.py import_routes
python manage.py import_stops
python manage.py create_stations
python manage.py import_stairs
python manage.py recover_viz_features media/estaciones-match-stops.csv

python manage.py collectstatic   # required before runserver
python manage.py runserver
```

## Database

Toggle via `POSTRGRESQL_DB` in `.env`:
- **SQLite** (empty value): also comment out `'django.contrib.postgres'`
  in `INSTALLED_APPS`. It is added dynamically only when
  `POSTRGRESQL_DB=True`.
- **PostgreSQL** (`True`): provide connection details.
  `DATABASE_SCHEMA` sets the `search_path` option.

## Tests

```bash
pytest
```

Settings module: `core.settings` (see `pytest.ini`).

## Architecture

Apps: `stop` (GTFS routes/stops/stations/levels), `stair` (legacy
`Stair` + GTFS `Pathway`), `report` (`StairReport`, `EvidenceImage`),
`profile_auth` (custom `User` with editor flags), `api` (DRF views,
serializers, urls — no models).

Non-obvious patterns:
- **Dual stair model**: `Stair` is legacy STC-Metro; `Pathway` is the
  GTFS-compliant replacement. `StairReport` may reference either.
- **`GET /api/catalogs/`**: bulk-fetch endpoint that annotates stairs
  with their latest report status via `OuterRef`/`Subquery`, used by
  the frontend to initialize state.
- **XLS export**: `StairReportViewSet` mixes in `ExportXlsMixin` from
  `yeeko_xlsx_export` (GitHub install). Columns declared in `xls_attrs`.
- **Conditional `INSTALLED_APPS`**: `django.contrib.postgres` and
  `storages` are added at runtime in `core/settings/__init__.py`
  depending on env vars. Storage falls back to local FS when
  `AWS_STORAGE_BUCKET_NAME` is unset.

### Miro module (`utils/miro/`)

Converts Miro frames into `Stop`, `Level`, and `Pathway` records via
`MiroSchemaBuilder`. For API structures, color → `PathwayMode` mapping,
shape conventions, and parsing rules see the `miro-api` skill.

Preview without writing to DB:

```bash
python manage.py preview_miro_schema <frame_title> [--from-db] [--output PATH]
```

## Conventions

API error messages in Spanish (the user-facing frontend is in Spanish).