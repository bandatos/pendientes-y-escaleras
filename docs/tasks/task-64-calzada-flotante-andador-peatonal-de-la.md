---
type: task
id: task-64
title: "Calzada Flotante: andador peatonal de la salida sur de San Antonio Abad al nivel 1 de la plataforma norte de Chabacano"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-21]]", "[[task-61]]"]
---

# Calzada Flotante: andador peatonal de la salida sur de San Antonio Abad al nivel 1 de la plataforma norte de Chabacano

Sesión aparte, por decisión de Ricardo («preferiría guardarlo como tarea con todas las especificaciones que ya señalé»). Lo que dijo de la obra, textual: «es un "andador peatonal" por encima de las vías del tren (usa todo el ancho del camellón) y conecta la plataforma superior de chabacano, la parte norte (level 1 de la Línea 2) con la salida sur de San Antonio Abad, no tengo claridad si alguien de OSM ya mapeó ese andador, pero creo que no... Y no tengo claro cómo hacer ese andador peatonal sin poner los puentes de acceso (a lo largo de su recorrido)».

## Plan acordado

Ricardo, sobre la recomendación (fuentes primero; si no aclaran, publicar el andador principal con `fixme`): «P9. Completamente de acuerdo, pero algo que me preocupa es que esta sesión ya se está llenando su ventana de contexto, entonces preferiría guardarlo como tarea». Lo que se publica sigue abierto (paso 2).

1. Antes de ir a campo, agotar en este orden: búsqueda web con un explorador (planos de proyecto, renders, notas de prensa con los accesos intermedios, una imagen aérea posterior a febrero de 2025); la consulta en vivo a OSM sobre el camellón entre las dos estaciones; la imagen Bing dentro de JOSM, por si es más reciente que Esri.
2. Si nada aclara los accesos intermedios: dibujar solo el andador principal, un `footway` con `bridge=yes`, `layer=1`, `level=1` por el eje del camellón, del acceso sur de San Antonio Abad (E-03, que Ricardo ya movió al sur del área en la 03, [[task-61]]) hasta el nivel 1 de la plataforma norte de Chabacano, con `fixme` de que faltan sus accesos intermedios. Ricardo decide si se publica así o se espera la visita.
3. Toca dos estaciones: San Antonio Abad (E-03 y su pasillo al vestíbulo) y la salida de Chabacano, que es otra familia y se trabaja en esa sesión solo en lo que toca al andador.

## Datos

- En la imagen Esri del 24 de febrero de 2025 el camellón al sur de San Antonio Abad está abierto, sin huella de la obra; OSM no tiene nada del andador.
- En el tablero de Miró, el conector 3458764677010013290 cruza de frame entre San Antonio Abad y Chabacano (extremos 3458764677009670141, que es E-03 de San Antonio Abad, y 3458764677009904492); el importador no lo resuelve ([[task-21]]).
- La plantilla no tiene una pieza para un acceso de nivel 1 que llega directo al vestíbulo: el generador lo ubica en el centro de sus vecinos y lo une a lo que tenga más cerca.

## Criterios de aceptación

- [ ] Fuentes previas al campo agotadas y su resultado anotado
- [ ] Ricardo decidió si se publica el andador principal con `fixme` o se espera la visita
- [ ] Si se publica: el andador trazado en San Antonio Abad y en la salida de Chabacano
