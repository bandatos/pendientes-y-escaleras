---
type: task
id: task-11
title: Cumplir la política de importación de OSM antes de subir datos
state: open
date: 2026-08-26
owner: ricardo
related: ["[[task-10]]"]
---

# Cumplir la política de importación de OSM antes de subir datos

Subir a OSM datos que vienen de nuestra base/Miro cuenta como importación aunque un humano coloque cada objeto en JOSM. Requisitos de Import/Guidelines y Organised Editing Guidelines:

- Verificar que la licencia del GTFS de CDMX es compatible con ODbL — requisito de sí o no, hay que resolverlo primero.
- Página en el wiki de OSM con la fuente, la licencia, la conversión de campos a etiquetas y el código publicado.
- Aviso en el foro (categoría México, etiquetas `import` e `import-proposal`) y espera de 14 días tras resolver objeciones — ya no es la lista de correo, aunque la guía en español todavía la cita.
- Cuenta dedicada `<usuario>_Import`.
- Conflación contra lo existente (447 accesos ya están en OSM) y también contra lo que Pablo ya subió desde nuestra propia base sin registro de vuelta (escaleras numeradas en Centro Médico y el pasillo elevado de Tlalpan).
- La decisión de sumar nuestros accesos a las relaciones `stop_area` existentes ([[adr-0004]]) contradice la sugerencia de la reunión del 19 de agosto de no usar relaciones: hay que llevarla de vuelta al colectivo antes de subir.
- Página del grupo Bandatos con cuentas y contacto.

Pablo (Bandatos) ya mapea en OSM: validar con él el esquema de etiquetas antes de avanzar.

Ligada a [[task-10|compartir el proyecto en el foro]].

## Criterios de aceptación

- [ ] Está resuelto si la licencia del GTFS de CDMX es compatible con ODbL
- [ ] Existe la página del wiki de OSM con fuente, licencia, conversión de campos y código
- [ ] Se publicó el aviso en el foro con las etiquetas correctas y se esperaron los 14 días
- [ ] Existe la cuenta dedicada `<usuario>_Import`
- [ ] Se hizo la conflación contra los 447 accesos ya existentes en OSM
- [ ] Existe la página del grupo Bandatos con cuentas y contacto
- [ ] Se validó con Pablo el esquema de etiquetas
- [ ] El colectivo conoce y acepta el uso de las `stop_area` existentes
