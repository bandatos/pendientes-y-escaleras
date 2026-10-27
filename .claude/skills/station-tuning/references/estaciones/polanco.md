# Polanco (Línea 7)

Carpeta `data/osm/l7-polanco/`. Componentes: andén profundo de la Línea 7 (`componentes/anden-l7-profundo.md`), cascada de la Línea 7 en su forma de caracol (`componentes/cascada-san-pedro.md`) y acceso a cielo abierto (`componentes/acceso-cielo-abierto.md`). Marco de la 01: rumbo 6,5° y ancla 19.4335865,-99.1909774, en el centroide del KML. Sus hechos viven en el bloque `stations.0200L7-POLANCO` de `data/osm/templates/l7-deep-cascade.json`, que empieza con `keys` porque los sufijos del tablero nombran otros papeles que en las hermanas. La versión vigente es la más alta de la carpeta. La tarea que lleva la estación se enlaza aquí cuando se abra.

## Hechos propios

- **Un solo lateral por andén.** Es la única de la familia con una salida lateral por andén, al norte, de unos 9 m de ancho (no los 6,5 m del componente) y con patas diagonales, 4,2° al oriente y 7,9° al poniente, que el `elbow` de la plantilla no expresa.
- **Lóbulos sur del KML.** Son nichos electromecánicos y no llevan trazo (dato de Pablo).
- **Salida doble al oriente.** Acceso doble con las dos bocas a 18,67 m una de otra y un descanso compartido; las dos escaleras miden 9,34 m. El generador aún no dibuja el acceso doble (`componentes/acceso-cielo-abierto.md`).
- **Escaleras a la calle** de 10 m en el norponiente y el surponiente: regla de Pablo solo para Polanco.
- **Pestaña sur** alargada 4,5 m por Pablo.
- **Entradas de OSM** movidas de 3,1 a 11,9 m por dato de campo; la de 11,9 m excede el tope general de 10 m y se aceptó.
- **Relación `stop_area` 8429771.** Fuera del archivo por acuerdo con Pablo: se conserva en el servidor tal como está.
- **Pasillos centrales** en u −0,7 (oriente) y −1,8 (poniente); nodo de estación en u −1,25, entre los dos.
- **Caracol.** Las dos mitades de la caja de la cascada quedan a 10,5 m entre ejes al oriente y a 11,8 m al poniente.

## Versiones

- 01, generada con `keys`.
- 02, del trazador.
- 03, de Pablo.
- 04, integra lo de Pablo.
- 05, escaleras a la calle de 10 m.
- 06, el oriente en línea.
