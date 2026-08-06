---
type: task
id: task-5
title: Cablear apiSync a la API real o retirar el flujo de sincronización
state: open
date: 2026-08-06
owner: ricardo
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Cablear apiSync a la API real o retirar el flujo de sincronización

`syncStore.js` (usado por `SyncStatusBar.vue` y `StationSummary.vue`) llama `getApiSync()` sin argumento, y `ApiSyncService` tiene `apiBaseUrl = https://jsonplaceholder.typicode.com` como default, con endpoints tipo `/posts`. Es decir: el flujo de sincronización visible en la UI apunta a una API de prueba. Detectado el 5 de agosto de 2026 al revisar un reporte erróneo que lo daba por código muerto — no lo es, está a medio cablear.

## Criterios de aceptación

- [ ] Está decidido si el flujo syncStore→apiSync se conecta a la API real (pasando VITE_APP_API_URL a getApiSync) o se elimina
- [ ] El código refleja la decisión y jsonplaceholder desaparece como destino posible
