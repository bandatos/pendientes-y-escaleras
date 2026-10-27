# General Anaya (Línea 2)

Carpeta `data/osm/l2-general-anaya/`. Componente: superficie de la Calzada de Tlalpan (`componentes/tlalpan-surface.md`, plantilla `data/osm/templates/tlalpan-surface.json`); marco de la 01: rumbo 16,1° y ancla 19.3532707,-99.1450020. Medidas en ese marco (u a lo largo del andén, v transversal). La versión vigente es la más alta de la carpeta. La tarea que lleva la estación es `docs/tasks/task-43`.

## Hechos propios

- **Área.** Es el edificio de OSM 611635886, adoptado con la forma del KML: 35 vértices, de los que seis los comparte con vías y bardas en u ±85,6. Los 14 vértices viejos del edificio se borraron, confirmados sin uso en OSM en vivo.
- **Lóbulos asimétricos.** El de oriente mide 14,1 × 20,3 m y el de poniente 10,2 × 25,3 m; cada uno es el pabellón de su lado.
- **Puente.** Los dos brazos no son colineales y están corridos 19,6 m entre sí: 5,25 m de ancho con eje en u −12,79 y 4,41 m con eje en u 6,85. El puente peatonal de OSM 43763040, a 70 m del andén, no es de la estación y se quedó.
- **Andén** de 150 m, con la senda en v 1,02.
- **Calzada.** Sus caras quedan en v ±14 y OSM no tiene banquetas mapeadas ahí, así que los accesos no llevan conector. E-01 queda en (11,94, −34,62) y E-02 en (−19,15, 29,34).
- **Nodo de estación** a media distancia entre los ejes de los brazos (u ≈ −2,97), movido unos 14 m de donde estaba en OSM.
- **Escaleras del andén** de 9,11 m en la 06: llegada fija sobre la pasarela y pie corrido, el máximo que cabe con 1,5 m libres (estándar en `componentes/tlalpan-surface.md`). Pablo no las tocó; la plantilla todavía no las genera y viven en el bloque `local` de la estación.

## Versiones

- 01, generada desde la plantilla.
- 02, con lo aprendido de `portales-02-rick`.
- 03, de Pablo: alargó los bancos de acceso a 12,5 m.
- 04, endereza la deriva que dejó la edición de Pablo.
- 05, nodo de estación.
- 06, escaleras del andén de 9,11 m.
