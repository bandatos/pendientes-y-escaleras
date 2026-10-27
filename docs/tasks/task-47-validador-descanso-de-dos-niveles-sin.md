---
type: task
id: task-47
title: "Validador: descanso de dos niveles sin `incline` y cercanía entre segmentos de distinto nivel"
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-38]]"]
---

# Validador: descanso de dos niveles sin `incline` y cercanía entre segmentos de distinto nivel

Dos huecos del validador (`api/utils/osm/validate.py`) que las versiones aprobadas del 27 de octubre de 2026 dejaron a la vista:

1. `_check_incline` exige `incline` a todo `footway` con dos niveles. El descanso de la escalera en U de San Antonio (`level=-1;0`, entre dos tramos `steps -1;0`, decisión de Ricardo de conservarlo como lo dibujó Pablo) es plano por definición y marca error. Eximir al footway de dos niveles cuyos dos extremos son escaleras del mismo par de niveles.
2. El validador compara nodos contra nodos y nodos contra segmentos, pero no segmentos paralelos de distinto nivel entre sí: el encime de 0,17 m a lo largo de 12,6 m entre una fija y una reversible en San Joaquín 07 pasó sin aviso, y la escalera interior del andén bajo la pasarela en Portales 05 tampoco se detecta. `.claude/scratch/san-joaquin/clearance.py` ya mide holguras de nodos y de tramos paralelos entre niveles; graduarlo.

## Criterios de aceptación

- [x] San Antonio 06 valida sin errores
- [ ] Un par de tramos paralelos de distinto nivel a menos de 0,3 m da aviso, con test

## Notas de trabajo

- 27 de octubre de 2026 ([[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]): el punto 1 quedó resuelto en la misma sesión (commit posterior a 8b6da43): `_landing_ways` en `validate.py` exime al footway de dos niveles cuyos dos extremos son escaleras del mismo par de niveles, con `test_landing.py` (2 pruebas); San Antonio 06 pasa de 1 error a 0. Queda el punto 2 (cercanía entre segmentos de distinto nivel).
