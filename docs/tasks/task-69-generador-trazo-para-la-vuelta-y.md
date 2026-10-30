---
type: task
id: task-69
title: "Generador: trazo para la vuelta y pasillo en la mitad opuesta del pabellón (L2)"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
---

# Generador: trazo para la vuelta y pasillo en la mitad opuesta del pabellón (L2)

Dos reglas de circulación que Ricardo dictó al revisar las seis estaciones de la L2 de superficie ([[adr-0018]]):

- **Trazo para la vuelta.** Donde dos escaleras paralelas se juntan en un nodo, el pasillo sigue un tramo corto en la misma dirección (largo por confirmar con Ricardo; sus trazos rondan 1 m: entre 0,87 y 1,73 m en las versiones -rick del 30 de octubre; el coordinador había propuesto 2 m sin respuesta) antes de dar la vuelta perpendicular. Hoy la plantilla tiene el tramo `lead` de 4 m de cada escalera al nodo de encuentro, pero no el tramo posterior. Alcanza a las seis estaciones nuevas; a General Anaya y Portales solo si Ricardo lo pide. Probablemente alcanza a toda familia con bancos de escaleras paralelas: preguntar antes de aplicarlo a la L7.
- **Pasillo en la mitad opuesta.** En la L2, entre la entrada y la escalera casi siempre hay un pasillo en la mitad del pabellón opuesta a donde está la escalera. En el lóbulo ancho el generador ya lo hace; falta el lóbulo hondo. El ejemplo es el pasillo que Ricardo agregó en `xola-02-rick.osm` ([[task-59]]).

**Pregunta a Ricardo:** si General Anaya publicada (cuatro escaleras del andén iguales de 9,11 m, torniquetes a ±5, sin trazo para la vuelta) y Portales publicada (sin trazo para la vuelta) se corrigen en OSM para alinearlas con la plantilla, o quedan como están.

## Criterios de aceptación

- [ ] El generador dibuja el tramo para la vuelta, con el largo que confirme Ricardo, tras el nodo de encuentro de un banco
- [ ] En el lóbulo hondo el pasillo de la puerta al banco va por la mitad opuesta a la escalera
- [ ] Ricardo dijo si se aplica a General Anaya, Portales y la L7, y si las dos publicadas se corrigen
- [ ] Prueba en api/utils/osm
