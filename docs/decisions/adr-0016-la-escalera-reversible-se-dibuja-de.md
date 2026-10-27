---
type: decision
id: adr-0016
title: La escalera reversible se dibuja de arriba hacia abajo con incline=down, y el catálogo recibe la publicación, la boca en el anillo, los conectores evidentes y el par a 3,0 m
state: accepted
date: 2026-10-27
origin: ricardo
deliberation: confirmed
rationale: recorded
source: ["[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]"]
supersedes: "[[adr-0012]]"
affects: ["api/utils/osm/tags.py", "api/utils/osm/builder.py", "api/utils/osm/validate.py", "api/utils/osm/publish.py", "api/stop/management/commands/publish_station_osm.py", "data/osm/templates/l7-deep-cascade.json", ".claude/skills/station-tuning/references/general.md", ".claude/skills/station-tuning/references/componentes/"]
related: ["[[adr-0010]]", "[[adr-0011]]", "[[adr-0013]]", "[[adr-0015]]", "[[task-11]]"]
---

# La escalera reversible se dibuja de arriba hacia abajo con incline=down, y el catálogo recibe la publicación, la boca en el anillo, los conectores evidentes y el par a 3,0 m

## Contexto y planteamiento del problema

[[adr-0012]] decidió que la escalera eléctrica bidireccional se dibuja de abajo hacia arriba con `incline=up` y `conveying=reversible`, porque OSM no expresa el sentido habitual de una reversible; [[adr-0013]] lo recogió en el catálogo y `validate.py` lo exigía. Esa práctica se había corroborado contra la wiki de OSM y 32 637 escaleras del mundo ([[2026-10-21-sesion-san-pedro-a-plantilla-y-san-joaquin]]).

El 26 de octubre de 2026 Pablo, analista de campo de Bandatos, devolvió San Joaquín con las cuatro reversibles invertidas: dibujadas de arriba hacia abajo. Un turno las restauró de oficio y Ricardo corrigió: fue intencional, Pablo sabe mejor y se le hace caso; la reversible de cada trío tiene por sentido principal bajar y así se dibuja, aunque contradiga el ADR. Ricardo confirmó la lectura exacta el 27 de octubre: la reversible de cada trío va de arriba hacia abajo con `incline=down`; fijas y eléctricas de subida siguen de abajo hacia arriba con `incline=up`.

La misma sesión produjo cuatro convenciones más que [[adr-0013]] no tenía y que este ADR consolida, porque el catálogo es el estado vigente y no debe leerse con enmiendas sueltas.

## Criterios de decisión

- El dato de campo de Pablo manda sobre la convención estadística.
- La etiqueta debe acompañar al sentido de dibujo: `incline` se lee en el orden de los nodos, y una reversible dibujada cuesta abajo con `incline=up` dice lo contrario de lo que se quiso.
- El catálogo vigente debe poder leerse solo.

## Opciones consideradas

- **A. Mantener [[adr-0012]]** (de abajo hacia arriba, `up`) y restaurar lo de Pablo. Es lo que hizo el turno de San Joaquín 08 antes de la corrección.
- **B. Reversible de arriba hacia abajo con `incline=down`**, fijas y de subida hacia arriba con `up`.
- **C. Por escalera**, también las fijas que la gente usa sobre todo para bajar. Ricardo no la pidió; se descarta hasta que Pablo diga algo distinto.

## Resultado

Se eligió **B**. Se aparta a sabiendas de la práctica observada en OSM; lo decide el relevamiento de campo.

Lo demás que este ADR fija en el catálogo, por decisión de Ricardo del 26 y 27 de octubre:

- **Publicación.** Las versiones de trabajo conservan `upload='never'` y las etiquetas de traza. Para subir, `publish_station_osm` escribe `<slug>-NN-pub.osm` sin `note:*` y sin el atributo `upload`, fuera de la cadena de versiones (el autor `pub` no cuenta como turno). Reemplaza la frase de [[adr-0013]] «retiradas con `--no-trace` antes de cualquier subida», que no servía para archivos editados a mano. Las relaciones `stop_area` del servidor quedan ausentes del archivo, nunca con `action='delete'` (acuerdo con Pablo). El changeset lleva `source=survey` e `imagery_used=Esri World Imagery`; el comentario corto en `comment` (255 caracteres) y el largo en la discusión del changeset. Las primeras estaciones se publican como mapeo manual con cuenta personal, no como import ([[task-11]] sigue para la escala completa).
- **Boca de acceso a cielo abierto.** Es la entrada de OSM movida a la punta de la pestaña del área y es vértice del anillo exterior: excepción explícita a «el área solo comparte nodos con edificios» de [[adr-0011]]. No aplica a accesos con edificio (San Antonio oriente).
- **Conectores a la banqueta.** Solo cuando hay un enlace corto y evidente a una banqueta mapeada; si no, la boca queda sin conector y no se inventa un trazo. El automático de 45 m del generador es provisional.
- **Par de −1 a 0 de la cascada L7.** 3,0 m entre ejes y paralelas; los tríos siguen a 1,8 m.
- **Pabellón de Tlalpan.** El lóbulo del área es el pabellón y no lleva `building` propio; una sola puerta, hacia la Calzada.

### Consecuencias

- **Bueno:** los archivos dicen lo que Pablo relevó; el catálogo vuelve a leerse completo en un solo lugar con [[adr-0013]].
- **Malo:** nos apartamos de la práctica mayoritaria de OSM en las reversibles; un mapeador externo puede «corregirlo». El validador ya solo avisa de una reversible con `incline=up` (una familia con `reversible_runs: up` sigue siendo legítima), así que la forma vieja no truena, solo avisa.

### Cómo se comprueba

`api/utils/osm/test_reversible.py` (la reversible baja con `incline=down` sin importar el sentido del pathway; el validador acepta la coherente y marca la incoherente) y `test_publish.py` (la copia `-pub` sin traza ni `upload`, fuera de la cadena). Las seis versiones aprobadas del 27 de octubre traen las reversibles con `down`.

## Más información

[[2026-10-27-sesion-seis-estaciones-afinadas-y-primera-publicacion]]. La prosa vigente está en `.claude/skills/station-tuning/references/general.md` y en los componentes `cascada-san-pedro.md`, `acceso-cielo-abierto.md` y `tlalpan-surface.md`.
