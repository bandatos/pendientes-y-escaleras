---
type: task
id: task-43
title: "General Anaya (L2): estación afinada, publicada y pendiente de cierre"
state: open
date: 2026-10-27
owner: ricardo
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-26]]", "[[task-38]]", "[[adr-0015]]"]
---

# General Anaya (L2): estación afinada, publicada y pendiente de cierre

Estación de superficie de la Calzada de Tlalpan, componente `tlalpan-surface`, carpeta `data/osm/l2-general-anaya/`, hechos en `.claude/skills/station-tuning/references/estaciones/general-anaya.md`.

## Estado al 27 de octubre de 2026

- Versión aprobada: `general-anaya-06-claude.osm`. Cadena: 01 generada (rumbo 16,1°), 02 con lo aprendido de `portales-02-rick`, 03 de Pablo (bancos de acceso alargados a 12,5 m con el pie al fondo del pabellón), 04 endereza la deriva de Pablo, 05 nodo de estación al cruce real de los brazos (u −2,97), 06 escaleras del andén de 9,11 m (llegada fija, pie corrido; es el máximo que cabe con las llegadas a 10,5 m y 1,5 m libres).
- Publicada en OSM por Ricardo: changeset 191085829 (79 creados, 2 modificados, 14 borrados), contenido verificado contra el `-pub`.
- La plantilla `tlalpan-surface.json` ya mide brazos y lóbulos (`arms.py`) y regenera la estación con residuo máximo de 0,5 m (banco poniente de Pablo a 3,5 m del fondo contra 3 de la regla; andén descentrado 0,46 m). Lo que no reproduce: las escaleras del andén y la losa longitudinal, que viven en el bloque `local` de la estación hasta que la plantilla aprenda el vestíbulo longitudinal (task de la plantilla de Tlalpan).
- Pablo no trabajó las escaleras del andén; el estándar de 9,11 m va en la lista de validación que se le manda.
- Defecto del generador que esta estación destapó, arreglado: la 01 daba de baja diez nodos de OSM que la Calzada y las vías seguían usando (`settle_deletes`).

## Criterios de aceptación

- [ ] Ricardo declara cerrada la estación
- [ ] Regenerar con --out reproduce la 06 dentro de la tolerancia que Ricardo acuerde (task-38)
