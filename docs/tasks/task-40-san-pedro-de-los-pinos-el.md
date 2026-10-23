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

En `san-pedro-de-los-pinos-05-claude.osm` el tramo alto del pasillo de −1 poniente (way −80, nodos −75→−76, a u = 9) sale del área: un tramo de 2,81 m de largo queda fuera, hasta unos 1,04 m dentro de la muesca (las dos cifras miden cosas distintas y las dos valen: el largo fuera, de segcheck.py, y la profundidad, medida el 22 de octubre de 2026 en San Pedro regenerado contra el KML); atraviesa la muesca del KML entre v −41,5 y −44,3, cuyo fondo está en u = 7,88. Lo detectó `.claude/scratch/spp/segcheck.py`, que prueba tramos; el `check.py` de nodos no lo veía. La salida que se veía entonces era bajar ese tramo dentro del área (en la prueba de largos quedó en u = 7,35); Ricardo decidió después rellenar la muesca (abajo). Va en la siguiente versión de San Pedro, junto con lo que Ricardo diga al revisar la 05.

Pregunta para Ricardo, en la misma versión: la 05 abrió los codos de las cuatro salidas laterales a los radios de San Joaquín (senda 8,58 m, muros a ±3,25 m), más abiertos que los del KML, que tenía un exterior de unos 5,5 m y un interior de unos 3,6 m, no concéntricos. Con 6,5 m de ancho y codos concéntricos, conservar el radio interior del KML pone la senda a 6,9 m y el muro exterior a 10,15 m. ¿Se conserva el radio interior del KML (cambio mínimo al KML) o se queda el de San Joaquín? La alternativa estaba en el reporte del turno y no se le presentó.

## Decisiones del 22 de octubre de 2026 (sesión de San Antonio)

Ricardo decidió que la muesca es un error del KML: en la versión 06 de San Pedro se rellena en el área y el pasillo de −1 poniente vuelve a u = 9 (la plantilla ya lo trae así). Literal: «P5. 2» sobre las opciones «correr el pasillo a 7.85» / «tratar la muesca como un error del KML y rellenarla».

La misma versión 06 recoge además:

- Los aproches de la cascada como regla del componente: 1 m, y 1,5 m en el extremo lejano del segundo conjunto (Ricardo: «P4. 1»). La plantilla ya los trae; San Pedro se mueve.
- El tercer conjunto poniente corrido 2,25 m (Ricardo: «sí está perfecto»); las dos −1→0 y su pasillo se mueven 0,25 m respecto de la 05.
- El área se mete 0,98 m por los muros del pabellón poniente de OSM (way 476125317); recomendación del coordinador, sin respuesta de Ricardo: corregir el área en la 06 con la misma lógica que la muesca, porque el pabellón debe caber entero (Ricardo: «El pabellón entero»).
- Dos casi-encimados que la revisión con nivel 0 encontró en la 05: el centro del pabellón poniente (N-08) a 0,20 m de la reversible −2→−1 (lo corrige el 2,25) y la punta de una −2→−1 a 0,02 m del pasillo puerta→centro de E-01 (aceptado: Ricardo, «creo que aceptarlo es la respuesta»).
- El generador movió el nodo de OSM 4697711295 (esquina del pabellón oriente 476125318) 0,13 m para que quepa en el área; pendiente de que Ricardo lo revise (ver la tarea de San Antonio).

La pregunta de los radios de los codos sigue sin presentarse; la regla vigente es que el generador no reforma el área del KML y cada sesión decide (Ricardo: «que sea algo abierto a criterio de cada sesión, después si vemos patrones, lo ponemos como regla»).

## Criterios de aceptación

- [ ] La siguiente versión de San Pedro no tiene tramos fuera del área según segcheck.py
