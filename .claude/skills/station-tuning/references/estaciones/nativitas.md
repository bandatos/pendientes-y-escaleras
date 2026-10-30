# Nativitas (Línea 2)

Carpeta `data/osm/l2-nativitas/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`); marco de la 01: rumbo 8,5° y ancla 19.3795464,-99.1401985. Medidas en ese marco (u a lo largo del andén, positivo al norte; v transversal, positivo al oriente). La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-57`.

## Hechos propios

- **Área.** Es el edificio de OSM 531159102 («Nativitas»), adoptado con la forma del KML. Traía `layer=2`, que Ricardo decidió quitar porque el contorno incluye los pabellones a nivel de calle.
- **Lóbulos hondos** los dos: oriente 10,7 × 26,6 m (eje del brazo en u −9,84), poniente 13,8 × 26,5 m (eje en u −0,01); brazos corridos 9,8 m.
- **Pabellón poniente y jardín.** El KML mete el fondo del lóbulo unos 7 m en el jardín de OSM 1275816500 (`landuse=grass`); un árbol grande hace parecer el jardín más grande de lo que es, y Ricardo acortó el área en su 03. Los nodos 5156348365/66 del edificio viejo los usa ese jardín y no se dan de baja.
- **Entrada de OSM 5156348346** adoptada como E-01 (`osm_node` + `relocate`), movida 1,06 m. E-01 lleva un connector de 6,5 m a la punta 554206757 de la banqueta 864674193; E-02 va sin conector (la acera oriente no está mapeada).
- **Puente peatonal de OSM 43763069** borrado (cae sobre los ejes de los brazos); hoy a mano, con script.
- **Nodo de estación** 30385133 movido 11,9 m a media distancia entre los ejes de los brazos (u −4,92).

## Versiones

- 01, generada; falla la validación por la entrada suelta.
- 02, entrada adoptada, puente borrado, bajas bloqueadas conservadas.
- 03, de Ricardo: área acortada en el pabellón poniente.

## Pendientes

Diff de la 03 contra la 02, quitar `layer=2`, trazo para la vuelta en los dos bancos: en la tarea.
