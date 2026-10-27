# Componente: cascada de salida de la Línea 7

La salida desde el pasillo central hasta el pabellón, en tres conjuntos de escaleras paralelas por cada lado (oriente y poniente): el primero va del nivel −3 al −2, el segundo vuelve del −2 al −1 en sentido contrario, y el tercero sube del −1 a la calle apilado junto al segundo, desembocando en el centro del pabellón. Nació del trazo de Ricardo en San Pedro y se afinó en San Joaquín; que las dos estaciones compartan este componente, y no sean dos variantes de cascada, está por confirmar con Ricardo. Su JSON es el bloque `banks`, los `extra_ways` marcados con `cascade`, el bloque `fit.cascades` y los accesos `E-01`/`E-02` de `data/osm/templates/l7-deep-cascade.json`; la plantilla todavía trae los valores de antes del 22 de octubre de 2026 (separaciones de 1 a 2,5 m y corrimiento de apilado que mueve el nodo) hasta que aprenda lo de abajo.

## Lo que rige

- Separación de 1,8 m entre ejes en los dos tríos (−3 a −2 y −2 a −1) y de **3,0 m en el par de −1 a la calle**, paralelas, dato de Pablo confirmado por Ricardo (`spacing` de `cascada-oriente-3` y `cascada-poniente-3`). La reversible de cada trío se dibuja de arriba hacia abajo con `incline=down` (`general.md`). Nodo de encuentro en el eje del conjunto; tramos cortos de 1 m a los nodos de encuentro (1,5 m en el extremo lejano del segundo conjunto).
- El par de 3,0 m deja menos holgura sobre el trío de abajo que el de 1,8 m: con los corrimientos de la plantilla el generador avisa 0,20 m en San Pedro oriente y 0,15 m en los dos lados de San Joaquín, bajo el umbral de 0,3 m; los `stack_offset` quedan por reajustar desde las versiones aprobadas (en San Joaquín Pablo corrió el par oriente −0,47 m).
- El tercer conjunto se corre en bloque respecto del eje del segundo, hacia el lado contrario a donde llegan los pasillos de −1 y −2, lo justo para que nada se encime entre niveles: en San Joaquín 0,45 m (un cuarto de la separación). En San Pedro poniente el motivo fue otro, que una conexión de −2 pasaba sobre la punta de una escalera de −1 a la calle (0,5 m).
- Los pasillos de −2 y −1 son ortogonales: salen del nodo de encuentro sobre el eje del conjunto y, donde pasan sobre otro conjunto, van a medio claro (0,9 m del eje).
- Los largos son de cada estación (ver `general.md`). San Joaquín: 21 / 21 / 14,4 m. San Pedro: 16,5 / 13,6 / 12,9 m al oriente y 21,9 / 21,5 / 14,3 m al poniente. La plantilla todavía trae los de la versión 03 de San Pedro (17 / 20,5 / 12,5 y 17 / 16 / 8,5 m) hasta que aprenda de su versión aprobada.
- Regla de slots en todos los conjuntos; la fija en medio.
- El pabellón adoptado de OSM recibe una puerta en cada lado salvo el de las escaleras; cuál está clausurada es un hecho de la estación.
- En una estación hermana la cascada se mueve en bloque, probando primero tal como está dibujada y luego las ocho simetrías ancladas al pabellón de OSM; cabe la que deja todo dentro del área y el centro del pabellón dentro del pabellón, y entre las que caben se prefiere la que no mete las escaleras por el muro de la entrada de OSM, luego la paralela, luego la de aproche más corto. Acortar es el último recurso.

## La regla del caracol

Regla de Ricardo para la caja de la cascada, textual: «el rectángulo a lo largo se divide en 2 partes iguales: una vez que entras (por las escaleras), das la vuelta y en el siguiente medio rectángulo está casi siempre la taquilla, luego das media vuelta y te encuentras el trío de escaleras, vuelves a dar la vuelta y te encuentras otro trío de escaleras (en la estación Constituyentes hay 3 tríos), luego giras un poco (o directo) y ya estás en el pasillo central».

- La escalera de entrada, la que baja de la calle, no siempre sigue la regla: su forma es de cada estación (en Polanco y San Antonio, a cielo abierto, ver `acceso-cielo-abierto.md`).
- En Polanco las dos mitades quedan a 10,5 m entre ejes al oriente y a 11,8 m al poniente; los números viven en el bloque `stations.0200L7-POLANCO` de la plantilla (`local.banks`), y el comentario de su `local` cuenta el caracol de esa estación.
- Que San Pedro y San Joaquín, con pabellón y el tercer conjunto apilado, sean el mismo caracol con otra entrada o un componente distinto no está resuelto; este archivo los guarda juntos mientras tanto.
