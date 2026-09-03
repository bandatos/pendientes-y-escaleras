---
type: decision
id: adr-0002
title: JOSM como editor de carga y MapRoulette para repartir estaciones
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["vue/", "api/"]
related: ["[[adr-0011]]"]
---

# JOSM como editor de carga y MapRoulette para repartir estaciones

## Contexto

Nuestra base tiene la topología de cada estación (andenes, nodos, pathways por nivel) pero ninguna coordenada por elemento: solo un punto GTFS por estación. Lo que hay que hacer es generar por estación un archivo con todos los elementos dispuestos en una rejilla estándar cerca del punto de la estación, que un humano acomode sobre imagen satelital y suba. Hace falta un editor que acepte objetos pregenerados en una capa editable y una forma de repartir ~195 estaciones entre pocos voluntarios.

## Opciones consideradas

- **JOSM** (editor de escritorio de OSM): carga archivos `.osm` con ids negativos como objetos nuevos; su Remote Control local (`127.0.0.1:8111`) permite que una app web le mande `/load_and_zoom` (baja lo existente y prefija los tags del changeset) y `/import?url=` (abre nuestro `.osm`). `load_data` no sirve para estaciones grandes (límite de URL). Plugins útiles: ShapeTools (rotar por ángulo numérico), indoorhelper (filtro por nivel, validación Simple Indoor Tagging), utilsplugin2 («Replace geometry» para conflación manual); el plugin `conflation` es experimental.
- **iD** (editor web por defecto): no puede recibir datos externos editables (solo GPX de referencia).
- **Rapid** (Meta): presenta geometría pregenerada, pero exige publicar el dataset en ArcGIS Online y revisión de Esri.
- **Vespucci / Every Door / StreetComplete** (móviles): sin GPS bajo tierra; Every Door sirve para la campaña de superficie (accesos, `wheelchair`).
- **MapRoulette**: gestor de tareas; con `mr-cli` cada estación se vuelve una tarea con su archivo de cambios adjunto, generado desde los mismos `.osm`.

## Resultado

JOSM como editor, disparado desde la app Vue vía Remote Control (`/load_and_zoom` + `/import?url=` contra un endpoint que sirve el `.osm` de la estación), y MapRoulette encima para reparto, estado y revisión entre voluntarios. Rapid queda como segunda opción si el proyecto crece. Overpass (espejo `maps.mail.ru`, con pausas: la instancia principal bloquea por ráfagas) para traer lo existente alrededor de cada estación.

### Consecuencias

- **Bueno:** un solo flujo, sin dependencias externas de revisión; el mismo archivo alimenta JOSM y MapRoulette.
- **Malo:** los voluntarios deben instalar JOSM y aprenderlo (Ricardo no lo ha usado); la conflación contra accesos existentes es manual.

## Más información

[[2026-08-26-sesion-mapeo-osm]], [[2026-08-19-reunion-bandatos-limpia]].

## Notas de enmienda

- 2 de septiembre de 2026 ([[2026-09-02-sesion-integracion-osm-y-niveles]]): la decisión central, JOSM como editor de subida, sigue vigente. Dos detalles del resultado ya no describen lo que corre: los endpoints de Overpass son `overpass-api.de` con `overpass.kumi.systems` de respaldo, no el espejo `maps.mail.ru`; y la conflación contra accesos existentes dejó de ser manual para los accesos enlazados por `osm_id` en `data/osm/osm-links.csv`, que el generador adopta según [[adr-0011]].
