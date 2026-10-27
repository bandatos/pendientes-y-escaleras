# Publicación en OSM de seis estaciones, 27 de octubre de 2026

Las seis las publicó Ricardo con su cuenta la madrugada del 27 de octubre de 2026: General Anaya (changeset 191085829), Portales (191085874), Polanco (191085961), San Antonio (191086008), San Joaquín (191086058) y San Pedro de los Pinos (191086111). Cada changeset contiene exactamente su archivo `-pub`, verificado contra el servidor. El changeset de San Joaquín (191086058) lleva por error el comentario corto de San Pedro; como un changeset cerrado no se edita, la aclaración y el texto correcto van como primer comentario en su discusión.

Archivos para subir con JOSM, uno por estación, generados con `publish_station_osm` a partir de la versión aprobada de cada una. Son copias sin las etiquetas de traza (`note:*`) y sin `upload='never'`, por eso en JOSM la flecha de subir aparece activa. Las versiones de trabajo siguen en la carpeta de cada estación.

## Mecánica en JOSM, igual para todas

1. Abrir el archivo `-pub` de la estación (Archivo → Abrir). No hace falta descargar datos de OSM antes: el archivo trae los objetos existentes con su versión.
2. Subir (Archivo → Subir datos, o la flecha verde). En la pestaña **Description** del diálogo: en el comentario, pegar el texto corto de la estación; en la fuente de datos, `survey`.
3. En la pestaña **Settings** del mismo diálogo, en la tabla de etiquetas del changeset, agregar una fila con clave `imagery_used` y valor `Esri World Imagery`. JOSM agrega sola `created_by`.
4. Un changeset por estación. Al terminar la subida, abrir la página del changeset en openstreetmap.org y pegar el texto completo de la estación como primer comentario en la discusión. El comentario del changeset admite solo 255 caracteres; por eso va corto, y el detalle va en la discusión.

Conteos esperados en el diálogo de subida (objetos por agregar / por modificar / por borrar), para confirmar que el archivo abierto es el correcto:

| Estación | Archivo | Agregar | Modificar | Borrar |
|---|---|---|---|---|
| Polanco (L7) | `polanco-07-pub.osm` | 243 | 4 | 0 |
| General Anaya (L2) | `general-anaya-06-pub.osm` | 79 | 2 | 14 |
| Portales (L2) | `portales-05-pub.osm` | 81 | 7 | 25 |
| San Joaquín (L7) | `san-joaquin-09-pub.osm` | 260 | 15 | 0 |
| San Pedro de los Pinos (L7) | `san-pedro-de-los-pinos-08-pub.osm` | 311 | 4 | 0 |
| San Antonio (L7) | `san-antonio-06-pub.osm` | 269 | 7 | 0 |

«Modificar» y «Borrar» cuentan solo objetos que ya existen en OSM. Es lo mismo que JOSM muestra en el diálogo de subida y lo que queda registrado en el changeset.

## Polanco (L7)

Comentario del changeset:

> Metro Polanco (L7), mapeo colaborativo de Bandatos en sitio: agregamos área, andenes, pasillos, escaleras y torniquetes (niveles −4 a 0); movimos las 3 entradas (3 a 12 m) y el nodo de estación (6 m). No borramos nada.

Primer comentario en la discusión del changeset:

> Estación Polanco, Línea 7. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Agregamos el área de la estación (multipolígono), los dos andenes y los pasillos, escaleras y torniquetes de los niveles −4 a 0, con los accesos norponiente, surponiente y el acceso doble del oriente. Modificamos las tres entradas existentes: las movimos entre 3 y 12 m a su boca real y les agregamos las etiquetas entrance, level y description. Movimos el nodo de estación 6 m al eje entre andenes. No borramos ningún objeto.

## General Anaya (L2)

Comentario del changeset:

> Metro General Anaya (L2), mapeo colaborativo de Bandatos en sitio: el edificio toma su forma real con 2 pabellones; agregamos andén, puente-vestíbulo, escaleras, pasillos, torniquetes y 2 entradas. Borramos 14 nodos sueltos del contorno viejo.

Primer comentario en la discusión del changeset:

> Estación General Anaya, Línea 2. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Modificamos el edificio de estación existente para que tome la forma del polígono real con sus dos pabellones. Agregamos el andén central con su senda, el puente de vestíbulo sobre las vías, las escaleras de acceso y de andén, pasillos y torniquetes, y las dos entradas, una por pabellón, en la fachada hacia Calzada de Tlalpan. Movimos el nodo de estación 14 m al cruce del vestíbulo. Lo único que borramos son 14 nodos del contorno anterior del edificio que quedaron sueltos.

## Portales (L2)

Comentario del changeset:

> Metro Portales (L2), mapeo colaborativo de Bandatos en sitio: agregamos andén, escaleras, pasillos y torniquetes; el edificio toma su forma real. Borramos el puente peatonal que duplicaba el vestíbulo, ahora en detalle, y 20 nodos del contorno viejo.

Primer comentario en la discusión del changeset:

> Estación Portales, Línea 2. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Agregamos andén, senda, escaleras, pasillos del puente, torniquetes y un conector a la banqueta. Modificamos el edificio de estación existente para que tome la forma de la estación con sus dos pabellones; movimos las dos entradas existentes 12 m a la puerta de su pabellón frente a Calzada de Tlalpan y les agregamos las etiquetas entrance, level y description; movimos el nodo de estación 14 m al vestíbulo y ajustamos tres nodos de la banqueta y de Calle Hamburgo. Borramos el puente peatonal que duplicaba el vestíbulo-puente, que ahora está trazado en detalle, y 20 nodos del contorno anterior del edificio.

## San Joaquín (L7)

Comentario del changeset:

> Metro San Joaquín (L7), mapeo colaborativo de Bandatos en sitio: agregamos área, andenes, pasillos, 18 escaleras y torniquetes; corregimos el nombre de las 2 entradas (San Juaquin → San Joaquín) y las movimos 1,5 m. No borramos nada.

Primer comentario en la discusión del changeset:

> Estación San Joaquín, Línea 7. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Agregamos el área de la estación (multipolígono con cuatro islas), los dos andenes, pasillos, 18 escaleras y dos torniquetes de los niveles −4 a 0. Modificamos las dos entradas existentes: las movimos 1,5 m al muro de su pabellón, corregimos su nombre (San Juaquin → San Joaquín) y les agregamos las etiquetas entrance, level y description. Ortogonalizamos los dos pabellones; ningún nodo se movió más de 28 cm. Movimos el nodo de estación 2 m al eje entre andenes. No borramos ningún objeto.

## San Pedro de los Pinos (L7)

Comentario del changeset:

> Metro San Pedro de los Pinos (L7), mapeo colaborativo de Bandatos en sitio: agregamos área, andenes, pasillos, 18 escaleras, torniquetes y el acceso oriente; movimos el acceso poniente (5 m) y el nodo de estación (30 m). No borramos nada.

Primer comentario en la discusión del changeset:

> Estación San Pedro de los Pinos, Línea 7. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Agregamos el área de la estación (multipolígono con cuatro islas), los dos andenes, pasillos, 18 escaleras, dos torniquetes y dos explanadas peatonales de los niveles −4 a 0; también el acceso oriente y las puertas laterales y las clausuradas de ambos pabellones. Modificamos el acceso poniente existente: lo movimos 5 m al muro de su pabellón. Movimos el nodo de estación 30 m a la mitad del pasillo central. No borramos ningún objeto.

## San Antonio (L7)

Comentario del changeset:

> Metro San Antonio (L7), mapeo colaborativo de Bandatos en sitio: agregamos área, andenes, pasillos, 16 escaleras y torniquetes; movimos las 2 entradas (1 y 4 m) y el nodo de estación (16 m); redibujamos el edificio del acceso oriente. No borramos nada.

Primer comentario en la discusión del changeset:

> Estación San Antonio, Línea 7. Mapeo colaborativo de Bandatos: el equipo recorrió y visitó la estación. Agregamos el área de la estación (multipolígono con cuatro islas), los dos andenes, pasillos, 16 escaleras y dos torniquetes de los niveles −4 a 0; el acceso poniente es a cielo abierto y el oriente queda bajo el edificio de Tintoreto. Modificamos las dos entradas existentes, que movimos 1 y 4 m, y el edificio del acceso oriente, que redibujamos sobre la imagen y alargamos a 12,8 m. Movimos el nodo de estación 16 m a la mitad del pasillo central. No borramos ningún objeto.
