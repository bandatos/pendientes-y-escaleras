# vue — PWA de relevamiento

Frontend Vue 3 + Vuetify para los reportes sobre el estado de escaleras y elevadores del Metro (STC-Metro). **v1 (actual)**: app para auditores en campo. **v2 (planeada)**: versión pública para la ciudadanía. Consume la API de `../api/` (ver su `CLAUDE.md`).

Claves de `.env`: `VITE_APP_API_URL`, `VITE_APP_PASSPHRASE`, `VITE_APP_TITLE`, `VITE_APP_VERSION`.

## Arquitectura

- Solo hay dos rutas, en `src/views/`: `StationSelector` (`/`) y `StationSummary` (`/station/:station_id`).
- Offline-first con Dexie (base `relevamientoMetro`, esquema v3 — ver `src/services/indexDB.js`). Los stores consumen la clase estática `IndexedDBService`; no toques la instancia `db` directamente.
- `useStationStore.init()` llama a `GET /api/catalogs/`, que devuelve `{ routes, stops, stations, stairs }` de un golpe y siembra a la vez el store de Pinia y el caché de IndexedDB.
- `unplugin-auto-import` está activo para Vue (`ref`, `computed`, `watch`, …) y Pinia (`defineStore`, `storeToRefs`, `acceptHMRUpdate`): no escribas esos imports a mano. Alias `@/` = `src/`.

## Gotchas

- `src/services/apiSync.js` está a medio cablear: `syncStore.js` lo usa (`getApiSync()` sin argumento), por lo que su `apiBaseUrl` cae en el default `jsonplaceholder.typicode.com` — el flujo de sincronización apunta a una API de juguete, no a la real. Ver la task abierta en `docs/` antes de tocarlo.
- Solo se cargan escaleras del STC-Metro. Algunas escaleras que se ven dentro de una estación pertenecen a centros comerciales contiguos y el backend las filtra aguas arriba (por ejemplo, Estación Rosario).
- El backend tiene doble modelo de escalera, `Stair` legado y `Pathway` GTFS. Un `StairReport` puede referenciar cualquiera de los dos: no asumas uno.

## Límites

- ⚠️ Subir la versión del esquema de Dexie: los auditores de campo cargan datos sin sincronizar en sus dispositivos. Confirma un plan de migración antes de incrementarla en `src/services/indexDB.js`.
- 🚫 Nunca hardcodees ids de estación, línea o escalera. Vienen del endpoint de catálogos y del caché de IndexedDB.
