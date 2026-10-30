---
type: task
id: task-68
title: "Generador: brazo sin lóbulo y umbral del barrido de lóbulos"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-58]]"]
---

# Generador: brazo sin lóbulo y umbral del barrido de lóbulos

En Villa de Cortés cada brazo del puente y su pabellón son un solo rectángulo del mismo ancho: `measure_arm` falla en el lado +v («llega al muro del fondo sin abrirse en un lóbulo») y en el −v el muro sur, que se abre 1,1 m en 33 m, le hace encontrar un lóbulo falso y clasificarlo ancho. La 01 salió de un envoltorio fuera del repo. Propuesta del trazador: si el barrido llega al fondo sin ensancharse, el lóbulo es el brazo entero, la orientación sigue la regla del lado largo ([[adr-0017]]) y la puerta va en un muro lateral elegible por estación; medir el ensanche contra la recta de los muros del brazo, no contra su ancho inicial; y agregar `arms` a `PATCH_DICT_SECTIONS` para que el bloque de estación pueda fijarlo.

**Antes de implementar, la regla es de Ricardo** (P3 de Villa de Cortés, sin respuesta en texto): su lectura del lado poniente («las escaleras son "paralelas a las vías"» y una ampliación con los torniquetes sobre la avenida) contradice el banco sobre el eje. Se decide con el diff de [[task-58]] y la visita de [[task-63]].

## Criterios de aceptación

- [ ] Ricardo decidió la regla del brazo sin lóbulo
- [ ] Villa de Cortés se genera con el command, sin envoltorio
- [ ] Un muro levemente oblicuo no se confunde con un lóbulo
- [ ] Prueba en test_arms.py
