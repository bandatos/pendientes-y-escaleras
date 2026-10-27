---
type: task
id: task-46
title: "Plantilla L7: corrimiento de apilado del par de −1 a 0 con la separación de 3,0 m"
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-38]]"]
---

# Plantilla L7: corrimiento de apilado del par de −1 a 0 con la separación de 3,0 m

El 27 de octubre de 2026 el `spacing` de `cascada-oriente-3` y `cascada-poniente-3` pasó a 3.0 (regla de Pablo confirmada por Ricardo). Con los `stack_offset` actuales el generador avisa holguras bajo 0,3 m: San Pedro oriente 0,20 (antes 0,40), San Joaquín 0,15 en los dos lados (antes 0,45). La holgura máxima entre un par a 3,0 y un trío a 1,8 es 0,30 m por lado, y solo si comparten eje y van a 0°.

Lo que las versiones aprobadas enseñan (San Joaquín 09, San Pedro 08):

- El par va centrado en el eje del trío de abajo; en San Joaquín oriente se corrió −0,47 m en u para despejar la reversible (hecho de estación).
- La pierna del pasillo −1 que sale del nodo de encuentro del trío debe terminar unos 0,6 m antes del arranque de nivel 0, porque las colas de nivel 0 se abren unos 34°.
- Las puertas clausuradas alineadas con el cruce del pabellón van sobre su muro a la v del eje del par.
- Opciones: medir el corrimiento en las aprobadas y llevarlo a cada bloque de estación, o fijar un `stack_offset` que dé 0,3 m (por ejemplo −2,25 da 0,45 contra el trío) y dejar la diferencia como hecho de estación.

## Criterios de aceptación

- [ ] Regenerar San Joaquín y San Pedro no avisa holguras bajo 0,3 m en el par de −1 a 0
- [ ] El residuo contra la 09 y la 08 en ese conjunto es menor que la tolerancia de task-38
