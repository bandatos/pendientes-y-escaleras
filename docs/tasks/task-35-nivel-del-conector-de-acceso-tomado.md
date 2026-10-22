---
type: task
id: task-35
title: Nivel del conector de acceso tomado de la way destino
state: open
date: 2026-10-21
owner: ai
source: ["[[global:fb-335]]"]
related: ["[[task-26]]", "[[adr-0011]]", "[[adr-0014]]"]
---

# Nivel del conector de acceso tomado de la way destino

Sale del feedback fb-3 del proyecto (capturado el 2 de septiembre de 2026 como [[global:fb-335]] y trasladado aquí el 5 de septiembre), que el 2026-10-21 se convirtió en esta task porque en un proyecto con cliente no se mantiene feedback local; ese mismo día se retiró toda la carpeta de feedback del proyecto y esta task quedó como el lugar de su contenido en el repo. El [[global:fb-335]] del grafo global sigue pendiente con la misma propuesta (Ricardo lo devolvió a pendiente al arreglar su enlace); se resuelve allá cuando esta task cierre. El contexto: tras el hallazgo del crítico de que los tramos de Portales se colgaban de un puente peatonal con `bridge=yes` y `layer=2`, el coordinador ordenó la exclusión que Ricardo revirtió.

## Lo que dijo Ricardo

El 2 de septiembre de 2026, cuando el coordinador ordenó excluir puentes, túneles y toda way con `layer` o `level` distinto de 0 como candidatas de conexión, Ricardo lo revirtió:

> hay muchos muchos accesos del metro que no están a nivel de calle, no estoy seguro de la decisión que tomaste de excluir puentes y túneles. Revierte eso, ya veré en la próxima sesión cómo arreglo eso que pasó en Portales

## La propuesta que quedó en el feedback fb-3

Redactada por el coordinador de esa sesión, no por Ricardo: «un acceso del Metro se conecta a la vía peatonal más cercana sea cual sea su nivel; el nivel del tramo de conexión se toma de la way destino, no se fija en 0».

## Estado del código al 2026-10-21

- La parte «no excluir puentes ni túneles» está hecha: `data/osm/README.md` (paso 1 de «Cómo se arma el archivo») dice que no se filtra por altura.
- La parte del nivel no: `api/utils/osm/tags.py` `connector_tags()` devuelve `level=0` fijo y `StationBuilder._build_connectors` en `api/utils/osm/builder.py` registra el way con niveles `[0.0]`. El `target` del feedback fb-3 decía `api/utils/osm/overpass.py`, pero el cambio cae en `builder.py` y `tags.py`.
- El síntoma sigue anotado al final de `data/osm/README.md` («Los connectors de Portales llegan al puente, no a la banqueta»): los accesos de Portales se conectan a la way 43763067 (`bridge=yes` + `layer=2`) con un connector `level=0`.
- En la edición a mano de Portales del 2 de septiembre (`~/Descargas/portales(1).osm`, ver [[2026-09-30-imagenes-sotm-evolucion-portales]]) Ricardo borró esa pasarela y los dos accesos adoptados; eso resolvió el caso de Portales en su archivo, no la regla del generador.

## Preguntas que la propuesta no cierra (de Ricardo)

- La way destino puede no llevar `level`: la 43763067 lleva `layer=2` y no `level`. ¿Se deriva `level` de `layer`, se deja el connector sin `level`, o se conserva `level=0` cuando el destino no lo declara?
- El acceso está en `level=0`. Si la way destino está en otro nivel, un connector recto de un solo nivel dice que se pasa de un nivel a otro sin escalera. ¿El connector lleva `level=0;<destino>`, se emite el nivel del destino y se avisa, o un destino de otro nivel deja de ser candidato salvo que haya escalera de OSM?

## Criterios de aceptación

- [ ] Ricardo decide las dos preguntas de arriba
- [ ] El connector sale con el nivel que él decida y la validación cubre el caso de un destino sin `level`
- [ ] `data/osm/README.md` deja de describir el connector como `level=0` fijo y el supuesto «Los connectors de Portales llegan al puente» queda resuelto o reescrito
