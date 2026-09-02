---
type: task
id: task-29
title: Replicar las plantillas a Xola y San Joaquín
state: open
date: 2026-09-02
owner: ai
source: ["[[2026-09-02-sesion-primeras-dos-estaciones-josm]]"]
depends-on: ["[[task-26]]"]
related: ["[[adr-0006]]", "[[adr-0010]]"]
validate-paths: false
---

# Replicar las plantillas a Xola y San Joaquín

Segundo paso del plan de Ricardo: una vez afinadas las dos plantillas ([[task-26]]), generar las estaciones hermanas y comparar. Xola ya exporta sin errores contra `tlalpan-surface` (mismo perfil de etiquetas que Portales, hereda el puente); San Joaquín tiene en la base los mismos 14 nodos, 26 aristas y modos que San Pedro de los Pinos, pero la dirección de almacenamiento de sus aristas bidireccionales difiere y el generador necesitó canonicalizarlas para exportarla. Xola requiere además decidir sus tres elevadores, presentes en `data/raw/elevadores_escaleras_v4.csv` y ausentes en la base (el generador falla con error nombrado ante un elevador hasta que `tags.py` los soporte como nodo `highway=elevator`). Rumbos: Xola 8,7° del GTFS; San Joaquín sin shape, medir sobre la calle como en San Pedro.

Dos cuidados: el índice entre pathways paralelos se asigna por orden de `miro_id`, así que una estación hermana puede recibir las cuatro escaleras de Portales o los tres pasillos de San Pedro en posiciones permutadas; cada réplica exige comprobar índice ↔ posición con `note:miro_id`. Y hay que resolver con Ricardo qué quiso decir con «2 pares de estaciones casi idénticas»: una hermana por plantilla (Xola y San Joaquín) o dos pares más, es decir, cuatro estaciones.

## Criterios de aceptación

- [ ] `data/osm/xola.osm` y `data/osm/san-joaquin.osm` generados y validados
- [ ] Las diferencias contra Portales y San Pedro caben en la plantilla o quedan anotadas como adiciones
