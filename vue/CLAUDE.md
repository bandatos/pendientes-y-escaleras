# Sistema de Relevamiento

Vue 3 frontend for citizen reports on the state of escalators/stairs in
the Mexico City Metro (STC-Metro). **v1 (current)**: app used by in-field
auditors. **v2 (planned)**: public-facing for citizens. Pairs with the
Django API at `D:\dev\open\escaleras_survey_ws` — see its `CLAUDE.md`
for backend details.

Package manager: **pnpm**. Node ≥ 20.19.

## Commands

```sh
pnpm install
pnpm dev       # Vite on port 5174 (host 0.0.0.0)
pnpm build
pnpm preview
```

The Django backend must be running locally on `:8013`. `.env` keys:
`VITE_APP_API_URL`, `VITE_APP_PASSPHRASE`, `VITE_APP_TITLE`,
`VITE_APP_VERSION`.

## Architecture

- Routes live in `src/views/`: `StationSelector` (`/`) and
  `StationSummary` (`/station/:station_id`).
- Stores in `src/stores/`, services in `src/services/`. **For any new
  store/service, or work touching those folders, follow the
  `refactor-store-service` skill** — it is the source of truth for the
  patterns used here.
- Offline-first via Dexie (db `relevamientoMetro`, schema v3 — see
  `src/services/indexDB.js`). Stores consume the static class
  `IndexedDBService`; do not touch the `db` instance directly.
- Bulk catalog endpoint: `GET /api/catalogs/` returns
  `{ routes, stops, stations, stairs }` and seeds both the Pinia store
  and the IndexedDB cache on app init via `useStationStore.init()`.
- `unplugin-auto-import` is active for Vue (`ref`, `computed`, `watch`,
  …) and Pinia (`defineStore`, `storeToRefs`, `acceptHMRUpdate`). Do
  not write those imports manually. Alias `@/` = `src/`.

## Gotchas

- `src/stores/syncStore.js` and `src/services/apiSync.js` look like
  dead code (the latter defaults `apiBaseUrl` to
  `jsonplaceholder.typicode.com`). Verify before reusing; pending
  cleanup once confirmed.
- Only STC-Metro stairs are loaded. Some stairs visible inside a
  station belong to adjacent malls and are filtered upstream by the
  backend (e.g. Estación Rosario).
- The backend has a dual stair model — legacy `Stair` and GTFS-compliant
  `Pathway`. A `StairReport` may reference either; do not assume one.

## Boundaries

- ⚠️ Bumping the Dexie schema version: field auditors carry unsynced
  data on their devices. Confirm a migration plan before raising the
  version in `src/services/indexDB.js`.
- 🚫 Never hard-code station, line, or stair IDs. They come from the
  catalog endpoint and the IndexedDB cache.