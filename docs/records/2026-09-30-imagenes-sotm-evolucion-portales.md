---
type: record
id: 2026-09-30-imagenes-sotm-evolucion-portales
title: "Imágenes para State of the Map Latinoamérica: evolución del mapeo de Portales por versión"
date: 2026-09-30
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]", "[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
---

# Imágenes para State of the Map Latinoamérica: evolución del mapeo de Portales por versión

Sesión del 30 de septiembre de 2026 (session log `session_01XPxVLt8R4nwZqeLvioLX9J`). Ricardo prepara una presentación para el State of the Map Latinoamérica, que será en México, y necesitaba para una diapositiva una imagen por versión del mapeo automatizado de una estación, con todos los niveles en cada imagen, que mostrara de un vistazo cómo fue mejorando. Esta es la fotografía de qué se encontró, qué se generó y qué eligió. Se relaciona con [[task-10]] (compartir con la comunidad OSM México) y con la revisión en JOSM de [[task-26]].

## Los cuatro estados de cada estación

El generador (`export_station_osm`, [[adr-0011]], [[adr-0012]], [[adr-0013]]) no se ha tocado desde el 2 de septiembre; los commits posteriores en la rama son solo documentación. Para Portales y San Pedro de los Pinos existen cuatro estados distinguibles, todos del 2 de septiembre:

| Estado | Dónde | Qué lo distingue |
|---|---|---|
| v1, commit `392924e` (01:33) | `git show` | Esquema puro: grafo de la base más plantilla por familia; andenes inventados, accesos como nodos nuevos, sin contexto OSM. |
| v2, commit `85fb16a` (18:20) | `git show` | Contexto de Overpass, accesos reales adoptados por `osm_id`, área de estación del KML, edificios de acceso en San Pedro. |
| v3, commit `788d624` (20:57) | `data/osm/*.osm` | El polígono del KML reforma el contorno OSM, andenes inscritos con ancho derivado, bancos de escaleras, pabellones reales adoptados, contexto a 120 m. |
| Final a mano (JOSM, 22:55) | `~/Descargas/portales(1).osm` y `~/Descargas/san-pedro-de-los-pinos-medias.osm` | Edición de Ricardo sobre v3; no está versionada. |

Los archivos `~/Descargas/portales.osm` y `~/Descargas/san-pedro-de-los-pinos.osm` son byte a byte iguales a v3. Sobre el sufijo del archivo de San Pedro, Ricardo:

> medias en nombre es que solo terminé la mitad de la estación (la salida poniente)

Los PNG que había en `.claude/scratch/` son conversiones de un borrador anterior a v1 y a San Pedro le faltan dos niveles; no sirvieron como primera versión.

## Hallazgos de datos

- En la edición final de Portales, la pasarela OSM 43763067 (`highway=footway`, `bridge=yes`, `layer=2`) y los dos accesos OSM adoptados (nodos 5197203900 y 5197203901) llevan `action=delete`, y los pabellones y plazas que v3 generó ya no están en el archivo. Quedan dos accesos generados. Es decir: la edición a mano en Portales no solo movió, también podó.
- Las cifras de desplazamiento entre v3 y la edición final dependen del método: contar nodos con `action=modify` da 61 en Portales y 47 en San Pedro; emparejar por geometría (JOSM renumera los ids negativos) da 27 y 35 objetos, con máximos que varían porque las escaleras de etiquetas idénticas se emparejan de forma ambigua. Por eso la imagen final no lleva cifras.
- El renderer del repo (`api/utils/osm/preview.py`) no sirve para esta lámina: produce un SVG por nivel, omite el contexto OSM y solo lee su propio documento, no un `.osm` editado por JOSM.
- No existe nada en el grafo sobre State of the Map ni sobre la presentación; esta sesión es el primer rastro.

## Las tres propuestas

Tres ejecutores en paralelo, cada uno con un enfoque y libertad para iterar mirando sus propios PNG, produjeron cuatro imágenes por estación más una tira 4-en-1:

- **A, pila isométrica** (`.claude/scratch/sotm/iso/`): un plano traslúcido por nivel, apilados, escaleras como conectores 3D, halo amarillo en lo nuevo o movido. La mejor para entender la cascada de San Pedro; floja en Portales, con dos niveles.
- **B, planta con color por nivel** (`.claude/scratch/sotm/plan/`): un plano cenital por versión, rampa de color por profundidad, insignias numeradas con las mejoras; paleta validada para daltonismo.
- **C, planta más corte transversal con colores de cambio** (`.claude/scratch/sotm/free/`): planta arriba, corte este-oeste abajo, color por lo que hizo cada versión (nuevo, ajustado, heredado).

Ricardo descartó desde el principio las rejillas de una imagen por nivel («no cabe en una diapositiva») y aceptó que fueran cuatro imágenes.

## La elección

> Nos quedaremos con la propuesta C. solo con portales, con los siguientes ajustes: Quitar el "título y subtítulo", quitar la V2, quitar el "corte transversal", que está abajo. Me haría más sentido que los colores se usaran para tipos de cosas, más que para identificarlo que cambio, por ejemplo: área de estación, escaleras normales, escaleras eléctricas, pasillos, andenes. Si dejamos solo 3 versiones se entenderá por sí mismo

La imagen final es `.claude/scratch/sotm/free/out/portales-3up-tipos.png` (16:9, 3520 px), con los tres paneles sueltos como `portales-tipos-{v1,v3,v4-josm}.png`. Se regenera desde `.claude/scratch/sotm/free/` con:

```
python3 render_free.py --slug portales --versions v1,v3,v4 --colour-by type --no-title --no-section
```

Paleta por tipo validada con el validador del skill dataviz (daltonismo PASS; aviso de contraste bajo en turquesa y ocre, compensado por forma y leyenda): área de estación `#1fc4bf`, andén `#1e7bc1`, pasillo `#6731aa` (el del puente a +1 con borde oscuro), escalera fija `#eb5422`, escalera eléctrica `#ab276e`, acceso `#3f964c`, torniquetes `#d9a421`. Pabellones y plazas de v3 van en el turquesa del área, sin entrada propia en la leyenda. Ricardo dio la imagen por terminada sin aplicar el recorte al centro de la estación que se le propuso.

Todo vive en `.claude/scratch/sotm/`, que git ignora: `inputs/` con las ocho versiones `.osm`, una carpeta por propuesta con su script, su `NOTES.md` y su `out/`. Nada del repo versionado cambió; el record es el único rastro en el grafo.

## Sobre la subida a OSM

Ricardo dijo que para el State of the Map ya se habrá subido a OSM. La política de importación ([[task-11]]) sigue abierta y v2 y v3 ya modifican objetos existentes.
