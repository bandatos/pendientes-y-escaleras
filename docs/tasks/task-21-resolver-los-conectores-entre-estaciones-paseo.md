---
type: task
id: task-21
title: Resolver los conectores entre estaciones (Paseo de los Libros, andador Chabacano–San Antonio Abad)
state: open
date: 2026-09-01
owner: ricardo
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
related: ["[[task-7]]"]
---

# Resolver los conectores entre estaciones (Paseo de los Libros, andador Chabacano–San Antonio Abad)


El importador de Miró trabaja frame por frame: un conector cuyos extremos viven en frames distintos nunca resuelve y aparece en el resumen como «stop not found for miro_id …». Son pasos peatonales reales entre estaciones: el Paseo de los Libros entre Zócalo y Pino Suárez, y el andador peatonal nuevo entre Chabacano y San Antonio Abad. Ricardo no sabe todavía cómo modelarlos; la task existe para no perderlos.

Conectores afectados en la corrida del 1 de septiembre de 2026 (frame, miro_id del conector):

- Zócalo 3458764675451631239 (extremos 3458764659031665501 / 3458764675451510395)
- Pino Suárez 3458764675592607605 (extremos 3458764671749336104 / 3458764659031665501)
- San Antonio Abad 3458764677010013290 (extremos 3458764677009670141 / 3458764677009904492)
- Chabacano 3458764677010013340 (extremos 3458764677009904492 / 3458764677009904566)
- Deportivo 18 de Marzo 3458764679400728562 (extremos 3458764679400728548 / 3458764679400728560)

Los ids de extremo se repiten entre estaciones vecinas (Zócalo con Pino Suárez, San Antonio Abad con Chabacano): es la huella de un conector que cruza frames.

Enfoque propuesto, sin diseñar: una segunda pasada al final de `--all-stations` que resuelva los conectores pendientes contra todos los `Stop` ya importados, y una decisión sobre a qué estación pertenece el `Pathway` resultante (o si GTFS lo admite entre dos `parent_station` distintos).

## Criterios de aceptación

- [ ] Está decidido cómo se modela un pathway entre dos estaciones (a qué parent_station pertenece o si GTFS lo admite entre dos)
- [ ] El importador resuelve los 5 conectores listados en una segunda pasada o los reporta con un motivo propio distinto de «stop not found»
