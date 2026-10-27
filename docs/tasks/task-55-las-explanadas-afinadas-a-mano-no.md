---
type: task
id: task-55
title: Las explanadas afinadas a mano no sobreviven a una regeneración
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-38]]", "[[task-48]]", "[[task-54]]"]
---

# Las explanadas afinadas a mano no sobreviven a una regeneración

Lo que destapó el jardín poniente de San Pedro ([[task-54]]): Ricardo dibujó la forma real de las dos explanadas en la 02-rick y la 03-rick, la 04 regenerada las perdió sin que nadie lo notara, y el rectángulo del generador se publicó el 27 de octubre de 2026 (changeset 191086111) invadiendo una escuela y una banqueta. Cuatro huecos, cada uno con su arreglo:

1. **Plantilla.** El generador solo dibuja un cuadro por explanada (`plaza_half`) y el bloque por estación no puede guardar su geometría. O el bloque admite la geometría de cada explanada en el marco local (como ya admite `area`), o el skill `station-tuning` exige comparar toda la superficie (explanadas, edificios, entradas) contra la última `-rick` al regenerar, no solo los trazos del grafo.
2. **Imagen.** `compose_station_imagery` dibuja las explanadas, edificios y entradas del contexto de OSM, pero no los del `.osm` que recibe; por eso la pérdida fue invisible de la 04 a la 08. Debe dibujar también los nuestros.
3. **Validador.** Avisar cuando una explanada nuestra se encima con un edificio de OSM o cruza una banqueta sin nodo compartido.
4. **Publicación.** `publish_station_osm` debe negarse, o al menos avisar, cuando una versión anterior de la estación ya tiene changeset: a partir de ahí toda corrección va contra ids del servidor, no contra una copia nueva con ids negativos.

## Criterios de aceptación

- [ ] Regenerar San Pedro reproduce las dos explanadas de la 03-rick o el skill obliga a compararlas antes de aprobar
- [ ] `compose_station_imagery` muestra explanadas, edificios y entradas del `.osm` recibido
- [ ] El validador avisa de una explanada sobre un edificio de OSM o cruzando una banqueta sin nodo compartido, con test
- [ ] `publish_station_osm` avisa o se niega cuando la estación ya tiene una versión publicada
