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
