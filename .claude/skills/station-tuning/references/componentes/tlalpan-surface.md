# Componente: superficie de la Calzada de Tlalpan (Línea 2)

Andén central en el camellón de la Calzada de Tlalpan, vestíbulo-puente en el nivel +1 que cruza sobre las vías y la Calzada, y un pabellón de acceso en cada acera. Lo comparten Portales y General Anaya, y lo heredan las hermanas de superficie de la Línea 2 que nombra la plantilla. Su JSON es `data/osm/templates/tlalpan-surface.json`, entero: el andén `P-01`, los nodos del puente y de los accesos (`N-01` a `N-05`, `E-01`, `E-02`), los bancos de acceso (`banks.acceso-oriente` y `banks.acceso-poniente`), la losa del puente en `extra_ways` y `station_node`. Las reglas de abajo nacieron de General Anaya (cierre del 26 de octubre de 2026) con lo que Pablo y Ricardo dejaron en Portales; dónde vive cada número en el JSON lo dice la plantilla, y donde esta prosa y el JSON choquen, se corrige uno de los dos.

## Lo que rige

- **El pabellón es el lóbulo del área.** Cada acceso es el lóbulo del KML que sale de la franja hacia su acera, no un cuadrado inventado: los cuadrados de 14 y 13 m de la 01 de Portales ya no se dibujan. Los lóbulos no tienen por qué ser simétricos (en General Anaya, 14,1 × 20,3 m al oriente y 10,2 × 25,3 m al poniente).
- **Una sola puerta por pabellón, hacia la Calzada.** Regla de Pablo, textual: «En los casos donde ya exista pasillo superior, eliminar o reemplazar el objeto. Generalmente solo existe un acceso por edificio de estación y éste está frente a la vía Calzada de Tlalpan». La primera mitad es la regla general del puente peatonal de OSM (`general.md`, «Lo que viene de OSM»): se borra o se reemplaza solo si cae sobre el área.
- **Banco de acceso.** Dos escaleras paralelas a 1,8 m entre ejes (la separación general) desde el pabellón hasta la cabecera del puente. El banco va en el eje del brazo del puente al que sube, con el pie a 3 m del fondo del pabellón, y la circulación dentro del pabellón, de la puerta al pie del banco, va en U. Largo de 12,5 m, provisional: es el que dejó Pablo en General Anaya y falta confirmarlo en otra estación. Los números viven en `banks.acceso-oriente` y `banks.acceso-poniente`.
- **Puente y nodo de estación desde los brazos reales.** Los dos brazos del puente no son colineales ni miden lo mismo; cada uno se lee de su pasillo del KML. Las cabeceras del puente (donde llega cada banco) y el nodo `railway=station` se derivan de los ejes reales de los brazos, no de una `u` escrita a mano: el nodo de estación va sobre el eje de la franja, a media distancia entre los ejes de los dos brazos.
- **Escaleras del andén, pendientes de estándar.** Las que suben del andén a la losa del puente no tienen todavía medida estándar: Ricardo la decide con los datos de Portales. Mientras tanto cada estación conserva las suyas y lo dice en su archivo.

## Lo que no le aplica

Las reglas de la Línea 7 (salidas laterales, islas, cascada, nodo de estación a la mitad del pasillo central) no valen aquí.
