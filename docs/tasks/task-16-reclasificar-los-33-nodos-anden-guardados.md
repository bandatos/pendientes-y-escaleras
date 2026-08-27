---
type: task
id: task-16
title: Reclasificar los 33 nodos «Andén» guardados como acceso
state: open
date: 2026-08-26
owner: ricardo
---

# Reclasificar los 33 nodos «Andén» guardados como acceso

33 de 445 stops con `location_type=2` son en realidad andenes (listado por estación en `data/analysis/osm-accesos-cruce.csv`, columna `notes`) (por ejemplo Universidad 10, Zaragoza 7, Constitución de 1917, Santa Anita), pero están guardados como acceso.

Decidir si deben ser nodo genérico u otra cosa, y corregir en Miro o en el parser según corresponda.

## Criterios de aceptación

- [ ] Está decidido qué tipo de nodo les corresponde a los 33 stops
- [ ] Los 33 quedan reclasificados en Miro o en el parser, según dónde se decidió corregir
