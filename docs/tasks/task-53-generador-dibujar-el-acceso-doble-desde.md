---
type: task
id: task-53
title: "Generador: dibujar el acceso doble desde `is_double` e índice de duplicado en la traza"
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-44]]", "[[task-38]]", "[[adr-0016]]"]
---

# Generador: dibujar el acceso doble desde `is_double` e índice de duplicado en la traza

Un acceso con `is_double` en la base (marca «[IZQ/DER]» del tablero) son dos bocas gemelas: dos nodos de acceso con el mismo `stop_id` y dos escaleras con el mismo `pathway_id` que nacen de un descanso compartido y se bifurcan hacia cada boca. En Polanco oriente (E-03, publicado el 27 de octubre de 2026 en el changeset 191085961) se trazó a mano y el bloque de la plantilla lo expresa con un `extra_way` explícito (`acceso-oriente-boca-2`, escalera de 8,73 m con el `pathway_id` repetido y `end_tags` de entrada). Dos huecos, descritos en `.claude/skills/station-tuning/references/estaciones/polanco.md` y `componentes/acceso-cielo-abierto.md`:

1. El generador no dibuja el acceso doble: debe emitir las dos bocas y las dos escaleras desde `is_double`, con el descanso compartido en el eje de la pestaña y cada escalera recta hacia su boca (la posición de las bocas es dato de campo, como vértices del anillo).
2. La traza no distingue a las gemelas: `note:pathway_id` repetido hace que `diff_station_osm` empareje una sola y reporte la otra como añadida (también pasa con la escalera en U de San Antonio partida en tramos con la misma traza). Hace falta un índice de duplicado en la traza (por ejemplo `note:pathway_id=<id>#2` o una clave aparte) que el diff y `publish_station_osm` entiendan.

## Criterios de aceptación

- [ ] Regenerar Polanco sin el `extra_way` manual reproduce las dos bocas y las dos escaleras de la 07
- [ ] `diff_station_osm` empareja los dos ways gemelos de Polanco y los tramos de la U de San Antonio sin reportar añadidos falsos
