---
type: task
id: task-39
title: Croquis del STC como fuente de la planta subterránea
state: open
date: 2026-10-22
owner: ricardo
source: ["[[2026-10-22-sesion-ciclo-de-afinacion-y-san-joaquin]]"]
related: ["[[task-26]]", "[[task-29]]"]
---

# Croquis del STC como fuente de la planta subterránea

Ricardo trajo el croquis L7-06 de San Joaquín (STC, «Proyecto de espacios publicitarios», 24 de julio de 2002; `~/Descargas/LINEA 7_Page_09.png`, página 9 de un PDF «LINEA 7»). Un agente lo comparó con `san-joaquin-06-claude.osm`; superposiciones y scripts en `.claude/scratch/sj-croquis/` (`overlay_anden_centro.png` es la imagen para mirar primero). Ricardo lo dejó para después: «está interesante que sea super exacto, pero ya es demasiado por ahora».

Cómo se lee: el norte sale de los nombres de las terminales, no del símbolo; 8 px/m a 2540 px de ancho; muros fiables a ±0,5 m; las cotas son de anuncios y no sirven; los planos de vestíbulo son esquemáticos.

Lo que sugiere para San Joaquín, sin decidir:

- Confirma: salidas laterales de 6,6 a 6,9 m (el estándar de 6,5 se sostiene); islas con una sola esquina redonda, la exterior; la fija en medio de dos eléctricas; torniquetes donde los tenemos.
- Cascadas: conjuntos de tres carriles (eléctrica 2,6 m, fija 3,5 m, eléctrica 2,6 m) con ejes a 3,4 m, no 1,8, llenando el pasillo; escaleras de unos 19 m, no 21; pie simétrico a unos 35 m del eje de vías.
- Escaleras de cambio de andén rectas en el eje del pasillo, del muro del andén hacia afuera, unos 7,8 m; el paso bajo las vías mediría 15 m y la senda de −3 rodearía la escalera por un paso de 3,1 m.
- Área unos 7 m corta en las puntas de las cascadas (caja de −2 hasta ±65 m; vestíbulo de −1 con taquilla hasta −70 y +62); bloque central algo más compacto (islas 1,5 a 2 m más cortas, pasillo central de 9,4 a 9,9 m).
- Andenes posiblemente corridos 7 m al sur y de 3,6 a 4 m de ancho (confianza baja a media).
- La mitad del pasillo central queda 14 m (nuestro trazo) a 21 m (croquis) al norte de la mitad del andén.

## Criterios de aceptación

- [ ] Ricardo decide si el croquis entra como fuente y cuáles de sus diferencias se aplican
- [ ] Si existe el PDF completo «LINEA 7», queda localizado y referido para las demás estaciones
- [ ] Ricardo decide si el croquis (y el PDF, si aparece) puede versionarse en `data/sources/`; hoy vive solo en `~/Descargas` y las superposiciones en `.claude/scratch/sj-croquis/`, ignorado por git
