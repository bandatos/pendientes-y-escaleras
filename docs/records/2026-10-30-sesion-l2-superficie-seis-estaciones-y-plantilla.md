---
type: record
id: 2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla
title: "Sesión del 27 al 30 de octubre de 2026: la plantilla de Tlalpan aprende el vestíbulo longitudinal y el banco por el lado largo, y seis estaciones de la L2 de superficie llegan a la revisión de Ricardo"
date: 2026-10-30
session: 4cdc1d8b-0ac4-4e3b-ae36-913e8abf4dd0
---

# Sesión del 27 al 30 de octubre de 2026: la plantilla de Tlalpan aprende el vestíbulo longitudinal y el banco por el lado largo, y seis estaciones de la L2 de superficie llegan a la revisión de Ricardo

Bitácora `4cdc1d8b-0ac4-4e3b-ae36-913e8abf4dd0` (una sola conversación: del 27 de octubre por la tarde al 30 de octubre, con una pausa de tres días en la que solo corrió el keep-alive). Rama `first-stations-josm`. Commits: los cuatro de la sesión anterior (`423e2ef`..`270df85`) ya estaban en el árbol y Ricardo pidió hacerles push a media sesión (quedaron en `origin/first-stations-josm`); el de esta sesión es el commit de cierre, pendiente al escribir este record.

## Punto de partida

Ricardo abrió con el alcance, textual:

> Estamos listos para hacer una nueva sesión para todas las estaciones desde Natividas hasta San Antonio Abad, excepto chabacano que no lo haremos con el mismo grupo. Creo que vale la pena de una vez hacer la parte de la línea 2 de ermita de una vez, la única diferencia es que existe un pasillo en el +1 que va por en medio de las vías hacia el sur.

El explorador de apertura encontró cuatro obstáculos antes de trazar: la plantilla de Tlalpan seguía dibujando la losa transversal descartada ([[task-45]] abierta, con el nodo de encuentro de los brazos sin regla); Ermita L2 no se podía exportar porque los 21 stops de Ermita cuelgan del padre de L12 y las claves cortas por sufijo chocan entre líneas; San Antonio Abad traía un tercer acceso de nivel 1 («Acceso Calzada Flotante») y sus dos eléctricas como bidireccionales; y Xola (3) y Ermita L2 (1) tienen elevadores en el CSV crudo que no están en la base.

## Qué se hizo

- **La plantilla aprendió el vestíbulo longitudinal** ([[task-45]], ahora cerrada): `api/utils/osm/vestibule.py` (nuevo) convierte la sección `vestibule` de `tlalpan-surface.json` en la pasarela de nivel 1 en v = senda + 1,40, torniquetes a ±4,1 m del centro (simetría de los de Portales 05, por convención del ejecutor), cuatro escaleras del andén en serie (exteriores 12,5 m, interiores lo que cabe con 1,5 m libres: 9,60 m) y el nodo de encuentro de los brazos a media distancia entre sus ejes; el generador falla si el nodo de encuentro cae fuera de los torniquetes. El bloque `local` de General Anaya desapareció. Regenerada, General Anaya coincide con la 06 dentro de 1 m salvo las escaleras exteriores del andén (12,5 contra 9,11 m; si la 06 publicada se corrige es pregunta de Ricardo, [[task-69]]). Decisiones en [[adr-0017]].
- **Portales es excepción de estación** en el vestíbulo: su bloque lleva `centre` y `meeting` en el eje del brazo poniente, y así reproduce la 05 publicada.
- **El banco de acceso se orienta por el lado largo del lóbulo** (`_lobe_bank` en `arms.py`, `banks.*.lobe` en la plantilla): lóbulo hondo, banco sobre el eje del brazo a 1,8 m; lóbulo ancho, banco a lo largo de la calzada con separación fondo/4, cabecera en el borde del brazo, pie a 3 m del muro de la punta y puerta cerca de la esquina. Reproduce sin excepción los cuatro lóbulos publicados de Portales y General Anaya (Portales oriente dentro de 0,8 m en escaleras y 0,14 m en la puerta; General Anaya idéntica). Residuo que el coordinador aceptó sin preguntar: la eléctrica oriente de Portales mide 14,05 m en la 05 contra 12,5 de la regla (1,1 m); queda pendiente de Ricardo, ligado a la tolerancia de [[task-38]].
- **Filtro `--line`** en `export_station_osm` (y `--context-cache`): filtra los hijos del padre por prefijo de línea y nombra la carpeta `<línea>-<slug>`; las 105 estaciones con hijos salen idénticas sin el filtro. Ermita L2 se exporta como `020L12-ERMITA --line L2`.
- **San Antonio Abad corregida en Miró.** Ricardo: «P3. No son reversibles». Los pathways salen del tablero de Miró, no del GTFS ([[adr-0009]]); los dos conectores de las eléctricas tenían flecha en ambas puntas. Se quitó la segunda punta con script, simulado antes con rollback (exactamente dos cambios `bidir` 1→0), y se reimportó la estación conservando ids. El clasificador del modo auto bloqueó la escritura al tablero compartido; Ricardo pasó a modo manual desde el celular y aprobó el permiso.
- **Seis estaciones generadas por seis `station-tracer` en paralelo** y revisadas por Ricardo en JOSM el 30 de octubre. Las seis validan y `check_station_osm_live` no bloquea ninguna baja en su última versión nuestra. Cada una tiene su task y su archivo en `.claude/skills/station-tuning/references/estaciones/`.
- **Auditoría de congruencia** del skill `station-tuning` y de `data/osm/README.md` contra el código de hoy (catorce hallazgos, aplicados por el auditor en paralelo con este cierre).

## Versiones por estación

| Estación | Carpeta | Nuestras | De Ricardo | Task |
|---|---|---|---|---|
| Nativitas | `l2-nativitas/` | 01-claude (falla la validación), 02-claude | 03-rick | [[task-57]] |
| Villa de Cortés | `l2-villa-de-cortes/` | 01-claude (salió de un envoltorio fuera del repo), 02-claude | 03-rick | [[task-58]] |
| Xola | `l2-xola/` | 01-claude | 02-rick | [[task-59]] |
| Viaducto | `l2-viaducto/` | 01-claude, 02-claude | 03-rick | [[task-60]] |
| San Antonio Abad | `l2-san-antonio-abad/` | 01-claude (baja que OSM bloquea), 02-claude | 03-rick | [[task-61]] |
| Ermita L2 | `l2-ermita/` | 01-claude (falla la validación), 02-claude | ninguna | [[task-62]] |

Ninguna tiene copia `-pub`: no se publicó nada en esta sesión. Con estas seis llegarían a doce las estaciones de mapeo manual, el tope de [[task-11]].

## Decisiones de Ricardo

Las costosas de revertir están en [[adr-0017]] (vestíbulo y banco del componente Tlalpan) y [[adr-0018]] (reglas generales, estaciones de correspondencia, nombres de contorno, elevadores). Las de una sola estación están en su task. Las preguntas que Ricardo dejó sin responder en texto (Villa de Cortés P3 y P5, Xola P7) se resuelven primero con el diff de su versión.

## Correcciones de Ricardo sobre la forma de trabajar

- Pidió que las presentaciones lleven imágenes porque revisaba desde el celular (27 de octubre); al volver a su computadora pidió las preguntas citando el `.osm` que debía abrir (30 de octubre).
- Las opciones se explican completas, no comprimidas, textual:

> Siento que en el Claude.md del proyecto o en el skill correspondiente deberíamos decir que la explicación de las opciones debe intentar no resumirse, es mejor entenderlo con claridad que resumir las explicaciones, por ejemplo con la P11 me pasó, pero en general siento que es dificil descifrar lo que me dices con tan poco texto, aunque siento que tiene que ver con que estamos revisando muchas estaciones a la vez.

  Capturado como feedback global [[global:fb-1100]].

## Desviaciones del coordinador que no corrigió Ricardo

- El brief del trazador de San Antonio Abad puso el acceso flotante al norte del vestíbulo; Chabacano está al sur. Lo corrigió el trazador, que lo reportó como hecho falso del brief ([[global:fb-1101]]).
- Seis trazadores, y antes dos ejecutores, escribieron a la vez en la plantilla y el builder ([[global:fb-1103]]).
- Llamadas que los delegados devolvían a Ricardo (torniquetes a ±4,1 m, residuo de 1,1 m de Portales) se le presentaron como resueltas ([[global:fb-1105]]); quedaron pendientes en [[adr-0017]].
- Se afirmó sin verificar que el túnel 536525793 de Ermita no pertenece a ninguna relación ([[global:fb-1106]]).
- El clasificador bloqueó la escritura a Miró aunque Ricardo había elegido esa opción ([[global:fb-1102]]). Ricardo pidió que este cierre lo hiciera un subagente que lee la bitácora, no un fork ([[global:fb-1104]]).

## Lo que queda abierto

Los seis turnos de diff (su primer entregable es la comparación de la versión de Ricardo contra la nuestra), bajo [[task-56]]; la Calzada Flotante en sesión aparte ([[task-64]]); y los aprendizajes del generador y del validador: contexto ampliado ([[task-65]]), borrar y adoptar ways de OSM desde la plantilla ([[task-66]]), `osm_node` con `locate: door` ([[task-67]]), brazo sin lóbulo ([[task-68]]), trazo para la vuelta y pasillo en la mitad opuesta ([[task-69]]), conectores a la banqueta ([[task-70]]), elevadores ([[task-71]]), `stop_key` ([[task-72]]), entradas del contexto en el validador ([[task-73]]) y el andén que contiene las vías ([[task-74]]). Ricardo decidió cerrar la sesión antes de los diffs porque la ventana de contexto ya estaba cargada.

También abierto, de Ricardo:

- La P6 del 27 de octubre, el andén de Tlalpan que contiene las dos vías de OSM, que nunca respondió ([[task-74]]).
- Los torniquetes a ±4,1 o ±5 m y el residuo de la eléctrica oriente de Portales ([[adr-0017]]), y si General Anaya y Portales publicadas se corrigen ([[task-69]]).
- Si los scripts con los que se armaron las versiones 02 (Nativitas, San Antonio Abad, Ermita) y la 01 de Villa de Cortés se versionan junto a cada estación o se quedan en `.claude/scratch/l2-2026-10-27/`, ignorado por git, sin reproducibilidad.
- Heredado de la sesión anterior y sin tocar en esta: subir la corrección del jardín poniente de San Pedro ([[task-54]]), decidir la explanada oriente (way 1572119589) y poner los textos largos y la aclaración de San Joaquín en las discusiones de los changesets.
