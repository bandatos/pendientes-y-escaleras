---
type: task
id: task-52
title: "Skill `station-tuning`: verificar el linaje como primer paso del diff de una versión de un tercero"
state: open
date: 2026-10-27
owner: ricardo
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
---

# Skill `station-tuning`: verificar el linaje como primer paso del diff de una versión de un tercero

Propuesta al harness del proyecto, pendiente del ok de Ricardo. El 27 de octubre de 2026 la versión de Portales que Pablo devolvió resultó descender de la 01 regenerada (la 03 borrada) y no de la 02 de Ricardo; el turno de diff lo descubrió comparando nodo por nodo contra cada versión previa (`.claude/scratch/portales/lineage.py`), después de haber perdido tiempo comparando contra la base equivocada. El skill dice que el primer entregable de un turno que recibe una versión es la comparación contra la anterior; falta decir que antes se verifica de cuál versión desciende (coincidencia al centímetro con cada previa), porque la numeración lineal no garantiza que la cadena no se haya bifurcado.

Línea propuesta para «Herramientas de cada turno»: «Antes de comparar, el turno establece de qué versión desciende la recibida (coincidencia al centímetro con cada una de las previas); si desciende de otra que la última, lo reporta primero, porque todo el diff cambia de base».

## Criterios de aceptación

- [ ] Ricardo aprueba o rechaza la línea
- [ ] Si la aprueba, está en SKILL.md y `lineage.py` graduó a herramienta del turno
