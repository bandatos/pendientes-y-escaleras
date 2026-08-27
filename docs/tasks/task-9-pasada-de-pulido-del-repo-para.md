---
type: task
id: task-9
title: Pasada de pulido del repo para quienes vienen después
state: open
date: 2026-08-26
owner: ai
---

# Pasada de pulido del repo para quienes vienen después

Hacer el repo replicable de principio a fin por cualquier colaborador nuevo, de cara a construir la herramienta de mapeo a OpenStreetMap.

- README y CLAUDE.md al día: el `CLAUDE.md` de `api/` dice que hay que comentar `django.contrib.postgres` a mano y ya es condicional en el código — corregir la instrucción.
- Documentar los pasos de restauración de la base desde `~/databases/`.
- Completar `.env.template`: faltan `MIRO_BOARD_ID` y las variables de AWS (hecho el 2026-08-26); `vue/.env.template` creado con las 6 claves (verificar que sigan al día).
- Exponer `Pathway` en la API (`PathwaySerializer` existe pero no está registrado en ningún router) y `stop_lat`/`stop_lon` en `StopCatSerializer`: el módulo de mapeo OSM los necesita.
- Documentar los comandos de importación en el orden correcto.
- Ninguna corrección de datos debe vivir solo en la base: todo por comando, migración de datos o CSV de origen.

## Criterios de aceptación

- [ ] README y CLAUDE.md de `api/` no contienen instrucciones obsoletas
- [ ] Existen pasos documentados para restaurar la base desde `~/databases/`
- [ ] `api/.env.template` y `vue/.env.template` incluyen todas las claves en uso
- [ ] La API expone `Pathway` y las coordenadas de `Stop`
- [ ] Los comandos de importación están documentados en el orden en que deben correrse
- [ ] Se verificó que ninguna corrección de datos conocida vive solo en la base
