---
type: record
id: 2026-09-01-sesion-miro-corchetes-entrance
date: 2026-09-01
---

# Sesión del 1 de septiembre de 2026: convención de corchetes en Miró, campo `entrance` y tres reimportaciones

Sesión en modo duo (coordinador Fable 5.1, ejecutores Opus 5). Arrancó con una pregunta de Ricardo: qué formatos aceptaba el parser para la marca IZQ/DER después de haber editado el tablero de Miró para que todas las marcas de clasificación fueran entre corchetes. Terminó con una convención documentada ([[adr-0009]]), el campo `Stop.entrance`, cinco `short_name`, dos commands nuevos y el tablero reimportado tres veces. Rama `miro-izq-der-corchetes`.

## Estado de la base en cada reimportación

Respaldo previo: `~/databases/escaleras-local-2026-09-01.sql` (509 KB, PostgreSQL `escaleras-local`).

| Corrida | Motivo | Stops con `miro_id` | Pathways | Levels | `is_double` | Estaciones |
|---|---|---:|---:|---:|---:|---:|
| 0 (previa) | — | 1339 | 2128 | 384 | 28 | 98 |
| 1 | regex de `[IZQ/DER]` solo corchetes | 1332 | 2121 | 384 | 50 | 98 |
| 2 | Ricardo editó textos (entrada/salida → acceso, andenes) y Tacuba | 1332 | 2121 | 384 | 51 | 98 |
| 3 | `entrance`, `short_name`, «(en proceso)», párrafos pegados | 1390 | 2191 | 402 | 52 | 104 |
| 3b | Viveros con `short_name`, andén STE ignorado | 1395 | 2195 | 406 | 52 | 105 |
| 4 (final) | corrida completa de confirmación tras el crítico | 1395 | 2195 | 406 | 52 | 105 |

Las 7 salidas que se perdieron entre 0 y 1 fueron pares IZQ/DER fundidos en un solo nodo `[IZQ/DER]` en Aquiles Serdán (dos pares), Auditorio, Chabacano, Polanco y San Antonio Abad, más Tacuba, cuyo nodo sobreviviente no traía la marca; Ricardo la agregó y entró en la corrida 2. Entre 1 y 2 el grafo fue idéntico: solo cambiaron 28 nombres y 33 descripciones. Estado final de `entrance`: andenes 217 `yes` / 20 `entrance` / 14 `exit`; accesos 449 `yes` / 4 `entrance` / 10 `exit`. `is_closed`: 4 (El Rosario «L6 Acceso oriente», Guerrero «L3 Acceso norponiente» y «L3 Acceso nororiente», Garibaldi y Lagunilla «L8 => central» con `[INHABILITADO]`).

## Inventario de corchetes en el tablero (volcado crudo, 128 frames)

| Marca | Cantidad | Reconocida al inicio de la sesión | Al final |
|---|---:|---|---|
| `[IZQ & DER]` | 42 | sí | sí |
| `[IZQ/DER]` | 9 | sí | sí |
| `[IZQ / DER]` | 1 | sí | sí |
| `[salida]` | 6 | no | `entrance=exit` |
| `[SALIDA]` | 4 | no | `entrance=exit` |
| `[entrada]` | 4 | no | `entrance=entrance` |
| `[CLAUSURADO]` | 4 | no (el parser exigía la A) | `is_closed` |
| `[CLAUSURADA]` | 2 (solo en leyendas) | sí | sí |
| `[INHABILITADO]` | 1 | no | `is_closed` |
| `[STATUS ESPECIAL]` | 1 (leyenda) | no | se descarta |

## Hallazgo: las «palabras pegadas» eran un defecto del parser

«Accesodomo», «Vestíbulotorniquetes», «AndénE», «PasilloTAPO» y «Salida Sur[salida]» no existen en el tablero: son dos párrafos `<p>` consecutivos que `_strip_html` unía sin espacio (para `<br>` sí lo ponía). Afectaba a 25 nodos. Se corrigió sustituyendo cada tag por un espacio. La única errata real era «aceso» en Balderas.

## Ediciones aplicadas en Miró por API (9, todas verificadas antes y después)

- Balderas: «L1 Pasillo vestibular aceso nororiente» → «… acceso nororiente».
- Bondojito, Canal del Norte, Fray Servando, Talismán, Candelaria: «L1 <= Santa Anita» → «L4 <= Santa Anita» (Candelaria no estaba en [[task-7]]).
- Morelos: «L1 Pasillo inferior - cambio de andén» → «LB Pasillo inferior - cambio de andén» (el nodo está en la banda LB Nivel -2 y sus dos conectores van a vestíbulos de LB).
- Títulos de frame: «Escuadron 201» → «Escuadrón 201», «Tezozomoc» → «Tezozómoc» (habrían coincidido igual por la normalización de acentos; la edición es correcta de todos modos).

El token de Miró tiene alcance `boards:write`; el command `apply_miro_edits` quedó en el repo para repetir el procedimiento (simulación por defecto).

## Reporte de revisión del tablero

### Cobertura

De 128 frames, 105 se importan. Fuera: 20 «(en proceso)» (Atlalilco, Calle 11, Culhuacán, Eje Central, Lomas Estrella, Mexicaltzingo, Nopalera, Observatorio, Olivos, Pantitlán, Parque de los Venados, Periférico Oriente, San Andrés Tomatlán, Tasqueña, Tezonco, Tlaltenco, Tláhuac, Zapata, Zapotitlán, más «Copy of Tezonco (en proceso)», que sobra) y 3 diccionarios de leyenda («Dicc complificado», «Dicc detalles», «Dicc niveles por cada línea»).

### Conectores que el importador omite (18 en cada corrida)

- Color fuera del mapa color → PathwayMode (9): Tacuba 3458764661687799415; Hidalgo 3458764659009988019; Guerrero 3458764660784243803; Mixcoac 3458764661687232696; Eugenia 3458764672806283934, 3458764672806283962, 3458764672806283988, 3458764672806284032; Consulado 3458764678225173953. El de Mixcoac no es error: es el conector punteado con diamantes que marca accesos A/B; el importador lo usa para `stop_code` y no debería contarlo como omitido.
- Extremo suelto (4): El Rosario 3458764655662078314 y 3458764655662078412; Hidalgo 3458764659009988018; Guerrero 3458764660784243802.
- Extremos en otro frame (5, ver [[task-21]]): Zócalo 3458764675451631239; Pino Suárez 3458764675592607605; San Antonio Abad 3458764677010013290; Chabacano 3458764677010013340; Deportivo 18 de Marzo 3458764679400728562.
- Textos de nivel no parseables (4): «L7 Nivel Andenes superficie 0», «L6 Nivel Andenes superficie 0» (El Rosario) y «Nivel Andenes superficie 0» ×2 (una en Constitución de 1917).
- Tras excluir el andén del Trolebús en Constitución de 1917, sus 4 conectores quedan como «stop not found».

### Nodos de otros sistemas que sí se importan

En Constitución de 1917: «Acceso poniente Trolebús L-10», «Acceso oriente Trolebús L-10», «Acceso Cablebús L-2» y «Vestíbulo STE L-10». Solo el andén «STE-L10 <= Central» se excluye hoy (prefijo al inicio). Decisión pendiente en [[task-24]].

### Accesos con nombre repetido dentro de una estación y sin descripción que los distinga

Tacubaya «L1 Acceso suroriente» ×3 y «L1 Acceso nororiente» ×3 (una variante ya dice «-- Plaza Charles de Gaulle»); Constitución de 1917 «Acceso nororiente» ×2; División del Norte «Acceso oriente» ×2; Garibaldi y Lagunilla «L8 Acceso suroriente» ×2; Hidalgo «L3 Acceso Norte» ×2; Mixcoac «L12 Acceso Av. Patriotismo» ×2; Salto del Agua «L1 Edificio acceso sur» ×2; Zócalo «Acceso Plaza Constitución Norte» ×2; Insurgentes «Nicho de salida Sur» ×2; Velódromo «descanso» ×4. Los homónimos de mezzanines y vestíbulos son gemelos legítimos por andén.

### Otros

- 33 nodos «Andén» tipados como acceso, exactamente los de [[task-16]]; 13 de ellos llevan `[IZQ & DER]` (Zaragoza «Andén A» a «G», Santa Anita «L4 Andén B» a «G»; «L4 Andén A» de Santa Anita es la única sin marca de su serie).
- Consulado: cuatro nombres terminados en «centralN» / «centralS», que parecen sufijos deliberados.
- «Niños Héroes y Poder Judicial CDMX» tenía el mismo doble espacio que Viveros en el GTFS; ambos corregidos en la canónica, en las copias, al importar y por migración de datos.
- `stop_id` de Moctezuma: guion bajo en `data/gtfs/metro_stops.csv`, guion en la copia de la API ([[task-6]]).

## Revisión del código antes del commit

Un fork revisó el árbol de trabajo completo contra las decisiones de la sesión y lo juzgó listo para commit. Encontró dos casos donde la regla de andenes no aplica por rótulos del tablero, ambos trasladados a [[task-24]]: en El Rosario los andenes de L7 dicen «L7 => Rosario» / «L7 <= Barranca del Muerto» y la regla de terminal compara con «El Rosario», así que los dos quedan `yes` (los de L6 sí funcionan porque dicen «El Rosario»); en Tacubaya solo hay un andén de L9 dibujado y L7 tiene tres, incluido «L7 <= Pantitlán», que no es de L7, así que los seis andenes quedan `yes`.

## Otros conteos finales

- 22 de los 2195 pathways tienen `is_closed=True`: la regla del conector con «X» o trazo gris claro (#e7e7e7) sí se dispara; el coordinador la había dado por no implementada hasta comprobarla en el código.
- `apply_miro_edits` viene con un JSON de ejemplo en `api/utils/miro/apply_miro_edits.example.json`, con el esquema `{"edits": [...]}` que lee el command.

## Corrida final de confirmación

Tras el crítico se corrió una última vez `preview_miro_schema --all-stations --reset` completa: 105 estaciones, 20 «en proceso», 3 sin coincidencia (leyendas). Stops con `miro_id` 1395, pathways 2195, niveles 406; `is_closed` en 4 stops y 22 pathways; `is_double` 52; `short_name` en 5 estaciones; `entrance` sin cambios (andenes 217 `yes` / 20 `entrance` / 14 `exit`; accesos 449 / 4 / 10).

## Medición del gris en los accesos

Para sostener con datos la línea de [[adr-0009]] «el gris es ayuda visual» se midió el color de relleno de los 466 rectángulos de acceso en los frames que no están «(en proceso)» (el volcado de `dump_miro_raw` ahora incluye `style`): 460 amarillo pálido `#fff6b6`; 4 gris `#595959`, los cuatro con `[CLAUSURADO]` (los tres accesos clausurados reales y el de la leyenda); 2 casi negro `#1a1a1a`, que son «L4 Andén F» y «L4 Andén G» de Santa Anita, andenes dibujados como rectángulo ([[task-16]]). Cero accesos grises sin corchete de clausura: la marca escrita basta.

## Crítico de cierre

Antes del commit corrió el agente `critic` sobre la bitácora y el diff. Hallazgos y resolución:

- `short_name` no era reproducible desde cero (solo vivía en la migración de datos): ahora lo puebla también `import_stops` desde `utils/miro/short_names.py`; dónde debe vivir a la larga es la casilla (q) de [[task-24]].
- Contradicción entre el harness y el código: `api/CLAUDE.md` y el skill decían una cosa y el código otra en puntos de la regla de andenes y las marcas; se realinearon con el código final.
- Los cinco nodos nuevos de `docs/` tenían el título H1 duplicado (el body empezaba con el H1 que `doc.mjs create` ya antepone desde `title`): corregido.
- Faltaba el conteo de pathways clausurados (gris/«X»): agregado arriba.
- La exclusión de otros sistemas abarcaba prefijos que no existían en el tablero: reducida a `STE` (casilla (s) de [[task-24]]).
- La comprobación del ADR estaba redactada como hecho consumado antes de la corrida final: reescrita como expectativa.
- No se había propuesto ningún test pese a tocar lógica de parseo y de andenes: propuesta en la casilla (r) de [[task-24]].

## Archivos fuera del repo

Los logs de las reimportaciones, la línea base de la corrida 0, el JSON de ediciones y el script original de aplicación quedaron en `~/respaldos/pendientes-y-escaleras-2026-09-01/`.
