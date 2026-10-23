---
type: task
id: task-38
title: Aprendizaje de la plantilla de la Línea 7 tras San Joaquín y San Pedro
state: open
date: 2026-10-22
owner: ai
source: ["[[2026-10-22-sesion-ciclo-de-afinacion-y-san-joaquin]]"]
related: ["[[adr-0014]]", "[[task-26]]", "[[task-29]]"]
---

# Aprendizaje de la plantilla de la Línea 7 tras San Joaquín y San Pedro

Las versiones `san-joaquin-06-claude.osm` y `san-pedro-de-los-pinos-05-claude.osm` llevan reglas que la plantilla `l7-deep-cascade.json` y el generador todavía no producen. Ricardo aprobó el ciclo en el que la plantilla aprende al cierre; este es ese aprendizaje, pendiente.

- Partir la plantilla en componentes (andén profundo de L7; cascada) más un bloque de hechos por estación (`closed_doors`, puertas corridas, largos de escaleras, ancho del pasillo central, corrección del área).
- Salidas laterales de 6,5 m con codos de cuartos de círculo concéntricos; bocas y esquinas de isla sobre el borde exterior del andén; pasillo central ortogonal a ancho constante.
- Conjuntos de escaleras a 1,8 m entre ejes, nodo de encuentro en el eje, corrimiento del conjunto (no del nodo) para no encimar niveles; reemplaza el `stack_offset` que mueve el nodo.
- Nodo de estación a la mitad del pasillo central y en el eje entre andenes.
- La regla de los 50 cm que convierte un nodo de OSM cercano en vértice del área se filtra por categoría: soldó el área subterránea de San Joaquín al hueco de un baño.
- El validador del generador prueba tramos y no solo nodos (fuera del área y a menos de 0,3 m de una línea de otro nivel); los scripts `check.py` y `segcheck.py` de `.claude/scratch/sj/` y `.claude/scratch/spp/` son la semilla.
- Primer paso: graduar `check.py` (`.claude/scratch/sj/`) y `segcheck.py` (`.claude/scratch/spp/`) a `api/utils/osm/`, versionados, para que el validador y [[task-40]] no dependan de scripts ignorados por git en un repo público.
- El edificio de OSM que sobresale unos centímetros del área se ajusta mínimamente para caber (Ricardo lo hizo a mano con el pabellón oriente de San Joaquín).
- Escaleras de cambio de andén que arrancan más adentro del pasillo central, simétricas respecto del eje entre andenes, con largo por estación.
- Pasillos de −1 y −2 ortogonales, con los torniquetes recorridos con ellos.
- `closed_doors` y la puerta norte del pabellón oriente entran al bloque por estación (viene del punto 4 de [[task-37]]).
- Adelgazar `data/osm/README.md` a lo operativo (comandos, carpetas, esquema de plantilla): Ricardo lo aprobó el 22 de octubre de 2026 con la opción 1 de «las 3 capas»; los criterios en prosa viven en las referencias del skill `station-tuning`.
- Quitar la ruta vieja `OSM_DIR / "context"` que queda como respaldo en `compose_station_imagery.py`.
- `builder.py:1281` tiene una variable sin uso (`end`).

## Criterios de aceptación

- [ ] Regenerar San Joaquín y San Pedro fuera de su carpeta reproduce sus últimas versiones aprobadas dentro de una tolerancia acordada con Ricardo
- [ ] El validador detecta un tramo fuera del área y un encimado entre niveles
