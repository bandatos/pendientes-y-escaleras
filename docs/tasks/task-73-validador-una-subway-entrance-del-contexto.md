---
type: task
id: task-73
title: "Validador: una subway_entrance del contexto que no es acceso de la estación hace fallar la conectividad"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Validador: una subway_entrance del contexto que no es acceso de la estación hace fallar la conectividad

El validador exige que toda `subway_entrance` del archivo llegue al andén, también las que vienen del contexto y no son accesos de la estación. En Villa de Cortés (entrada 13648121868, vértice de un edificio ajeno) y en Xola (5160032503 antes de enlazarla) eso obligó a enlazar o borrar para pasar la validación. Opciones: eximir las entradas del contexto que no son accesos de la estación, o avisar en vez de fallar.

## Criterios de aceptación

- [ ] Una entrada del contexto que no es acceso no tumba la validación
- [ ] Prueba en test de validate
