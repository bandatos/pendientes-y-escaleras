---
type: task
id: task-26
title: Revisar y afinar los trazos de Portales y San Pedro de los Pinos en JOSM
state: open
date: 2026-09-02
owner: ricardo
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
related: ["[[adr-0010]]", "[[adr-0006]]", "[[task-8]]"]
---

# Revisar y afinar los trazos de Portales y San Pedro de los Pinos en JOSM

Los archivos `data/osm/portales.osm` y `data/osm/san-pedro-de-los-pinos.osm` se generan con `export_station_osm` a partir de las plantillas `data/osm/templates/tlalpan-surface.json` y `data/osm/templates/l7-deep-cascade.json`; los comandos exactos y el esquema de plantilla están en `data/osm/README.md`. Los previews por nivel están en `data/osm/preview/`. La idea es afinar la plantilla, no el XML, para que el ajuste se herede en las estaciones hermanas; lo que solo se pueda corregir en JOSM se anota aquí para llevarlo después a la plantilla.

Supuestos a revisar, todos listados también en el README:

- Andén de Portales de 150 × 10 m: encierra las dos vías `railway=subway` de OSM (a −3,1 y +3,4 m del eje) y roza la calzada central por unos 0,6 m en su esquina norte. Opciones: angostar a 7 m en la plantilla o dejarlo y corregir las vías de OSM.
- Accesos de San Pedro en u ≈ +5,6 m, copiados del nodo existente de OSM; Wikipedia pone las dos salidas en Avenida Revolución con Calle 4 y Calle 9, que cruzan el eje en u ≈ −31 m. Toda la cascada poniente cuelga de ese acceso: verificar con imagen satelital antes de replicar a San Joaquín.
- San Pedro sin torniquetes: sus vestíbulos de torniquetes a −1 solo reciben escaleras y un torniquete no puede ir sobre `highway=steps`. Hace falta un tramo corto de pasillo a −1 en la plantilla, o una regla del generador.
- Lado de los andenes en San Pedro: oriente sirve a «L7 => Rosario» por circulación por la derecha, coincidente con el grafo de Miró; no hay fuente citable de que el Metro circule por la derecha.
- Puente de Portales dibujado como dos líneas rectas (`bridge=yes` + `layer=1`); la forma real de la losa se dibuja a mano.
- Las cuatro escaleras andén–vestíbulo de Portales en abanico a u = ±10 y ±16 m; las posiciones reales son suyas.
- Sentido de las eléctricas unidireccionales = flecha de Miró; en estas dos estaciones todas suben.
- Dimensiones inventadas: andenes de San Pedro 150 × 5 m con 8 m de vías entre ellos y unos 8 m de desarrollo horizontal por tramo de cascada.

Si al abrir en JOSM la capa de OSM real, el validador marca «Way end node near other way» en cantidad, es el falso positivo esperado en estaciones apiladas; los cruces sin nodo compartido entre líneas de niveles distintos ya no se reportan (ticket 18293).

## Criterios de aceptación

- [ ] Las dos plantillas incorporan las correcciones de geometría que Ricardo decida, y los .osm regenerados las reflejan
- [ ] Cada supuesto del README queda confirmado, corregido o convertido en task
- [ ] Se decide qué pasa con los torniquetes de San Pedro

## Notas de trabajo

- 2 de septiembre de 2026 (tarde, [[2026-09-02-sesion-integracion-osm-y-niveles]]): hecho en el generador, según [[adr-0011]]: senda de punta a punta con extremos como vértices del andén (polígono de 6 nodos), contexto de OSM embebido con ids y versión reales (accesos, banquetas, contorno de estación), accesos existentes adoptados con nuestras etiquetas, tramos rectos a cada banqueta a menos de 40 m, área de estación del KML (San Pedro) y, en Portales por esta vez, las dos áreas, la del KML y el contorno de OSM, para que Ricardo elija; en San Pedro edificios de acceso de 12 m con tres puertas y explanadas hasta la banqueta; command `diff_station_osm` para leer la edición de JOSM en metros locales. Pendientes de Ricardo para otra sesión: lado de las puertas de cada edificio (el poniente quedó al sur porque OSM no tiene banqueta a lo largo del lado poniente de Revolución; se cambia con `door_side` en la plantilla), cuál de las tres puertas está clausurada (`closed_doors`), elegir el área de Portales, podar los tramos a banqueta sobrantes, y borrar en Miró el conector de Candelaria que va de «L4 Vestíbulo principal» a sí mismo ([[task-31]]). Ricardo: San Pedro tiene sus accesos en edificios dentro de un parque, así que la distancia a las banquetas (24 y 34 m) no es anomalía. `data/osm/sesion_dibujo.jos` es la sesión de JOSM de Ricardo; se propone ignorarla en git.
- 2 de septiembre de 2026, cierre con crítico ([[2026-09-02-sesion-integracion-osm-y-niveles]]): tres cosas más para la próxima sesión. (1) San Pedro emite seis puertas abiertas, tres por edificio, contra la realidad relevada por Ricardo de tres salidas con una clausurada; falta decir cuál y marcarla con `closed_doors`. (2) En Portales, la «banqueta sin nombre» a la que se conectan los accesos es el puente peatonal que OSM ya tiene (way 43763067, `highway=footway` + `bridge=yes` + `layer=2`, 75 m sobre Calzada de Tlalpan): nuestros dos tramos vestibulares lo duplican, y los tramos del acceso poniente se cuelgan de sus extremos con `level=0`. Ricardo decidió conservar solo lo nuestro en el archivo y resolver la duplicación él en la próxima sesión; también decidió que puentes y túneles siguen siendo candidatos para conectar accesos, porque muchos accesos del Metro no están a nivel de calle. (3) El respaldo de tramos a calles con `sidewalk=*` se eliminó: sin footway a 40 m no sale tramo y el exportador avisa.
- 2 de septiembre de 2026 (noche): el contexto embebido ya no es solo lo que lo nuestro toca. Enmienda de [[adr-0011]]: además de accesos enlazados, vías peatonales y contorno de estación, el archivo lleva congeladas —id y versión reales, sin tocar, sin conectar, nunca destino de tramos— las calles (`highway` de `motorway` a `service` con sus `_link`), las vías urbanas (`railway=subway|light_rail|tram`) y el transporte público (`public_transport=*`, `highway=bus_stop`, `railway=tram_stop`, `amenity=bus_station`) a 50 m de cualquier nodo nuestro; Overpass sigue consultando a 150 m y solo las vías peatonales reciben tramos desde los accesos. Al revisar en JOSM, esas calles y vías son contexto de lectura: la estación se ve dentro de su manzana. Portales embebe 12 calles (Calzada de Tlalpan, Calzada Santa Cruz, Avenida Víctor Hugo, Calle Albert, Calle Hamburgo) y las vías de la Línea 2; San Pedro de los Pinos, 12 calles (Avenida Revolución, Avenida 1, Avenida 1º de Mayo, Calles 2, 4, 7, 9 y 13), la vía de la Línea 7 y la plataforma del Trolebús Elevado.
