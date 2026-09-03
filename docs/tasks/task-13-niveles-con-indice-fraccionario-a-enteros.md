---
type: task
id: task-13
title: Niveles con índice fraccionario a enteros
state: open
date: 2026-08-26
owner: ricardo
---

# Niveles con índice fraccionario a enteros

En OSM `level` debe ser un entero consecutivo; lo señalizado en el sitio va en `level:ref`. Tacubaya trae «Mezzanine −2.5» y «−1.5» en nombres de nodos, lo cual no es exportable tal cual.

Definir la política de renumeración (cómo insertar niveles fraccionarios en la secuencia entera) y aplicarla en Miro y en la base antes de exportar a OSM.

## Criterios de aceptación

- [ ] Está definida la política de renumeración de niveles fraccionarios a enteros consecutivos
- [ ] Tacubaya está renumerada en Miro y en la base según esa política

## Notas de trabajo

- 2 de septiembre de 2026 (tarde, [[2026-09-02-sesion-integracion-osm-y-niveles]]): decidido: un `level_index` no entero detiene la exportación con error nombrando el stop, en vez de redondear (Tacubaya −2.5 y −1.5 caían ambos en −2). Tacubaya la renumera Ricardo. Los mezzanines intermedios de Mixcoac y Chabacano no reciben nivel propio, decidido ([[task-31]]). Corregido de paso el parser de niveles de Miró: «Nivel Andenes superficie 0» no se leía; el detalle está en el registro de la sesión.
