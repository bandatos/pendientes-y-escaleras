# Viaducto (Línea 2)

Carpeta `data/osm/l2-viaducto/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`); marco de la 01: rumbo 8,3° y ancla 19.4008868,-99.1368843. Medidas en ese marco. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-60`.

## Hechos propios

- **Área.** El contorno de OSM 217341597 («Metro Viaducto», pasa a «Viaducto») adoptado con la forma del KML a escuadra (ningún vértice movido más de 0,64 m). Las puntas norte y sur van en las esquinas viejas de OSM (2266139564, 2266139680, 2266139624, 2266139597) para no soltar las bardas 1322749521/22; queda un quiebre de 0,4 m en el muro poniente en los últimos 12 m del norte. La franja se ensancha entre los brazos (13,6 m contra 11,3 en las puntas), forma intencional del KML que se respeta.
- **Lóbulos hondos** de 13,1 × 26,1 m (oriente) y 13,1 × 26,4 m (poniente); ejes de los brazos en u 8,52 y −11,05.
- **Sin conectores**: E-01 no tiene peatonal a menos de 45 m y los tres candidatos de E-02 cruzaban la calzada o entraban al túnel 868793751.
- **Nodo de estación** 30385148, ya sobre el eje de la franja: movido 9,9 m a lo largo del andén, a u −1,27.

## Versiones

- 01, generada.
- 02, área a escuadra con las puntas de OSM, sin conector en E-02; la reproduce el bloque de la plantilla.
- 03, de Ricardo, cambios mínimos.

## Pendientes

Diff de la 03 y el nombre del contorno: en la tarea.
