---
type: task
id: task-45
title: "Plantilla de Tlalpan: vestíbulo longitudinal de nivel 1 y escaleras del andén en serie"
state: open
date: 2026-10-27
owner: ai
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
related: ["[[task-26]]", "[[task-38]]"]
---

# Plantilla de Tlalpan: vestíbulo longitudinal de nivel 1 y escaleras del andén en serie

Ricardo decidió el 27 de octubre de 2026 que el vestíbulo de nivel 1 del componente `tlalpan-surface` es el de su edición de Portales (`portales-02-rick`), injertado hoy en `portales-05-claude.osm`, y no la losa transversal con abanico que la plantilla genera. Hay que llevarlo a `data/osm/templates/tlalpan-surface.json` y al generador.

Lo que debe expresar la plantilla, con los números del turno de Portales 05 (scripts en `.claude/scratch/portales/`, marco de la 01; J es el eje del brazo poniente):

- Pasarela longitudinal (`footway`, `indoor`, `bridge=yes`, `layer=1`, `level=1`) en v = senda + 1,40, de J + 18,38 a J − 17,88 (36,26 m), que reemplaza la losa transversal de `extra_ways`.
- Torniquetes sobre la pasarela en J + 4,02 y J − 4,19, en vez de sobre los pasillos del puente (`turnstile.distance 6`).
- Nodo de encuentro de los dos brazos sobre la pasarela, en el eje del brazo poniente (Portales) o donde quede entre torniquetes: regla general por decidir (en General Anaya los brazos están corridos 19,6 m).
- Brazo oriente: baja por su eje hasta pasarela + 2,35, cruza en transversal hasta J y baja al nodo de encuentro.
- Escaleras del andén: dos fijas por lado, en serie, diagonales, llegadas sobre la pasarela en J + 18,38, J + 7,93, J − 6,34 y J − 17,88 (simetrizadas ±18,1 y ±7,1), pie sobre la senda; largo 12,5 m (el de las de acceso) o el máximo que deje 1,5 m en u entre el pie de la interior y la llegada de la exterior. En General Anaya salen 9,11 m las cuatro; en Portales 12,5 las exteriores y 9,06 / 10,14 las interiores.
- Prosa ya escrita en `references/componentes/tlalpan-surface.md`; el comentario de `station_node` («N-01 ocupa ese punto») pierde su motivo.

Residuos que hoy deja la plantilla y que esta task debe bajar: General Anaya banco poniente dv +0,50 (Pablo lo dejó a 3,52 m del fondo), andén du −0,46, losa en dos ways; Portales con el área de Pablo (opción tomada: el área de la 03 de Pablo va en el bloque de estación) banco oriente a lo largo de u en un lóbulo de 25,8 m, residuo de 10 a 14 m contra la regla del eje del brazo: Ricardo debe decir si es excepción de estación.

## Criterios de aceptación

- [ ] Regenerar General Anaya con --out contra la 06 y Portales contra la 05 da residuo por elemento menor que la tolerancia acordada en task-38, escaleras del andén incluidas
- [ ] El bloque `local` de General Anaya ya no lleva las escaleras del andén ni la losa

## Notas de trabajo

- 27 de octubre de 2026 (madrugada, hallazgo del crítico, hipótesis sin verificar en imagen): los polígonos de andén publicados de General Anaya y Portales (`railway=platform`, de 10 a 13 m de ancho) contienen las dos vías de OSM a lo largo de los 150 m. O las vías de OSM están corridas, o el andén es demasiado ancho; viene del hecho «el andén ocupa la franja entera del KML». Verificar sobre Esri antes de tocar la plantilla; si el andén es el que sobra, es un cambio de esta task y una corrección en OSM contra ids del servidor.
