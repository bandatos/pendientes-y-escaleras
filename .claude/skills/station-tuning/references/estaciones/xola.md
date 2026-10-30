# Xola (Línea 2)

Carpeta `data/osm/l2-xola/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`); marco de la 01: rumbo 8,7° y ancla 19.395197,-99.137804. Medidas en ese marco. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-59`.

## Hechos propios

- **Área.** El contorno de OSM 217340068 («Metro Xola», pasa a «Xola») toma la forma del KML. El KML tenía dos vértices invertidos que cruzaban el anillo; el bloque de la estación los cambia por el punto de cruce (4,35, −28,44).
- **Lóbulo poniente ancho** (20,9 × 13,7 m), el único de las hermanas: banco a lo largo de u con 3,43 m entre ejes, acortado a 9,51 m para dejar el pie a 3 m del muro de la punta. Lóbulo oriente hondo (13,2 × 21,2 m). Brazos corridos 9,9 m (ejes en u −8,33 y 1,55).
- **Entradas de OSM** 5160032503 (poniente, `wheelchair=yes`) y 5160032504 (oriente) enlazadas con `osm_node` + `relocate`. La regla del lóbulo ancho llevó la poniente 9,6 m a la esquina; Ricardo la recolocó en su 02.
- **Pasillo de Ricardo** en la mitad del pabellón opuesta a la escalera: el ejemplo de la regla de la L2.
- **Conectores** de la 01: E-01 a 5580858041 (4,1 m), E-02 a 8319476398 (5,0 m). Ricardo duda de la lógica en el lado poniente.
- **Nodo de estación** 30385145, ya a 2,7 m de la vía: se movió 2,9 m.
- **Tres elevadores** en el CSV crudo, fuera de esta edición.

## Versiones

- 01, generada; valida sin cambios.
- 02, de Ricardo: puerta poniente recolocada y un pasillo.

## Pendientes

Diff de la 02, banco de 9,5 o 12,2 m, lógica de conexión a la banqueta, índice de las escaleras del andén contra Miró: en la tarea.
