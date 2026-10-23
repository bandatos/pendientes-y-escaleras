---
type: task
id: task-40
title: "San Pedro de los Pinos: el pasillo de −1 poniente sale del área por una muesca del KML"
state: open
date: 2026-10-22
owner: ai
parent: "[[task-26]]"
source: ["[[2026-10-22-sesion-ciclo-de-afinacion-y-san-joaquin]]"]
---

# San Pedro de los Pinos: el pasillo de −1 poniente sale del área por una muesca del KML

En `san-pedro-de-los-pinos-05-claude.osm` el tramo alto del pasillo de −1 poniente (way −80, nodos −75→−76, a u = 9) sale 2,81 m del área: atraviesa la muesca del KML entre v −41,5 y −44,3, cuyo fondo está en u = 7,88. Lo detectó `.claude/scratch/spp/segcheck.py`, que prueba tramos; el `check.py` de nodos no lo veía. La única salida es bajar ese tramo dentro del área (en la prueba de largos quedó en u = 7,35). Va en la siguiente versión de San Pedro, junto con lo que Ricardo diga al revisar la 05.

Pregunta para Ricardo, en la misma versión: la 05 abrió los codos de las cuatro salidas laterales a los radios de San Joaquín (senda 8,58 m, muros a ±3,25 m), más abiertos que los del KML, que tenía un exterior de unos 5,5 m y un interior de unos 3,6 m, no concéntricos. Con 6,5 m de ancho y codos concéntricos, conservar el radio interior del KML pone la senda a 6,9 m y el muro exterior a 10,15 m. ¿Se conserva el radio interior del KML (cambio mínimo al KML) o se queda el de San Joaquín? La alternativa estaba en el reporte del turno y no se le presentó.

## Criterios de aceptación

- [ ] La siguiente versión de San Pedro no tiene tramos fuera del área según segcheck.py
