---
type: task
id: task-50
title: Normalizar los fines de línea de los .osm que vienen de Windows
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
---

# Normalizar los fines de línea de los .osm que vienen de Windows

Los seis archivos que Pablo devolvió el 26 de octubre de 2026 vienen con CRLF; las versiones que los tracers construyen editando su texto los conservan, y git avisa en cada commit que los normalizará a LF. No es error, pero el primer diff que alguien abra sobre ellos verá líneas enteras cambiadas. Decidir si se normalizan al ingresar (en el paso de copia a `<slug>-NN-pablo.osm`) o con `.gitattributes`, y aplicarlo a los que ya están.

## Criterios de aceptación

- [ ] Ningún `.osm` bajo `data/osm/` tiene CRLF y git no avisa al commitear
