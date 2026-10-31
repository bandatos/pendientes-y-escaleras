---
type: decision
id: adr-0020
title: Un way que cruza el contorno de un andén a su mismo nivel comparte nodo con el contorno; a otro nivel, no
state: accepted
date: 2026-10-30
origin: ricardo
deliberation: confirmed
rationale: recorded
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
affects: ["api/utils/osm/builder.py", "api/utils/osm/validate.py", "data/osm/README.md"]
related: ["[[adr-0019]]", "[[adr-0016]]", "[[task-75]]"]
---

# Un way que cruza el contorno de un andén a su mismo nivel comparte nodo con el contorno; a otro nivel, no

## Contexto y planteamiento del problema

El andén es un polígono (`railway=platform` + `area=yes`), dentro corre la senda, y a la senda llegan pasillos y escaleras desde fuera. En los archivos publicados de L7 los pasillos de −3 atravesaban el borde del polígono del andén de −3 «por el aire», sin nodo común. En OSM dos cosas que se tocan comparten nodo; sin él, el pasillo y el andén no se tocan, como un puente sobre un río, y el polígono queda a medias aunque el ruteo funcione por la senda. JOSM callaba porque el andén llevaba `layer=-3` y el pasillo no; con [[adr-0019]] los dos coinciden en `level` y `layer`, y JOSM marca entre 4 y 6 cruces por estación de L7 (iD no evalúa áreas de railway). En L2 no pasa: lo único que cruza el contorno del andén de nivel 0 son los pasillos del puente de nivel 1, y ese cruce sin nodo es correcto.

## Criterios de decisión

- Topología correcta: lo que se toca comparte nodo; lo que pasa por encima o por debajo, no.
- Una sola regla para el generador, y aviso cuando un archivo editado a mano la rompe.
- Reutilizar el mecanismo que ya existía para el anillo de la explanada.

## Decisión

Un way de circulación de un solo nivel que cruza el contorno de un andén de ese mismo nivel comparte con él un nodo en el punto de cruce, insertado en ambos ways; si el cruce cae a menos de 0,3 m (la distancia mínima de la validación) de un vértice de cualquiera de los dos, se reutiliza ese vértice. Un way de otro nivel o de dos niveles (pasillo de −4 bajo el andén de −3, escalera `-4;-3`, puente de nivel 1 sobre andén de 0) cruza sin nodo. La senda del andén corre por dentro y no se toca; si cruza su anillo, se avisa. Implementado en `_join_platform_crossings` (builder) y como aviso en `unjoined_platform_crossings` (validate). Ricardo lo confirmó como regla general para todas las estaciones.

## Alternativas descartadas

- Aceptar los avisos de JOSM como ruido: el dato ya estaba incompleto; el `layer` solo lo sacó a la luz.
- Mirar también andenes adoptados de OSM (`action=modify`): hoy todos los andenes los dibuja el generador; queda como extensión si algún día se adopta uno.

## Consecuencias

- En lo ya publicado: 4, 6, 6 y 6 nodos nuevos en Polanco, San Antonio, San Joaquín y San Pedro, que viajan en las mismas versiones que el `layer` ([[task-75]]). En San Pedro cuatro de ellos quedan a entre 0,5 y 0,7 m de un vértice existente, por encima del umbral; se dejan.
- Regenerar Portales y General Anaya no cambia un byte.
