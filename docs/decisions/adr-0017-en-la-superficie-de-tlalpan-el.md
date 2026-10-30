---
type: decision
id: adr-0017
title: En la superficie de Tlalpan el nodo de encuentro de los brazos va a media distancia entre sus ejes (Portales, excepción) y el banco de acceso se orienta por el lado largo del lóbulo, con separación fondo/4 en el lóbulo ancho
state: accepted
date: 2026-10-30
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
affects: ["api/utils/osm/vestibule.py", "api/utils/osm/arms.py", "api/utils/osm/builder.py", "api/utils/osm/template.py", "data/osm/templates/tlalpan-surface.json", ".claude/skills/station-tuning/references/componentes/tlalpan-surface.md"]
related: ["[[adr-0016]]", "[[adr-0009]]", "[[task-45]]"]
---

# En la superficie de Tlalpan el nodo de encuentro de los brazos va a media distancia entre sus ejes (Portales, excepción) y el banco de acceso se orienta por el lado largo del lóbulo, con separación fondo/4 en el lóbulo ancho

## Contexto y planteamiento del problema

El 27 de octubre de 2026 Ricardo decidió que el vestíbulo de nivel 1 del componente de superficie de la Calzada de Tlalpan es el de su edición de Portales (`portales-02-rick`): una pasarela longitudinal sobre el andén con los torniquetes encima y las cuatro escaleras del andén en serie, no la losa transversal con escaleras en abanico que la plantilla generaba ([[task-45]]). Llevarlo a la plantilla dejó abiertas dos reglas que con brazos del puente corridos (10,6 m en Portales, 19,6 m en General Anaya) cambian la geometría: dónde va el nodo de encuentro de los dos brazos sobre la pasarela, y cómo va el banco de acceso dentro de un pabellón (lóbulo del área) cuando el lóbulo es más ancho que hondo, como el oriente de Portales (25,8 × 17,9 m). Sin resolverlas, las seis hermanas de la sesión ([[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]) nacían con el vestíbulo equivocado o con excepciones por estación.

## Criterios de decisión

- Que la plantilla reproduzca lo ya publicado (Portales 05, General Anaya 06) sin excepciones de estación donde se pueda.
- Que la regla sirva para las estaciones que Ricardo no ha visto, y que lo que él ya leyó en JOSM se conserve.
- Reutilizar reglas que ya existen en el componente antes de inventar números de un solo caso.

## Opciones consideradas

**Nodo de encuentro de los brazos.** (1) En el eje del brazo poniente, como en Portales; (2) a media distancia entre los dos ejes, como ya se colocaba el nodo de estación; (3) donde caiga entre los torniquetes. Se renderizaron las tres sobre General Anaya para que Ricardo las viera.

**Portales frente a la regla de media distancia.** La media distancia cae 5,4 m al sur del vestíbulo publicado. (1) Excepción de estación; (2) rige la regla y la próxima afinación mueve lo publicado.

**Banco de acceso en el lóbulo ancho.** Primero se planteó como excepción de Portales (regla del eje del brazo contra el banco a lo largo de la calzada). Ricardo corrigió el planteamiento: la regla estaba mal escrita. Después, la separación entre las dos escaleras en el lóbulo ancho: (a) 4,7 m fijos, el número de Portales; (b) fondo/4, una escalera al centro de cada cuarto del fondo (4,5 m en Portales, 3,4 m en Xola); (c) 1,8 m siempre con Portales como excepción.

**Largo de las escaleras exteriores del andén.** (1) La regla escrita: 12,5 m o el máximo que quepa, y General Anaya conserva su 06 de 9,11 m; (2) «las cuatro iguales», al largo de las interiores.

## Resultado

- **Nodo de encuentro a media distancia entre los ejes de los brazos** (opción 2). Ricardo: «P1. 2, aunque me gustaría ver visualmente las otras opciones solo para corroborar».
- **Portales es excepción de estación**: su vestíbulo y su nodo de encuentro van centrados en el eje del brazo poniente (`stations.0200L2-PORTALES.vestibule`). Ricardo: «P1. Excepción».
- **El banco de acceso se orienta por el lado largo del lóbulo.** Ricardo, textual: «P2. Es una excepción si lo ves así, pero en realidad la regla está mal escrita, se parece más a la lógica de la L7 donde el rectángulo tiene un lado más largo y eso indica la orientación de las escaleras». Lóbulo hondo (fondo mayor o igual que el frente; el empate cuenta como hondo, por convención del ejecutor): el banco va sobre el eje del brazo, a 1,8 m entre ejes, con el pie a 3 m del fondo. Lóbulo ancho: el banco corre a lo largo de la calzada en la mitad del fondo del lóbulo, desde el borde del brazo hacia la punta, con el pie a 3 m del muro de la punta (si no cabe, se acorta con aviso; por debajo de 6 m es error) y la puerta en el medio del tramo de la cara entre la punta y el arranque de las escaleras.
- **Separación en el lóbulo ancho: fondo/4** (opción b). Ricardo: «P1. 2». En los lóbulos hondos sigue 1,8 m. Una estación puede fijarla a mano con `wide_spacing`.
- **Escaleras del andén: rige la regla escrita** (exteriores 12,5 m, interiores lo que quepa con 1,5 m libres). Ricardo, textual: «P3. Tiene sentido que las interiores sean un poco más cortas porque van a la plataforma, eso es lo que preguntaste?»; el coordinador lo leyó como la opción 1. Si General Anaya publicada (cuatro escaleras iguales de 9,11 m, torniquetes a ±5, sin trazo para la vuelta) y Portales (sin trazo para la vuelta) se corrigen, sigue siendo pregunta a Ricardo ([[task-69]]).
- **Las eléctricas de acceso de Tlalpan no son reversibles**, dato de Ricardo: «P3. No son reversibles». San Antonio Abad, que las traía bidireccionales, se corrigió en el tablero de Miró, que es la fuente de los pathways ([[adr-0009]]); Ricardo eligió que el agente corriera el script («P4. 1»).
- **Pendiente: Ricardo decide ±4,1 o ±5 m para los torniquetes.** La plantilla los pone hoy a ±4,1 m del centro, convención del ejecutor (simetría de los +4,02 / −4,19 de Portales 05) que el coordinador presentó como resuelta sin preguntar; General Anaya publicada los tiene a ±5 ([[global:fb-1105]]).

### Consecuencias

- **Bueno:** la plantilla reproduce Portales 05 y General Anaya 06 sin excepción en los bancos (siete de ocho tramos dentro de 1 m) y General Anaya regenerada sale idéntica a antes de la regla del banco; las seis hermanas salieron de la plantilla sin bloque `local`.
- **Malo:** Portales lleva una excepción de vestíbulo que una regeneración debe respetar; la eléctrica oriente de Portales queda a 1,1 m de la 05 por largo (14,05 m publicada contra 12,5 de regla), residuo que el coordinador aceptó sin preguntar (pendiente de Ricardo; ligado a la tolerancia de regeneración de [[task-38]]); la separación fondo/4 sale de un solo caso medido (Portales) y en el lóbulo poniente de Xola acorta el banco a 9,5 m, cosa que Ricardo todavía no confirma ([[task-59]]); General Anaya publicada tiene escaleras exteriores del andén de 9,11 m que la plantilla ya no reproduce.

### Cómo se comprueba

`cd api && .venv/bin/python -m pytest utils/osm -q` (28 pruebas, sin una específica de estas reglas: las propuestas de los ejecutores quedaron sin escribir, en espera de que Ricardo las acepte). Regenerar General Anaya y Portales con `--out` fuera de su carpeta: General Anaya idéntica a la regeneración previa a la regla del banco; Portales dentro de 1 m en bancos, puerta y pasillos salvo la eléctrica oriente. La línea `encaje: brazo …` del reporte del generador dice si cada lóbulo es hondo o ancho.

## Más información

[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]], [[task-45]], [[task-59]]. Prosa vigente en `.claude/skills/station-tuning/references/componentes/tlalpan-surface.md` y `data/osm/README.md`.
