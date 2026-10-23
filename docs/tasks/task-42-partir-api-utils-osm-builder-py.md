---
type: task
id: task-42
title: Partir api/utils/osm/builder.py, que pasa de 2 300 líneas
state: open
date: 2026-10-23
owner: ai
source: ["[[2026-10-22-sesion-san-antonio-y-aprendizaje-de-plantilla]]"]
related: ["[[task-38]]"]
---

# Partir api/utils/osm/builder.py, que pasa de 2 300 líneas

`builder.py` creció con el bloque por estación, la tolerancia a pathways sin plantilla, la regla del edificio que cabe en el área y el encaje por lado, y pasa de 2 300 líneas. Propuesta del ejecutor del 22 de octubre de 2026, no discutida con Ricardo: partirlo por responsabilidad (área, bancos, encaje, accesos y edificios de OSM, reporte) sin cambiar comportamiento. Conviene hacerlo junto con la partición de la plantilla en componentes de [[task-38]].

## Criterios de aceptación

- [ ] Ningún módulo de `api/utils/osm/` pasa de unas 800 líneas
- [ ] San Pedro, San Joaquín, San Antonio y Portales regeneran byte a byte iguales antes y después
- [ ] Los tests de `utils/osm` pasan
