---
type: task
id: task-66
title: "Generador: operaciones sobre ways de OSM desde la plantilla (borrar con delete_osm, adoptar un edificio como lóbulo)"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-55]]"]
---

# Generador: operaciones sobre ways de OSM desde la plantilla (borrar con delete_osm, adoptar un edificio como lóbulo)

Hoy el generador no sabe borrar ways de OSM: el puente peatonal que cae sobre el área (regla general) se borra a mano o con script en cada estación, y regenerar lo pierde. Pasó el 27 de octubre de 2026 en Nativitas (puente 43763069), Villa de Cortés (puente 221926316 y el edificio 1488931042), Ermita (puente 43763058 y la escalera 1304926070) y antes en Portales 05. Propuesta del trazador de Nativitas: un `delete_osm` por estación en el bloque de la plantilla. Cuando se borra un puente sobre el área, también sus escaleras de OSM dentro del área (caso de Ermita).

Mismo mecanismo, otro caso (San Antonio Abad): cuando OSM tiene un `building` que coincide con un lóbulo (desfase menor a 1 m), el lóbulo debería tomar la forma del edificio con la puerta insertada en su muro, versión en Tlalpan de «se adopta, no se duplica». Ricardo lo aceptó para San Antonio Abad («P10. Lo veo bien»).

Tercer caso, el nombre del contorno ([[adr-0018]]): Ricardo decidió los contornos sin «Metro» («Xola», «Viaducto», «Villa de Cortés»), pero ante un conflicto de `name` el generador conserva el de OSM, así que una regeneración vuelve a poner «Metro Xola». El bloque de estación, o una regla de la familia, debe poder imponer nuestro nombre al contorno adoptado.

## Criterios de aceptación

- [ ] Un bloque de estación puede declarar ways de OSM a borrar y el archivo los lleva con action=delete
- [ ] Regenerar Nativitas, Villa de Cortés y Ermita reproduce sus bajas sin script
- [ ] Regenerar Xola, Viaducto y Villa de Cortés da el contorno sin «Metro»
- [ ] Prueba en api/utils/osm
