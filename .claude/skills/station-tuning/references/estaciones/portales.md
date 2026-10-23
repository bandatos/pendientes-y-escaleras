# Portales (Línea 2)

Carpeta `data/osm/l2-portales/`. Estación de superficie con andén central: no comparte componentes con la Línea 7 y usa la plantilla `data/osm/templates/tlalpan-surface.json`. Las reglas del nodo de estación y de las salidas laterales de la Línea 7 no le aplican.

## Hechos propios

- El andén ocupa la franja entera del KML (unos 13 m de ancho) y mide 150 m centrados en la franja, con las puntas dentro del área; su senda va por el eje.
- Las escaleras nacen del andén y van en abanico con geometría propia; no forman conjuntos paralelos.
- El vestíbulo es un puente sobre las vías, cuya losa se dibuja como pieza extra de la plantilla.
- OSM no tiene pabellones: se dibujan cuadrados de 14 y 13 m, la medida de los lóbulos del KML.
- El área no tiene islas: es el edificio de estación que OSM ya tenía (way 1387762582), con sus etiquetas intactas y la geometría del KML.
- Dónde va su nodo de estación está abierto: el generador lo mueve 14,5 m y Ricardo no lo movió en su edición de septiembre.
