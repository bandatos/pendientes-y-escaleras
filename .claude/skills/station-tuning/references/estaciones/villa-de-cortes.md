# Villa de Cortés (Línea 2)

Carpeta `data/osm/l2-villa-de-cortes/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`); marco de la 01: rumbo 8,3° y ancla 19.3875836,-99.1389625, sin `--mirror`. Medidas en ese marco. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-58`; la visita de campo, `docs/tasks/task-63`.

## Hechos propios

- **Brazo sin lóbulo.** Cada lado es un solo rectángulo, puente y pabellón del mismo ancho (techo blanco el puente, rojo el pabellón). El generador no lo mide y la 01 salió de un envoltorio fuera del repo; la regla está por decidir (`docs/tasks/task-68`).
- **Lado poniente, lectura de Ricardo:** las escaleras van paralelas a las vías y una ampliación sobre la avenida aloja probablemente los torniquetes del pasillo del puente. Remodelación reciente: **no se publica sin visita física**.
- **Área.** El contorno de OSM 217340069 («Metro Villa de Cortés», pasa a «Villa de Cortés») lo redibujó otro mapeador en marzo de 2026 sobre Bing, corrido 3 a 12 m respecto de Esri y del KML. Los ejes de los dos brazos casi coinciden (u −4,33 y −3,84): el vestíbulo va en u −4,09.
- **Entradas de OSM** 13653654624 y 13648121868 adoptadas en la 02 con movimientos de 14,4 y 12,2 m; el edificio 1488931042 (`building:levels=8`) y el puente 221926316 dados de baja a mano en la 02.
- **Franja** de 13,98 m en el KML contra 11–11,5 m en la imagen y en OSM; no se tocó.

## Versiones

- 01, generada con el envoltorio del brazo sin lóbulo.
- 02, bajas a mano del puente y del edificio.
- 03, de Ricardo, con muchos cambios.

## Pendientes

Diff de la 03, las preguntas P3 y P5 sin respuesta en texto, el nombre del contorno, la visita: en la tarea.
