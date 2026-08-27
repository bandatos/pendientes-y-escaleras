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
