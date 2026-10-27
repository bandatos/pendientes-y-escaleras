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

## Avance del 22 de octubre de 2026 (sesión de San Antonio)

Hecho, sin commit hasta el cierre de esa sesión ([[2026-10-22-sesion-san-antonio-y-aprendizaje-de-plantilla]]):

- `l7-deep-cascade.json`: 1,8 m entre ejes en los seis bancos; aproches 1 m y 1,5 m en el extremo lejano del segundo conjunto (decisión de Ricardo); pasillos de −2 y −1 ortogonales a medio claro; tercer conjunto poniente de San Pedro corrido 2,25 m (confirmado); pasillo de −1 poniente de San Pedro en u = 9 (la muesca se rellena en la versión 06, [[task-40]]); salidas laterales con punto de geometría `elbow` (radio 8,58 m) que el generador rehace tras deformar los corredores; escaleras de cambio de andén medidas desde la senda (`dv`); `station_node.u` en la mitad del pasillo central; `id` en los `extra_ways`.
- Bloque por estación `stations.<stop_id>` (raíz antes del encaje, `local` en el marco de la estación después del encaje, `area` que sustituye el KML); San Joaquín y San Antonio lo usan. Documentado en el esquema de `data/osm/README.md`.
- Generador: tolerancia a pathways y nodos que la plantilla no dibuja (línea recta o posición provisional con `fixme`, aviso y línea en el reporte); el área solo reutiliza nodos de edificios y contornos de estación; `MIN_STACK_CLEARANCE_M` = 0,3; regla del edificio de OSM que cabe entero en el área (`BUILDING_FIT_MAX_M` = 0,5, cada nodo movido se reporta); el validador ya no compara un vértice de área con un nodo de OSM que no es edificio; una cascada colocada por `local` no es error de encaje.
- San Joaquín 06 aprobada por Ricardo: regenerar con su bloque la reproduce (26/26 pathways a < 0,1 m, 92/92 vértices de área a < 0,3 m). San Pedro no tiene versión aprobada; regenera sin errores y difiere de la 05 por las reglas nuevas.

Queda: los tres tests que Ricardo aprobó el 22 de octubre de 2026 («Sí a los tests, que los haga un SAG (en su momento)»), a escribir por un delegado: el `elbow` (tangencia y radio, también después de deformar los corredores), el filtro de categoría de `_area_node_ids` (no reutiliza un nodo de anillo de explanada, sí una esquina de edificio) y el aviso de holgura a 0,3 m; partir la plantilla en componentes; graduar la revisión por tramos (`check.py`, `segout.py`) a `api/utils/osm/` y que el validador la use; adelgazar la narrativa del README (D3, torniquetes, «San Joaquín con la plantilla de San Pedro»); los dos puntos menores de abajo de la lista. Lo que San Antonio enseña a la plantilla está en [[task-41]]; partir `builder.py`, en [[task-42]].

## Criterios de aceptación

- [ ] Regenerar San Joaquín y San Pedro fuera de su carpeta reproduce sus últimas versiones aprobadas dentro de una tolerancia acordada con Ricardo (San Joaquín reproducido el 22 de octubre de 2026 a < 0,1 m en pathways y < 0,3 m en área, con una tolerancia que fijó la sesión y Ricardo no acordó; cuatro pasillos de calle difieren hasta 0,26 m, pendiente en [[task-41]], punto 6. San Pedro espera su versión aprobada)
- [ ] El validador detecta un tramo fuera del área y un encimado entre niveles
- 27 de octubre de 2026 ([[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]): la plantilla L7 ganó `keys` (renombra sufijos por estación), `relocate`, `connector` y `end_tags` en los accesos, y el bloque de Polanco reproduce la 06 con residuo cero; `spacing` 3,0 en el par de −1 a 0 ([[adr-0016]]; los corrimientos de apilado quedan en [[task-46]]). Test propuesto y aún no escrito: `rename_template_keys`. La tolerancia del criterio 1 sigue sin acordarse; hoy las regeneraciones aprobadas residuo cero son Polanco; General Anaya 0,5 m ([[task-43]]).
