---
type: task
id: task-65
title: "Generador: contexto de OSM más allá del área, con landuse, leisure y natural"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-49]]"]
---

# Generador: contexto de OSM más allá del área, con landuse, leisure y natural

Regla de Ricardo ([[adr-0018]]): el contexto va más allá del área con un radio mayor e incluye `landuse`, `leisure` y `natural` (jardines, estacionamientos), para verlos en el archivo; si además se editan se decide caso por caso (Ricardo quiso achicar el jardín de Nativitas y no pudo porque no venía). Hoy la consulta a Overpass no los trae, y eso produjo dos cosas el 27 de octubre de 2026: el jardín de Nativitas (`landuse=grass` 1275816500) no aparecía en el archivo y su árbol grande engañó la lectura de la imagen; y dos estaciones propusieron bajas de nodos que OSM rechazaba porque los usan ways que el contexto no trae (Nativitas 5156348365/66, el jardín; San Antonio Abad 13389920428, el estacionamiento 1429237668).

Alternativa o complemento: correr `check_station_osm_live` dentro del export antes de escribir bajas, o traer todos los ways que usan los nodos del contorno. Del mismo turno (Viaducto): el aviso de nodos «que siguen en uso» debería decir por quién están en uso (calzada o barda cambió la decisión), y las esquinas del contorno viejo que comparten nodo con bardas o vías deberían quedarse en el anillo aunque el KML las tenga a más de 50 cm, o al menos avisar que se sueltan.

## Criterios de aceptación

- [ ] El contexto trae landuse, leisure y natural con un radio mayor que el área, y salen en el archivo sin acción
- [ ] El generador no propone bajas de nodos que un way de OSM fuera del contexto usa
- [ ] Prueba en api/utils/osm
