---
type: decision
id: adr-0012
title: "Sentido de las escaleras eléctricas: la flecha de Miró es el sentido real en las unidireccionales, las bidireccionales se dibujan del nivel alto al bajo, y la regla de pares se retira"
state: accepted
date: 2026-09-02
origin: ricardo
deliberation: confirmed
rationale: recorded
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]", "[[fb-2]]"]
affects: ["api/utils/osm/tags.py", "api/utils/osm/builder.py", "api/utils/miro/pathway_mixin.py", "api/.claude/skills/miro-api/SKILL.md"]
related: ["[[adr-0010]]", "[[task-24]]"]
---

# Sentido de las escaleras eléctricas: la flecha de Miró es el sentido real en las unidireccionales, las bidireccionales se dibujan del nivel alto al bajo, y la regla de pares se retira

## Contexto y planteamiento del problema

[[adr-0010]] tomó la flecha de Miró como sentido de las eléctricas unidireccionales sin confirmación de Ricardo; [[fb-2]] registró la medición y esperaba su palabra. Aparte, el skill `miro-api` documentaba una «regla de pares» (una eléctrica es bidireccional si hay dos conectores entre el mismo par de nodos) que el importador calcula pero nunca usa ([[task-24]], inciso a), y la convención con que el equipo dibujó las bidireccionales no estaba escrita en ningún lado.

## Criterios de decisión

- Una sola verdad sobre el sentido, verificable contra el tablero.
- Que la convención de dibujo del equipo quede escrita antes de que alguien la reinterprete.

## Opciones consideradas

- **Flecha de Miró como sentido real** — lo que el equipo hizo a propósito.
- **Regla de pares** — deducir bidireccionalidad de la existencia de dos conectores; no aplica en general, porque la de subida y la de bajada suelen llegar a descansos distintos.

## Resultado

- **Unidireccionales**: la flecha de Miró es el sentido real de la máquina. Confirmado por Ricardo. Medición en la base por diferencia de nivel: Línea 7, 77 suben, 18 bajan, 0 al mismo nivel; toda la red, 241 suben, 50 bajan, 4 al mismo nivel. El exportador las dibuja de origen a destino con `incline` según los niveles, `conveying=forward` y `oneway:foot=yes`.
- **Bidireccionales**: en Miró el origen es el nivel alto y el destino el bajo, porque normalmente bajan y se configuran para subir cuando la paralela de subida se descompone. El exportador las redibuja de abajo hacia arriba con `incline=up` y `conveying=reversible`; OSM no expresa el sentido habitual de una reversible.
- **Regla de pares**: se retira del skill `miro-api` y no se implementa. En L7, corrida una vez sobre 86 pares de nodos, 38 cumplen «bidireccional + sube», 36 solitarias en Aquiles Serdán, Camarones y Refinería están bien así, y 7 que solo suben sin gemela quedan por validar ([[task-34]]).

### Consecuencias

- **Bueno:** una regla por sentido, y la convención de dibujo escrita.
- **Malo:** si una flecha está mal en Miró, `incline`, `conveying` y `oneway:foot` se invierten juntos; solo se detecta en campo.

### Cómo se comprueba

`validate.py` exige `incline=up` en toda `conveying=reversible`; el skill `miro-api` ya no describe la regla de pares.

## Más información

[[fb-2]], [[2026-09-02-sesion-integracion-osm-y-niveles]].
