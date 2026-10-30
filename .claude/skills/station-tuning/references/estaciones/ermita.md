# Ermita (Línea 2)

Carpeta `data/osm/l2-ermita/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`). Estación de correspondencia con la Línea 12: sus stops cuelgan del padre de L12, así que se exporta como `020L12-ERMITA --line L2` y el bloque de la plantilla se indexa por `020L12-ERMITA`. Marco de la 01: rumbo 9,0° (promedio ponderado de los bordes largos del área; no hay rumbo de shape) y ancla 19.361969,-99.1429123. Medidas en ese marco. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-62`.

## Hechos propios

- **Nodo de estación** 12679525779: es el nodo único de la correspondencia, en L12, miembro del `stop_area` «Ermita (Linea 2)». No se mueve (`station_node: null` en el bloque).
- **Área.** El contorno de OSM 526205288 («Ermita L2», `layer=2`) toma la forma del KML. Decidido para la 03 (en la 02 todavía hay un hueco de 6 m): colinda con el área de L12 (way 1367187879) compartiendo los nodos 12661040766 y 12661040767, sin hueco, aunque se aparte unos 6 m del KML.
- **Pasillo de trasbordo de nivel 1**: puente sobre las vías por todo el ancho del camellón, del extremo sur del vestíbulo hasta donde la franja se abre al cuerpo de L12 (unos 206 m). En la 02 es un way nuevo; decidido para la 03: se adopta el way de OSM 536525798 «Transbordo Intermodal Metro Ermita», reetiquetado de túnel a `bridge=yes`, `layer=1`, `level=1`, y el túnel 536525793 de nivel −1 se da de baja.
- **Lóbulos hondos** de 10,5 × 22,9 m (oriente) y 11,3 × 26,2 m (poniente); ejes de los brazos en u −13,96 y −3,30.
- **Entradas de OSM** 5197238662 (E-01, `wheelchair=yes`) y 5197238663 (E-02) adoptadas a mano, con conectores perpendiculares soldados a mitad de banqueta (1367360654 y 1367360653).
- **Puente peatonal de OSM 43763058** y su escalera 1304926070 dados de baja.
- **Un elevador** de L2 en el CSV crudo, fuera de esta edición.

## Versiones

- 01, generada; falla la validación por el puente viejo.
- 02, nodo de estación devuelto a su lugar, entradas adoptadas, puente borrado, pasillo de trasbordo nuevo.

## Pendientes

La 03 con el trasbordo de OSM adoptado y el área estirada a L12: en la tarea.
