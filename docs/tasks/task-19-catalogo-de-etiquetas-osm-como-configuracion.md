---
type: task
id: task-19
title: Catálogo de etiquetas OSM como configuración del generador
state: open
date: 2026-08-26
owner: ai
related: ["[[adr-0004]]", "[[2026-08-26-alineacion-catalogos-osm]]"]
---

# Catálogo de etiquetas OSM como configuración del generador

Materializar la alineación de [[adr-0004]] y de la referencia [[2026-08-26-alineacion-catalogos-osm]] como archivo de configuración versionado del generador `.osm`: tabla tag ↔ campo ↔ valor por concepto (jerarquía de estación, niveles, los siete modos de pathway, accesos, accesibilidad, andenes, identificadores), incluyendo los conceptos que solo tiene un lado (marcados como tales). Sin migración de esquema: Ricardo prefirió configuración versionada sobre tabla de catálogo en la base.

## Criterios de aceptación

- [ ] Existe un archivo de configuración versionado que cubre todos los conceptos de la referencia, con los tres niveles de autoridad (wiki/aprobado/de facto) anotados
- [ ] El generador lee de ese archivo y no tiene etiquetas OSM escritas en el código
- [ ] Los conceptos de un solo lado (location_type 3 y 4, is_double, traversal_time, signposted_as, destination_sign) están listados con su tratamiento

## Notas de trabajo

- 2 de septiembre de 2026: el catálogo ya existe como código en `api/utils/osm/tags.py`, único módulo del generador que escribe etiquetas ([[adr-0010]]); es la semilla del archivo de configuración. Falta moverlo a un archivo versionado con los niveles de autoridad y sumar `gtfs:*` ([[task-27]]). Al mover el catálogo a configuración, conciliar [[adr-0004]] con [[adr-0010]]: el segundo enmienda cuatro viñetas del primero sin reemplazarlo, y ambos siguen aceptados.
