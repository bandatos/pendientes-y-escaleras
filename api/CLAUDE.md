# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**escaleras_survey_ws** ("Serpientes y Escaleras") is a Django REST Framework API for reporting and tracking the status of escalators/stairs in Mexico City Metro (STC-Metro) stations. It models transit infrastructure using the GTFS standard and allows citizens to submit accessibility reports.

## Setup

**Python 3.13+ required.**

```bash
# Create and activate virtualenv
python3 -m venv escaleras
source escaleras/bin/activate  # Linux/Mac
.\escaleras\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.template .env

# Run migrations and seed data
python manage.py migrate
python manage.py createsuperuser
python manage.py import_routes
python manage.py import_stops
python manage.py create_stations
python manage.py import_stairs
python manage.py recover_viz_features media/estaciones-match-stops.csv

# Collect static files (required before runserver)
python manage.py collectstatic

# Run dev server (port 8013 is the expected local URL)
python manage.py runserver
```

## Database Configuration

**SQLite (local development)** — leave `POSTRGRESQL_DB` empty in `.env`:
```env
POSTRGRESQL_DB=
DATABASE_NAME=db.sqlite3
```
When using SQLite, comment out `'django.contrib.postgres'` in `INSTALLED_APPS` (it is added dynamically only when `POSTRGRESQL_DB=True`).

**PostgreSQL** — set `POSTRGRESQL_DB=True` and provide connection details. `DATABASE_SCHEMA` sets the `search_path` option.

## Running Tests

```bash
pytest                        # run all tests
pytest api/tests.py           # run a specific test file
pytest api/tests.py::TestName # run a specific test
```

Settings module is `core.settings` (configured in `pytest.ini`).

## Architecture

### Apps

| App | Purpose |
|-----|---------|
| `stop` | GTFS-based models: `Route`, `Stop`, `Station`, `Level`, `Trip`, `StopTime`, `Shape` |
| `stair` | `Stair`, `Pathway`, `PathwayMode` — physical escalators/stairs and their GTFS pathway graph representation |
| `report` | `StairReport`, `EvidenceImage` — citizen accessibility reports with optional photo evidence |
| `profile_auth` | Custom `User` model (extends `AbstractUser`) with `full_editor`/`mini_editor` permission flags |
| `api` | All DRF views, serializers, and URL routing (no models) |

### API Structure

All routes under `/api/`. DRF DefaultRouter registers:
- `GET/POST /api/station/` — `StationViewSet`
- `GET/POST /api/stair_report/` — `StairReportViewSet` (also has `export_xls` action)
- `/api/stair_report/{id}/evidence_image/` — `AscertainableViewSet`
- `POST /api/login/` — token authentication
- `GET /api/catalogs/` — returns all routes, stops, stations, and stairs with their latest report status in a single response (used by the frontend to initialize state)
- `GET /api/health/` — health check

### Key Design Patterns

- **GTFS alignment**: Models in `stop` and `stair` mirror the GTFS spec (`stops.txt`, `pathways.txt`, `routes.txt`, etc.). Field names use GTFS conventions (`stop_id`, `route_id`, `pathway_id`).
- **Dual stair model**: `Stair` is a custom model for legacy STC-Metro data. `Pathway` is the newer GTFS-compliant model. `StairReport` can reference either.
- **Catalog endpoint**: `GET /api/catalogs/` is a single bulk-fetch endpoint that annotates stairs with their latest report data using `OuterRef`/`Subquery`.
- **XLS export**: `StairReportViewSet` mixes in `ExportXlsMixin` from `yeeko_xlsx_export` (installed from GitHub). The `xls_attrs` list on the viewset defines columns.
- **Storage**: When `AWS_STORAGE_BUCKET_NAME` is set, media and static files use S3 via `django-storages`. Otherwise, local filesystem is used.
- **Auth**: Token authentication (`rest_framework.authtoken`). Default permission is `IsAuthenticatedOrReadOnly`.

### Settings

`core/settings/__init__.py` loads from `.env` via `python-dotenv`. Helper functions in `core/settings/get_env.py` handle typed env vars (`getenv_bool`, `getenv_int`, `getenv_list`). The `django.contrib.postgres` app and `storages` are added to `INSTALLED_APPS` conditionally at runtime.
