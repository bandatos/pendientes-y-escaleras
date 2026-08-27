---
type: task
id: task-8
title: Revisar y corregir la propuesta de agrupamiento de estaciones en familias
state: open
date: 2026-08-26
owner: ricardo
source: ["[[2026-08-26-agrupamiento-estaciones-familias]]"]
related: ["[[2026-08-26-agrupamiento-estaciones-familias]]"]
---

# Revisar y corregir la propuesta de agrupamiento de estaciones en familias

Para mapear en OSM por plantillas hace falta agrupar las ~195 estaciones en familias arquitectónicas. Se generó una propuesta automática a partir de la firma topológica del grafo de cada estación (andenes, accesos, niveles, escaleras por tramo, simetría) para las 98 estaciones con datos de Miro, y por línea/tramo/forma del polígono KML para las 44 sin datos (provisionales). El documento completo vive en [[2026-08-26-agrupamiento-estaciones-familias]] (referencia, con su CSV `2026-08-26-agrupamiento-estaciones-familias.csv` al lado en `docs/reference/`).

Son 15 familias; las mayores: «cajón con acceso directo a la calle» (28, modelo Doctores), «cajón clásico con edificio de acceso» (25, Cuitláhuac), «cajón profundo de vestíbulo único» (14, Coyoacán), «profunda de L7 en cascada» (10, San Joaquín), «superficie de Calzada de Tlalpan» (8, Portales). Criterio de agrupamiento: correspondencia = familia base + adiciones (por ejemplo, Ermita es idéntica a Portales/General Anaya más un pasillo a L12).

## Qué revisar

- Si las dos primeras familias («cajón con acceso directo a la calle» y «cajón clásico con edificio de acceso») son en realidad una sola: comparten el mismo esqueleto y difieren solo en tener o no un edificio de acceso en superficie.
- Las asignaciones provisionales (las 44 estaciones sin datos de Miro).
- Cinco familias no tienen ninguna estación levantada (LA, L12 oriente, LB norte, L5 oriente, L5/L6 subterránea): levantar una estación de cada una confirmaría 43 estaciones en total.

El documento se corrige moviendo estaciones entre listas directamente en la referencia.

## Criterios de aceptación

- [ ] Se decidió si las familias A y B se funden en una sola
- [ ] Las asignaciones provisionales quedan revisadas o marcadas para verificación de campo
- [ ] Se identificó qué familia levantar primero entre LA, L12 oriente, LB norte, L5 oriente y L5/L6 subterránea
- [ ] La referencia [[2026-08-26-agrupamiento-estaciones-familias]] y su CSV quedan actualizados con las correcciones
