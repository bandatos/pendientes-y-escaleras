---
type: task
id: task-30
title: Servir el .osm por endpoint para el Remote Control de JOSM
state: open
date: 2026-09-02
owner: ai
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
related: ["[[adr-0002]]", "[[adr-0010]]", "[[task-26]]"]
---

# Servir el .osm por endpoint para el Remote Control de JOSM

[[adr-0002]] decidió que la app en Vue mande a JOSM `/load_and_zoom` y después `/import?url=` contra un endpoint que sirva el `.osm` de la estación. El generador de [[adr-0010]] escribe hoy archivos en `data/osm/` como paso intermedio y no existe endpoint ni task que lo pida. Falta: una vista en `api/` que corra `export_station_osm` (o lea el archivo generado) y responda `application/xml` con `upload=never`, sin etiquetas de traza salvo que se pidan; decidir si genera al vuelo o sirve archivos versionados; y recordar que en `/import?url=…` el parámetro `url` va al final. Depende de que los trazos de [[task-26]] se den por buenos.

## Criterios de aceptación

- [ ] `GET` de una estación devuelve el mismo XML que el comando, validado
- [ ] JOSM lo abre vía Remote Control desde el navegador
