# Criterios generales: toda estación

Estado vigente en prosa de lo que rige en cualquier estación. El porqué de cada pieza está en los ADR de convenciones de `docs/decisions/` (catálogo de etiquetado y geometría del generador); aquí no se repite la historia, solo lo que hoy se aplica. Lo marcado «por confirmar» lo decidió una sesión y Ricardo no lo ha validado todavía.

## Dónde vive cada cosa

Un número que el generador consume vive en JSON (`data/osm/templates/`); un criterio vive en prosa, aquí o en el archivo de su componente o estación; cada prosa nombra su JSON. El catálogo de etiquetas vive en `api/utils/osm/tags.py` y el ADR de catálogo lo explica; no se transcribe aquí.

## El área de la estación

- El área es la regla fundamental: todo trazo interior propio (andenes, sendas, pasillos, escaleras, nodos de encuentro, torniquetes) cae dentro de ella, y la validación lo trata como error. Accesos, pabellones, explanadas y conectores quedan fuera por definición. Si algo no cabe, lo primero es revisar la orientación y la posición del trazo, no el área: en San Joaquín las escaleras resultaron perpendiculares a las vías porque de otro modo no cabían. El área solo se toca con cambios mínimos o con evidencia (punto siguiente).
- El polígono del KML es la mejor forma disponible y el generador lo usa como área; donde OSM ya tiene contorno, ese contorno conserva su id y toma la geometría del KML. Pero el KML puede estar mal en un tramo: Ricardo corrigió a mano el área de San Joaquín. La corrección vive en la cadena de versiones de la estación y, si se generaliza, en un bloque por estación de la plantilla.
- Forma del área: un way cerrado con las etiquetas de estación cuando no tiene islas (Portales conserva así su edificio de OSM intacto); una relación multipolígono, con las etiquetas en la relación, un `outer` y un `inner` por isla, cuando las tiene (las cuatro islas que encierran las salidas laterales de la Línea 7). Nunca cortes de ancho cero: dibujan en JOSM muros que no existen.
- Los cambios al KML son mínimos. Una forma claramente intencional del KML (un vestíbulo redondo, un pasillo en diagonal, un ensanche) se respeta y no se pregunta si se endereza; lo que sí se corrige son las costuras, los pellizcos y las asimetrías de centímetros. Ricardo puede corregir el KML con más fuerza cuando conoce la estación, como hizo con el pasillo central de San Joaquín; el agente no lo propone sin evidencia (imagen, croquis, OSM).
- Se permiten ajustes finos de vértices no esenciales del área para que los elementos queden alineados, ortogonales y congruentes entre sí: centrar un pasillo lateral entre sus muros, cuadrar una esquina. Es mínimo, pero ayuda a la congruencia del conjunto.
- Un edificio de OSM que sobresale unos centímetros del área se ajusta mínimamente para que quepa, antes que deformar el área.

## Pasillos y anchos

- Los pasillos son líneas (`highway=footway` + `indoor=yes` + `level`), nunca áreas ni `corridor`; el «ancho» de un pasillo es el ancho del lóbulo del área que lo contiene.
- Los pasillos del mismo tipo tienen el mismo ancho; los de tipos distintos no: en la Línea 7 el pasillo central no mide igual que las salidas laterales del andén. Las medidas estándar de cada tipo se fijan en el componente.
- Los codos y curvas se dibujan con pocos nodos, parecidos a como Ricardo los deja a mano; una curva «estable» es una lógica de esquina clara, no cientos de vértices.
- Los trazos se ortogonalizan con herramienta; Ricardo lo intenta a ojo y espera que el agente lo deje exacto.

## Escaleras y circulación

- Se circula por la derecha: en un conjunto de escaleras paralelas que van en sentidos opuestos, avanzas por la derecha y ves a tu izquierda a quien viene en sentido contrario, sin importar si subes o bajas. Ricardo rompe esta regla sin querer al editar; el turno la restaura de oficio y se lo dice.
- Regla de slots, mirando el conjunto de escaleras paralelas desde el nivel bajo, de izquierda a derecha: las eléctricas que bajan, las fijas, las que suben. La fija siempre en medio; la reversible de la Línea 7 cuenta como la que baja.
- Las escaleras que no nacen del andén van en conjuntos paralelos (dos o tres escaleras que unen los mismos dos niveles) a **1,8 m entre ejes**, derivado de la mediana del trazo de Ricardo en San Joaquín (un componente puede fijar otra: el par de −1 a la calle de la cascada de la Línea 7 va a 3,0 m), con un tramo corto que une cada punta a un nodo de encuentro.
- El nodo de encuentro va en el eje del conjunto: sobre la escalera central si son tres, a la mitad si son dos. Esta regla manda sobre la de no encimar: cuando un pasillo de otro nivel cae encima de una escalera o de un nodo, se corre un poco el conjunto de escaleras (en San Joaquín, 0,45 m), nunca el nodo. Ninguna línea queda a menos de unos 0,3 m de una línea de otro nivel.
- Los largos de las escaleras son un hecho de cada estación, no del componente. En la cascada de la Línea 7 son típicos 21 m en las de −3 a −2 y −2 a −1 y 14,4 m en las de −1 a la calle (San Joaquín), pero «no siempre es igual»: San Pedro los acerca al poniente (21,9 / 21,5 / 14,3 m) y al oriente los tiene más cortos (16,5 / 13,6 / 12,9 m). Lo mismo vale para las escaleras de cambio de andén.
- Sentido de dibujo: las fijas y las eléctricas que suben van de abajo hacia arriba con `incline=up`; la reversible de cada trío va de arriba hacia abajo con `incline=down`, porque su sentido principal es bajar (dato de campo de Pablo, confirmado por Ricardo), y conserva `conveying=reversible`; la eléctrica de un solo sentido que baja va de arriba hacia abajo con `incline=down`. El `incline` siempre concuerda con el orden de dibujo: nivel del primer nodo menor que el del último es `up`, mayor es `down`. Las etiquetas de cada tipo (`conveying`, `oneway:foot`, `wheelchair=no`) están en el catálogo; no se improvisan.
- En los andenes, que la senda corra por la derecha es un supuesto sin fuente de campo (por confirmar).

## Lo que viene de OSM

- Lo que OSM ya tiene bien mapeado se adopta, no se duplica: pabellones aunque lleven `building=transportation`, explanadas con sus anillos, entradas existentes. Lo adoptado conserva id, versión y etiquetas y recibe solo lo que le falta.
- Los accesos de OSM se mueven hasta el punto medio del muro del pabellón al que estaban pegados, hasta unos 10 m. Ricardo confirmó que siga así como lógica general.
- Conectar o soldar un trazo nuestro a un elemento de OSM se decide por categoría, con criterio: se acopla cuando es del mismo nivel y claramente colindante (el edificio de la estación, el anillo de una explanada, la acera cuando cumple la regla de conectores de abajo); no se sueldan jardines ni líneas que siguen otra lógica, aunque toquen el área. Si aparece algo que tiene sentido conectar y no cae en estas categorías, se conecta, se reporta y se propone la categoría.
- Lo demás de OSM entra congelado como escenografía. El nodo `railway=station` es la excepción: se mueve, aunque doble un poco la vía de OSM de la que es vértice, sin aviso. Dónde va lo dice el componente.
- Un puente peatonal que OSM ya tiene se borra solo si cae sobre el área de la estación, porque nuestro trazo del vestíbulo-puente lo reemplaza con más detalle; si queda fuera del área no es de la estación y se queda. En Portales el way 43763067 cruzaba sobre el área y se borró; en General Anaya el 43763040 está a 70 m del andén y se quedó.
- Un nodo de OSM se da de baja solo si ningún objeto de OSM lo usa, y eso se confirma contra OSM en vivo con `check_station_osm_live` (uso en `data/osm/README.md`), no solo contra `context.json`: la caché trae lo que hay a 250 m del ancla y un way que pasa por el nodo puede quedar fuera de ella. El generador ya no da de baja los nodos que el contexto usa; la consulta en vivo es la segunda comprobación, antes de que la versión se dé por buena.
- **Conectores a la banqueta.** Un acceso lleva conector solo cuando hay un enlace corto y evidente a una banqueta mapeada en OSM. Si no lo hay, la boca queda sin conector: no se inventa un trazo que atraviese un parque, un jardín o un cruce de calle para alcanzar la peatonal más cercana. El generador todavía tira conectores automáticos a toda peatonal a menos de 45 m; ese tope es provisional, sus candidatos se podan con esta regla, y el acceso que no debe llevar conector se declara en la plantilla con `connector: false` (`data/osm/README.md`, paso 8). Lo que ya se publicó queda como lo dejaron Pablo y Ricardo; cada archivo de estación lo dice.
- El contexto se trae a 120 m de lo dibujado y se consulta a 250 m del ancla; edificios y barreras entran; puentes y túneles son destino válido de conector, porque muchos accesos del Metro no están a nivel de calle.
- Cada cambio a un elemento de OSM que haga Ricardo o un turno se presenta con hipótesis de intención; Ricardo confirma uno por uno.

## Los pabellones y accesos

- Cuántas puertas recibe un pabellón adoptado y en qué muros lo dice su componente: en la cascada de la Línea 7, una en cada lado salvo el de las escaleras (`componentes/cascada-san-pedro.md`); en la superficie de Tlalpan, una sola hacia la Calzada (`componentes/tlalpan-surface.md`). En todos los casos cada puerta lleva un pasillo al nodo central del pabellón y la clausurada sale como `disused`.
- Las puertas laterales pueden correrse a lo largo de su muro cuando la estación lo pide; eso es un hecho de la estación, no una regla.

## Fuentes

- Esri World Imagery para leer la estación, nunca para medir (el skill dice cómo).
- Los croquis del STC («Proyecto de espacios publicitarios», 2002) no son métricos: la escala gráfica es un sello idéntico en todas las páginas, la franja de andenes está dibujada 1,75 veces más ancha que la real (San Antonio, San Pedro, Mixcoac, Barranca) y a lo largo de las vías no son coherentes ni consigo mismos (errores de hasta 3,5 m). Sirven para la disposición, los sentidos, los carriles, los torniquetes y los largos fuera de la franja; los muros siguen siendo los del KML. El hallazgo está en la tarea de San Antonio (task-41) y el detalle de los croquis en la tarea del croquis (task-39).
