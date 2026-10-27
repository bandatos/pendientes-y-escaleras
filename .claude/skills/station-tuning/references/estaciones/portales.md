# Portales (Línea 2)

Carpeta `data/osm/l2-portales/`. Estación de superficie con andén central: no comparte componentes con la Línea 7 y usa la plantilla `data/osm/templates/tlalpan-surface.json`. Las reglas del nodo de estación y de las salidas laterales de la Línea 7 no le aplican. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-26`; la plantilla del vestíbulo longitudinal, `docs/tasks/task-45`.

## Hechos propios

- El andén ocupa la franja entera del KML (unos 13 m de ancho) y mide 150 m centrados en la franja, con las puntas dentro del área; su senda va por el eje.
- Las escaleras del andén son dos fijas por lado, en serie y en diagonal, del pie sobre la senda a la pasarela longitudinal de nivel 1: miden 12,5 / 9,06 / 10,14 / 12,5 m (las exteriores 12,5, las interiores lo que cabe). No forman conjuntos paralelos.
- El vestíbulo es un puente sobre las vías; sobre el andén, una pasarela longitudinal de nivel 1 paralela a las vías, con los torniquetes sobre ella (la de `portales-02-rick`, injertada en la 05), no la losa transversal que la plantilla todavía genera (task-45).
- OSM no tiene pabellones. La 01 los dibujó como cuadrados de 14 y 13 m; hoy el pabellón es el lóbulo del área, con una sola puerta hacia la Calzada y sin `building` propio: Ricardo quitó los dos `building=yes` (`componentes/tlalpan-surface.md`).
- El área no tiene islas: es el edificio de estación que OSM ya tenía (way 1387762582), con sus etiquetas intactas y la geometría del KML.
- Nodo de estación en u −5,80: a media distancia entre los ejes de los brazos (regla del componente), corrido sobre el eje por el despeje de 1 m del vestíbulo que la regla conserva.

## Versiones

- 01, generada desde la plantilla.
- 02, de Ricardo.
- 03, de Pablo.
- 04, integra lo de Pablo.
- 05, pasarela longitudinal de la 02 injertada.
