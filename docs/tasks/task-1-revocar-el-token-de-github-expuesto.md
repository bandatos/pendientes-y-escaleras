---
type: task
id: task-1
title: Revocar el token de GitHub expuesto y purgarlo de la historia de main
state: open
date: 2026-08-06
owner: ricardo
source: ["[[2026-08-05-integracion-del-monorepo]]"]
---

# Revocar el token de GitHub expuesto y purgarlo de la historia de main

`token.txt` contenía un Personal Access Token clásico de GitHub, trackeado desde el commit «Add files via upload» en un repo público. El archivo ya se eliminó del árbol en la rama `monorepo`, pero el token sigue legible en la historia de `main`. GitHub suele auto-revocar tokens detectados por secret scanning, pero no está confirmado. Purgar main implica reescribir historia publicada (git-filter-repo + push forzado); una alternativa es que la rama `monorepo` reemplace a `main` con purga incluida cuando se publique.

## Criterios de aceptación

- [ ] El PAT (ghp_…) que vivía en token.txt está revocado en GitHub o confirmado como inactivo
- [ ] Se decidió y ejecutó (o descartó explícitamente) la purga de la historia de main, que es pública
