---
type: task
id: task-24
title: "Urgente: revisar al volver: decisiones pendientes de Ricardo tras la sesión del 1 de septiembre de 2026"
state: open
date: 2026-09-01
owner: ricardo
source: ["[[2026-09-01-sesion-miro-corchetes-entrance]]"]
related: ["[[adr-0009]]", "[[task-7]]", "[[task-16]]"]
---

# Urgente: revisar al volver: decisiones pendientes de Ricardo tras la sesión del 1 de septiembre de 2026


Ricardo dejó la sesión en piloto automático para cerrar todo lo cerrable; lo que le toca a él quedó aquí, con el contexto para actuar sin releer la bitácora ([[2026-09-01-sesion-miro-corchetes-entrance]], [[adr-0009]]).

## Criterios de aceptación

- [ ] (a) Regla de escaleras eléctricas bidireccionales «por par de conectores»: el skill `miro-api` la documentaba, pero el código la calcula (`_build_escalator_pairs`) y nunca la usa desde marzo de 2026; hoy el modo 4 sigue la regla de caps de escaleras. Decidir: implementarla o eliminarla del skill.
- [ ] (b) Nodos de otros sistemas que sí se importan en Constitución de 1917: «Acceso poniente Trolebús L-10», «Acceso oriente Trolebús L-10», «Acceso Cablebús L-2», «Vestíbulo STE L-10». Solo el andén «STE-L10 <= Central» se excluye (prefijo al inicio). Dejarlos como correspondencia documentada o ampliar la exclusión a coincidencia por palabra (`Trolebús|Cablebús|Metrobús|STE`); si se excluyen, sus 4 conectores «stop not found» pasan a «other transit system».
- [ ] (c) Borrar en Miró el frame «Copy of Tezonco (en proceso)», duplicado de «Tezonco (en proceso)».
- [ ] (d) Accesos homónimos sin descripción que los distinga: Tacubaya «L1 Acceso suroriente» ×3 y «L1 Acceso nororiente» ×3 (Parque Lira / Erasmo Castellanos según [[task-7]]); Constitución de 1917 «Acceso nororiente» ×2; División del Norte «Acceso oriente» ×2; Garibaldi y Lagunilla «L8 Acceso suroriente» ×2; Hidalgo «L3 Acceso Norte» ×2; Mixcoac «L12 Acceso Av. Patriotismo» ×2; Salto del Agua «L1 Edificio acceso sur» ×2; Zócalo «Acceso Plaza Constitución Norte» ×2; Insurgentes «Nicho de salida Sur» ×2; Velódromo «descanso» ×4.
- [ ] (e) Santa Anita: «L4 Andén A» es el único de la serie A–G sin `[IZQ & DER]`. ¿Real o corchete faltante?
- [ ] (f) Los 33 nodos «Andén» tipados como acceso ([[task-16]]), 13 de ellos con `[IZQ & DER]` (Zaragoza A–G, Santa Anita B–G): revisar con Pablo; por ahora son Entrance/Exit.
- [ ] (g) Consulado: nombres terminados en «centralN» / «centralS» («L4 Pasillo superior dir. Santa Anita centralN», etc.). ¿Sufijos deliberados o pegados?
- [ ] (h) Las 20 frames «(en proceso)»: Atlalilco, Calle 11, Culhuacán, Eje Central, Lomas Estrella, Mexicaltzingo, Nopalera, Observatorio, Olivos, Pantitlán, Parque de los Venados, Periférico Oriente, San Andrés Tomatlán, Tasqueña, Tezonco, Tlaltenco, Tláhuac, Zapata, Zapotitlán. Entran solas en cuanto se quita el sufijo.
- [ ] (i) Validar la revisión del harness de `api/` hecha por el asistente: `api/CLAUDE.md` (sección Módulo Miró: marcas, `entrance`, reglas de andenes, otros sistemas, frames, commands) y `api/.claude/skills/miro-api/SKILL.md`.
- [ ] (j) `TESTING.md` no existe en el repo (la regla global de testing lo pide, con puntero desde `CLAUDE.md`): crearlo o decidir que no aplica todavía.
- [ ] (k) pytest: 16 fallos preexistentes en `api/api/tests.py` (`Stair()` recibe `name`, campo inexistente) y los scripts `api/utils/miro/scratch/test_*.py` rompen la recolección; hoy se corre con `--ignore=utils/miro/scratch` ([[task-12]]).
- [ ] (l) `stop_id` de Moctezuma: `0200L1_MOCTEZUMA` (guion bajo) en `data/gtfs/metro_stops.csv` frente a `0200L1-MOCTEZUMA` en `api/media/gtfs_metro/stops_metro.csv` ([[task-6]]).
- [ ] (m) Revisar `~/respaldos/pendientes-y-escaleras-2026-09-01/` (logs de reimportación, línea base, JSON de ediciones ya aplicadas, script original) y borrarlo si no sirve.
- [ ] (n) Merge de la rama `miro-izq-der-corchetes` (con push) a `monorepo`.
- [ ] (o) El Rosario L7: el tablero rotula los andenes terminales «L7 => Rosario» / «L7 <= Barranca del Muerto»; la regla de terminal compara la dirección con el nombre de la estación «El Rosario» y no reconoce «Rosario», así que los dos andenes de L7 quedan `yes` (L6 en la misma estación sí funciona porque dice «El Rosario»). Decidir: relajar la comparación (aceptar la dirección como sufijo del nombre) o corregir el rótulo en Miró.
- [ ] (p) Tacubaya: solo hay un andén de L9 dibujado («L9 <= Tacubaya») y L7 tiene tres andenes, incluido «L7 <= Pantitlán», que no es de L7 (probablemente un andén de L9 mal rotulado); los seis andenes de Tacubaya quedan `yes`. Corregir en Miró.
- [ ] (q) `short_name` se puebla ahora desde `import_stops` con el mapa de `api/utils/miro/short_names.py` (código), además de la migración de datos `0011`. Alternativa si se prefiere dato sobre código: una columna `short_name` en `data/gtfs/metro_stops.csv` y en la copia de la API. Decidir dónde vive.
- [ ] (r) Propuesta de tests, para recortar o descartar: unitarios de `assign_platform_entrances` (terminal, tres andenes con central, dos no terminales, andén STE excluido, dirección abreviada como «Rosario»); de `_parse_content` con las marcas aceptadas y rechazadas (`[IZQ/DER]`, `[IZQ & DER]`, `(IZQ & DER)`, `[DER/IZQ]`, `[CLAUSURADO]`, `[INHABILITADA]`, `[salida]`, `[ENTRADA]`); de `_is_in_progress` y `_normalize_title`; y del orden de `resolve_station_stops` (`short_name` → `stop_name` → normalizado).
- [ ] (s) `_OTHER_SYSTEMS_RE` quedó reducida a `STE`: los prefijos `MB|CBB|TL` que se habían puesto eran anticipatorios y no coincidían con ningún nodo del tablero. Confirmar que basta o ampliar cuando aparezca otro sistema.
- [ ] (t) `import_stops` no corre sobre una base limpia (`zone_id` eliminado en `0007`, `location_type` como entero, `LocationType` sin sembrar): decidir entre las opciones (a) y (b) de [[task-25]].

## Notas de trabajo

- 2 de septiembre de 2026: `TESTING.md` sigue sin existir (inciso j); la sesión nocturna de [[2026-09-02-sesion-primeras-dos-estaciones-josm]] no tocó código con pruebas. La regla global de testing pide ofrecerle a Ricardo crear `TESTING.md`; todavía no se le ha ofrecido, se le pregunta en el mensaje de la mañana. El inciso (a), regla de pares de escaleras eléctricas, tiene ahora un dato más: [[fb-2]] y [[adr-0010]] toman la flecha de Miró como sentido de las unidireccionales.
