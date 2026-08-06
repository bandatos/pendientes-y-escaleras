---
type: task
id: task-2
title: Decidir el despliegue público al mergear monorepo a main
state: open
date: 2026-08-06
owner: ricardo
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Decidir el despliegue público al mergear monorepo a main

GitHub Pages sirve hoy desde la raíz de `main` (build legacy) y el sitio vive en bandatos.org/pendientes-y-escaleras. En la rama `monorepo` el prototipo se movió a `prototype/`, así que mergear a main romperá el sitio salvo que se reconfigure Pages (por ejemplo, apuntándolo a otra carpeta o rama) o se despliegue `vue/` como reemplazo.

## Criterios de aceptación

- [ ] Está decidido qué sirve bandatos.org/pendientes-y-escaleras después del merge: el prototipo reubicado, el build de vue, u otra cosa
- [ ] GitHub Pages queda configurado en consecuencia
