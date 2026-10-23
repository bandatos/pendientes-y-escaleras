# Componente: cascada de salida de la Línea 7

La salida desde el pasillo central hasta el pabellón, en tres conjuntos de escaleras paralelas por cada lado (oriente y poniente): el primero va del nivel −3 al −2, el segundo vuelve del −2 al −1 en sentido contrario, y el tercero sube del −1 a la calle apilado junto al segundo, desembocando en el centro del pabellón. Nació del trazo de Ricardo en San Pedro y se afinó en San Joaquín; que las dos estaciones compartan este componente, y no sean dos variantes de cascada, está por confirmar con Ricardo. Su JSON es el bloque `banks`, los `extra_ways` marcados con `cascade`, el bloque `fit.cascades` y los accesos `E-01`/`E-02` de `data/osm/templates/l7-deep-cascade.json`; la plantilla todavía trae los valores de antes del 22 de octubre de 2026 (separaciones de 1 a 2,5 m y corrimiento de apilado que mueve el nodo) hasta que aprenda lo de abajo.

## Lo que rige

- Separación de 1,8 m entre ejes en todos los conjuntos; nodo de encuentro en el eje del conjunto; tramos cortos de 1 m a los nodos de encuentro (1,5 m en el extremo lejano del segundo conjunto).
- El tercer conjunto se corre en bloque respecto del eje del segundo, hacia el lado contrario a donde llegan los pasillos de −1 y −2, lo justo para que nada se encime entre niveles: en San Joaquín 0,45 m (un cuarto de la separación). En San Pedro poniente el motivo fue otro, que una conexión de −2 pasaba sobre la punta de una escalera de −1 a la calle (0,5 m).
- Los pasillos de −2 y −1 son ortogonales: salen del nodo de encuentro sobre el eje del conjunto y, donde pasan sobre otro conjunto, van a medio claro (0,9 m del eje).
- Los largos son de cada estación (ver `general.md`). San Joaquín: 21 / 21 / 14,4 m. San Pedro: 17 / 20,5 / 12,5 m al oriente y 17 / 16 / 8,5 m al poniente.
- Regla de slots en todos los conjuntos; la fija en medio.
- El pabellón adoptado de OSM recibe una puerta en cada lado salvo el de las escaleras; cuál está clausurada es un hecho de la estación.
- En una estación hermana la cascada se mueve en bloque, probando primero tal como está dibujada y luego las ocho simetrías ancladas al pabellón de OSM; cabe la que deja todo dentro del área y el centro del pabellón dentro del pabellón, y entre las que caben se prefiere la que no mete las escaleras por el muro de la entrada de OSM, luego la paralela, luego la de aproche más corto. Acortar es el último recurso.
