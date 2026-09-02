---
type: task
id: task-23
title: Revisar la compatibilidad de la base con OSM de punta a punta
state: open
date: 2026-09-01
owner: ricardo
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
related: ["[[adr-0003]]", "[[adr-0004]]", "[[adr-0009]]", "[[task-17]]", "[[task-19]]"]
---

# Revisar la compatibilidad de la base con OSM de punta a punta


Ricardo pidió que exista esta task (1 de septiembre de 2026). Hay decisiones parciales ([[adr-0003]] inventario físico en OSM, [[adr-0004]] etiquetas, [[adr-0009]] `entrance`, task-17 `osm_id`, task-19 catálogo de etiquetas) pero ninguna revisión completa campo por campo.

Alcance: para cada campo de `Stop`, `Level` y `Pathway` decir a qué etiqueta o rol OSM va (`entrance`, `ref`, `level`, `conveying`, `incline`, `step_count`, `is_bidirectional` → `oneway:foot`, `is_closed` → ¿`disused`? ¿`access=no`?), qué campos no tienen destino en OSM (`is_double`, `stop_code` A/B, `validated`) y qué necesita OSM que la base no guarda todavía. El resultado alimenta el exportador del módulo de mapeo ([[adr-0008]]).

## Criterios de aceptación

- [ ] Existe una tabla campo → etiqueta o rol OSM para Stop, Level y Pathway, escrita en docs/reference
- [ ] Están listados los campos sin destino en OSM y lo que OSM exige y la base no guarda
- [ ] El exportador del módulo de mapeo se alinea con esa tabla o la task que lo hará queda abierta
