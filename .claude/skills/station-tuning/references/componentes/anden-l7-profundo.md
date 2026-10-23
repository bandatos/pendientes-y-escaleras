# Componente: andén profundo de la Línea 7

Dos andenes laterales bajo tierra en el nivel −3, con las vías en medio, un pasillo central de salida y salidas laterales desde cada andén, más el paso bajo las vías para cambiar de andén. Lo comparten San Pedro de los Pinos y San Joaquín; Xola está por generar. Su JSON es hoy el bloque de andenes (`P-01`, `P-02`), los `nodes` y las `edges` de `data/osm/templates/l7-deep-cascade.json`; cuando la plantilla se parta en componentes, este archivo nombrará su pieza.

## Lo que rige

- Los andenes se inscriben en la franja larga del KML: el hueco de vías mide 6,5 m y el ancho de cada andén sale de la franja; el largo lo fijan los cruces del anillo del área, y los seis vértices de cada andén son vértices del área. La franja se mide sin muros falsos: en San Pedro da 15,23 m y andenes de 4,37 m.
- La senda de cada andén corre 1,5 m hacia la vía respecto del eje del andén (convención de dibujo, por confirmar).
- **Salidas laterales.** Cada andén tiene dos, que giran y desembocan en el pasillo central como un solo recinto, sin muro al final. Las cuatro miden **6,5 m**, estándar del componente para todas sus estaciones. El codo es una pierna recta corta seguida de cuartos de círculo concéntricos (muro interior, senda y muro exterior a ±3,25 m de la senda), con 4 a 5 tramos por arco; las esquinas donde la salida se une al pasillo central quedan rectas. Las patas paralelas a la vía de un mismo lado son colineales.
- **Islas.** Lo que las salidas laterales encierran entre el andén y el pasillo central no es estación: son los `inner` del multipolígono del área. Sus esquinas del lado del andén y las bocas de las salidas van exactamente sobre el borde exterior del andén.
- **Pasillo central.** Recto, ortogonal y de ancho constante desde el andén hasta las primeras escaleras que suben. Su ancho es de cada estación, no del componente (San Joaquín 10,4 m, San Pedro 7,4 m); Ricardo sospecha que depende de cómo se construyó, pero no hay regla.
- **Escaleras de cambio de andén** (paso bajo las vías, −4 a −3). Arrancan más adentro del pasillo central de lo que daba el generador, simétricas respecto del eje entre andenes. Su largo es de cada estación (San Joaquín 8,9 m; San Pedro 7,2 m, con el tope a ~1,2 m del cruce con la salida lateral).
- **Nodo de estación.** El `railway=station` va a la mitad del pasillo central y en el eje entre los dos andenes. Ojo: la mitad del pasillo central no es la mitad del andén (en San Joaquín queda 14 m al norte).
