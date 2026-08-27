---
type: task
id: task-15
title: "Piloto de LLM para borradores: niveles y nombres de accesos"
state: open
date: 2026-08-26
owner: ricardo
---

# Piloto de LLM para borradores: niveles y nombres de accesos

Usos propuestos: inferir el nivel desde el nombre del nodo; cruzar nombres de accesos entre la base, Wikipedia y OSM; opcionalmente, borrador de layout.

Modelos a probar: Gemini 3.7 Flash, Gemini 3.5 Flash-Lite y GLM 5.3 Flash (falta la API key de GLM). Medir el costo por estación.

Reusar el patrón de `~/dev/ibero/ocsa` (`RequestGemini`, salida estructurada con Pydantic).

No hay benchmarks públicos de modelos baratos en tareas espaciales: el piloto es la medición misma.

## Criterios de aceptación

- [ ] Se corrió el piloto con al menos dos de los tres modelos sobre una muestra de estaciones
- [ ] Se midió el costo por estación de cada modelo probado
- [ ] Está documentado si alguno de los usos (nivel, cruce de nombres, layout) da resultados usables como borrador
