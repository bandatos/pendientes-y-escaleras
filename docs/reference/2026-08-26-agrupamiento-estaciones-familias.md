---
type: reference
id: 2026-08-26-agrupamiento-estaciones-familias
title: Agrupamiento de estaciones del Metro CDMX en familias arquitectónicas
state: current
date: 2026-08-26
---

# Agrupamiento de estaciones del Metro CDMX en familias arquitectónicas

Documento de trabajo para el mapeo en OpenStreetMap por estaciones plantilla. Propuesta generada el 26 de agosto de 2026; está pensada para que la corrijas a mano moviendo estaciones entre listas (ver «Cómo corregir este documento» al final).

## Método y confianza

Las 163 estaciones del Metro (195 pares estación-línea, porque las correspondencias cuentan una vez por línea) se agruparon combinando cuatro fuentes. La primera y más fuerte es la topología levantada en Miro y cargada en la base: 98 estaciones tienen grafo interior completo (`Stop` de tipo andén, acceso y nodo genérico, con `Level`, más `Pathway` con modo pasillo / escalera fija / escalera eléctrica / elevador). La segunda es el trazo de cada línea con su tramo subterráneo, superficial o elevado. La tercera son los polígonos del KML de las áreas de estación (área, longitud, anchura y elongación del rectángulo mínimo), que separan bien las estaciones alargadas de viaducto de las cajas compactas. La cuarta es el conteo de escaleras del modelo legado `Stair`, que cubre 84 estaciones y da una señal débil pero útil donde no hay topología.

Para las 98 con topología se calculó una **firma estructural**: número de andenes y su `level_index`, número de accesos y su nivel, número de nodos intermedios y sus niveles, el papel de cada nodo según su nombre (vestíbulo de andén, pasillo inferior de cambio de andén, edificio de acceso, mezzanine, torniquetes, pasillo de correspondencia) y el conteo de aristas por modo. Sobre esa firma se corrió además un hash de Weisfeiler-Lehman para detectar isomorfismos exactos entre grafos. El hash exacto resultó demasiado fino —107 clases para 129 subgrafos línea-estación—, así que las familias se definieron sobre la firma estructural gruesa, que es la que corresponde a «misma arquitectura, distinto número de accesos».

**El hallazgo que ordena todo el documento confirma tu intuición sobre Ermita.** El subgrafo de L2 de Ermita es idéntico, nodo por nodo y arista por arista, al de Portales, General Anaya, Nativitas, Viaducto, Villa de Cortés y Xola: un andén central, un vestíbulo con torniquetes arriba, dos pasillos vestibulares, dos edificios de acceso y dos accesos a la calle. Ermita pertenece de lleno a esa familia; su condición de correspondencia es una **adición** (un pasillo de trasbordo hacia una estación de L12 que es, arquitectónicamente, otra estación pegada al lado). Por eso todas las familias de abajo se describen como «base + adiciones», y las correspondencias se asignan a la familia de su base siempre que la base sea reconocible.

Las adiciones que se registran por estación son: correspondencia (con las líneas), terminal, presencia de elevador, número de accesos cuando excede el de la base, y número de escaleras eléctricas. Todas se leen en el CSV adjunto.

Sobre la **confianza**: «confirmada» significa que la estación tiene topología en la base y su firma coincide con la de la familia. «Provisional» significa que la asignación viene de línea + tramo + forma del KML + escaleras legadas, sin grafo que la respalde; hay que verificarla en campo o en satélite antes de duplicar la plantilla. «Individual» marca las estaciones que no se agrupan y deben mapearse una por una.

Dos advertencias sobre los datos. Primera: **283 grupos de `Pathway` comparten la tupla exacta (origen, destino, modo, bidireccionalidad), con 444 aristas excedentes sobre 2126 totales**. Contra lo que parece, no son duplicados de importación: cada una tiene un `miro_id` distinto, y corresponden a elementos físicos paralelos reales (los cuatro tramos de escalera fija que bajan del puente al andén en Portales, los tres escalones mecánicos contiguos de un tramo de L7). Por eso las firmas se calcularon **conservando la multiplicidad**, no deduplicando: deduplicar habría borrado justamente el dato de cuántas escaleras hay. Segunda: hay estaciones con levantamiento incompleto o con errores de prefijo en Miro, detallados en «Casos que no encajan».

---

## Familia A — Cajón clásico con edificio de acceso

*(mi etiqueta: «cajón clásico con edificio de acceso»)*

**Firma.** Dos andenes laterales al nivel -1. Cada andén tiene su propio vestíbulo de andén al mismo nivel -1, y ambos vestíbulos se conectan entre sí por un **pasillo inferior de cambio de andén al nivel -2**, que pasa por debajo de las vías. Desde cada vestíbulo sube una escalera a un **edificio de acceso en superficie** (nivel 0), y de ahí se sale a la calle por un pasillo a nivel. Suele haber una escalera eléctrica de subida por lado. Es la estación de las primeras líneas construidas a cielo abierto (L1, L2, L3) más algunas de L8; la variante con edificio de acceso es la que distingue esta familia de la B.

**Estación modelo: Cuitláhuac (L2).** Es la más limpia: dos accesos, sin correspondencia, sin terminal, con el edificio de acceso claramente separado del vestíbulo y una sola escalera eléctrica. Construida ella, las 24 restantes se obtienen replicando y ajustando el número de accesos.

**Miembros** (todos con topología, todos confirmados): Allende (L2), Balbuena (L1), Balderas (L1+L3), Bellas Artes (L2+L8), Boulevard Puerto Aéreo (L1), Colegio Militar (L2), Cuauhtémoc (L1), Cuitláhuac (L2), Eugenia (L3), Guerrero (L3+LB), Gómez Farías (L1), Hidalgo (L2+L3), Hospital General (L3), Insurgentes (L1), Isabel la Católica (L1), Juanacatlán (L1), Juárez (L3), Normal (L2), Popotla (L2), Revolución (L2), San Cosme (L2), San Juan de Letrán (L8), Sevilla (L1), Tacuba (L2+L7), Zaragoza (L1).

**Adiciones notables.** Balderas, Bellas Artes, Guerrero, Hidalgo y Tacuba suman pasillo de correspondencia y accesos extra (Bellas Artes e Hidalgo tienen ocho accesos cada una); Tacuba añade además la estación profunda de L7, que pertenece a la familia G. Zaragoza tiene nueve accesos, la más ramificada de la familia. Insurgentes y Juanacatlán no tienen escalera eléctrica.

## Familia B — Cajón con acceso directo a la calle

*(mi etiqueta: «cajón con acceso directo a la calle»)*

**Firma.** El mismo esqueleto que la familia A —dos andenes laterales a -1, un vestíbulo de andén por lado, un pasillo inferior de cambio de andén a -2— pero **sin edificio de acceso**: desde cada vestíbulo de andén sube una escalera fija que desemboca directamente en el acceso a la calle. El caso canónico tiene cuatro accesos, dos por lado, en configuración perfectamente especular. Es la estación estándar de las líneas de los años ochenta y noventa (L6, L8, L9, LB) y de algunos tramos de L1, L2 y L3.

**Estación modelo: Doctores (L8).** Nueve nodos, ocho aristas, simetría especular exacta: dos andenes, dos vestíbulos, un pasillo inferior, cuatro accesos. No tiene escaleras eléctricas ni elevador, así que es la plantilla mínima; Lindavista y Norte 45 (L6) son la misma estación con dos accesos en lugar de cuatro.

**Miembros con topología (confirmadas):** Cerro de la Estrella (L8), División del Norte (L3), Doctores (L8), Iztapalapa (L8), La Viga (L8), Lagunilla (LB), Lindavista (L6), Lázaro Cárdenas (L9), Mixiuhca (L9), Moctezuma (L1), Morelos (L4+LB), Niños Héroes y Poder Judicial CDMX (L3), Norte 45 (L6), Obrera (L8), Panteones (L2), Pino Suárez (L1+L2), Salto del Agua (L1+L8), Tepito (LB), UAM-I (L8).

**Miembros provisionales (sin topología):** Escuadrón 201 (L8), Etiopía y Plaza de la Transparencia (L3), Merced (L1), Miguel Ángel de Quevedo (L3), Potrero (L3), Ricardo Flores Magón (LB), Romero Rubio (LB), Tlatelolco (L3), Viveros y Derechos Humanos (L3).

**Adiciones notables.** Morelos, Pino Suárez y Salto del Agua son correspondencias con pasillo añadido y accesos extra; Pino Suárez llega a ocho accesos y ocho escaleras eléctricas. División del Norte y Moctezuma tienen seis accesos. La Viga carece del pasillo inferior a -2 (sus dos andenes solo se comunican por el vestíbulo), lo cual es una diferencia real, no un error de levantamiento: verifícala antes de duplicar.

## Familia C — Cajón profundo de vestíbulo único

*(mi etiqueta: «cajón profundo de vestíbulo único»)*

**Firma.** Dos andenes laterales a un nivel más profundo, -2 o -3, y **un solo vestíbulo con torniquetes en el nivel intermedio -1** que sirve a los dos andenes, en lugar de los dos vestíbulos separados de las familias A y B. No hay pasillo inferior: el cambio de andén se hace por arriba, en el vestíbulo. Algunas tienen además un mezzanine intercalado. Es la solución de las estaciones que quedaron bajo avenidas anchas o bajo edificación, y es la arquitectura de todo el tramo poniente de L12.

**Estación modelo: Coyoacán (L3).** Es la única de la familia sin ninguna adición: dos andenes a -2, un vestíbulo a -1, tres accesos, once escaleras fijas y nada más. Si prefieres una con escalera eléctrica para tener el elemento en la plantilla, usa Hospital 20 de Noviembre (L12).

**Miembros con topología (confirmadas):** Centro Médico (L3+L9), Chapultepec (L1), Chilpancingo (L9), Copilco (L3), Coyoacán (L3), Hospital 20 de Noviembre (L12), Insurgentes Sur (L12), Patriotismo (L9), Vallejo (L6), Zócalo (L2).

**Miembros provisionales (sin topología, todos L12 poniente):** Eje Central, Mexicaltzingo, Parque de los Venados, Zapata (L3+L12).

**Por qué las cuatro de L12 caen aquí.** Las dos únicas estaciones del tramo poniente de L12 que sí tienen levantamiento —Hospital 20 de Noviembre e Insurgentes Sur— dan exactamente esta firma, y las cuatro restantes comparten línea, tramo, época constructiva y forma del KML (rectángulos de unos 155 × 40 m, elongación entre 4,2 y 5,2). Es la extrapolación mejor fundada del documento, pero sigue siendo provisional.

**Adiciones notables.** Centro Médico suma correspondencia a L9, nueve accesos y doce escaleras eléctricas; su subgrafo de L9, aislado, es idéntico al de Chilpancingo. Zócalo tiene ocho accesos repartidos en el perímetro de la plaza y un polígono KML anómalo (774 m de largo, elongación 27), reflejo de que el área dibujada abarca la plaza entera y no la estación.

## Familia D — Superficie de Calzada de Tlalpan

*(mi etiqueta: «superficie de Calzada de Tlalpan»)*

**Firma.** Un **andén central único a nivel de calle (0)**, en el camellón de la avenida. Encima, a +1, un vestíbulo con torniquetes sobre un puente que cruza la calzada, del que salen dos pasillos vestibulares, uno a cada lado. Cada pasillo baja por escalera fija y escalera eléctrica a un edificio de acceso a nivel de banqueta (0), y de ahí a la calle. Cuatro tramos de escalera fija comunican el andén con el vestíbulo. La estación es perfectamente especular respecto del eje de la avenida.

**Estación modelo: Portales (L2).** Ocho nodos, once aristas, sin ninguna adición. Es la plantilla más pequeña y más reutilizable del sistema entero.

**Miembros** (todos con topología, todos confirmados): Ermita (L2+L12), General Anaya (L2), Nativitas (L2), Portales (L2), San Antonio Abad (L2), Viaducto (L2), Villa de Cortés (L2), Xola (L2).

**Adiciones.** Ermita añade el pasillo de trasbordo a L12 y, con él, toda la estación profunda de L12 (dos andenes a -3, cascada de mezzanines de -2 a +1, tres elevadores, diez escaleras eléctricas). Trátala como «Portales + estación de L12 adosada», no como una estación distinta. San Antonio Abad tiene cuatro accesos en vez de dos.

**Nota.** Tasqueña, terminal del mismo tramo, quedó en la familia O porque su condición de terminal con andenes de maniobra domina la arquitectura.

## Familia E — Viaducto elevado de L8 (Churubusco)

*(mi etiqueta: «viaducto elevado de L8»)*

**Firma.** Andén central único sobre el viaducto (nivel 0 en la convención del levantamiento), con vestíbulos y torniquetes a +1, norte y sur, unidos por pasillos de acceso. Lo característico es la **enorme cantidad de accesos, entre diez y doce**, repartidos en dos alturas: accesos a nivel de calle bajo el viaducto y accesos elevados a +2 conectados a los puentes peatonales y a las estaciones de Metrobús Línea 5. Tres tramos de escalera fija bajan del vestíbulo norte al andén.

**Estación modelo: Aculco (L8).** Once accesos, dieciocho nodos, diecinueve aristas; Apatlaco es su gemela exacta.

**Miembros** (todos con topología, todos confirmados): Aculco (L8), Apatlaco (L8), Coyuya (L8), Iztacalco (L8).

**Adiciones.** Solo varía el número de accesos: Iztacalco diez, Aculco y Apatlaco once, Coyuya doce. Ninguna tiene escalera eléctrica ni elevador levantado.

## Familia F — Elevada de L4 (Circuito Interior)

*(mi etiqueta: «elevada de L4»)*

**Firma.** Dos andenes laterales sobre el viaducto, al nivel +2. Debajo, a +1, dos mezzanines, uno por sentido; encima, a +3, cuatro pasillos superiores que permiten el cambio de andén cruzando por arriba de las vías. Los vestíbulos con torniquetes están separados por sentido, de modo que la estación son en realidad dos mitades independientes unidas solo por los pasillos superiores. Cuatro niveles en juego (0 a +3), diez nodos intermedios y solo dos accesos, uno poniente y uno oriente.

**Estación modelo: Bondojito (L4).** Canal del Norte y Talismán son idénticas a ella; Fray Servando difiere solo en un nodo y añade dos escaleras eléctricas.

**Miembros** (todos con topología, todos confirmados): Bondojito (L4), Canal del Norte (L4), Fray Servando (L4), Talismán (L4).

**Advertencia de datos.** En las cuatro, el segundo andén está capturado en Miro con prefijo `L1-` en lugar de `L4-` (`L1-BONDOJITO-P-01`, etc.), queda desconectado del grafo y no tiene ninguna arista. Es un error sistemático de captura, no una diferencia arquitectónica; hay que corregirlo antes de usar estas estaciones como fuente.

## Familia G — Profunda de L7 en cascada

*(mi etiqueta: «profunda de L7 en cascada»)*

**Firma.** Dos andenes laterales muy profundos, entre -3 y -5, y una **cadena vertical de mezzanines** que sube nivel por nivel hasta la calle: cada tramo entre mezzanines lleva su escalera fija y una o dos escaleras eléctricas, una de subida y otra de bajada. Es la única familia donde la escalera eléctrica es estructural y no una adición: entre ocho y dieciséis por estación. El polígono del KML es compacto y casi cuadrado (elongación entre 1,1 y 1,7), porque la estación se resuelve en vertical y no en horizontal.

**Estación modelo: San Joaquín (L7).** San Pedro de los Pinos tiene exactamente el mismo grafo, hasta el hash; levantar una es levantar las dos. San Joaquín tiene además el edificio de acceso en superficie, que le da la plantilla completa.

**Miembros** (todos con topología, todos confirmados), ordenados por profundidad del andén:

- Andén a -3: Auditorio, Polanco, San Antonio, San Joaquín, San Pedro de los Pinos, Barranca del Muerto.
- Andén a -4: Aquiles Serdán, Constituyentes, Refinería.
- Andén a -5: Camarones.

**Adiciones.** Barranca del Muerto es terminal. Camarones es la más extrema de todas: diecisiete nodos intermedios, seis niveles y dieciséis escaleras eléctricas. Si la plantilla se parametriza por número de tramos de la cascada, esta familia se cubre entera con una sola construcción y un parámetro de profundidad.

## Familia H — Elevada de L9 oriente

*(mi etiqueta: «elevada de L9 oriente»)*

**Firma.** Dos andenes laterales elevados a +2, con nodos de vestíbulo al mismo nivel +2 y un pasillo superior a +3 para el cambio de andén, más dos accesos a nivel de calle. Es el tramo de L9 que corre sobre el Viaducto Río de la Piedad.

**Estación modelo: Puebla (L9).** Ciudad Deportiva es casi idéntica (un pasillo más).

**Miembros** (todos con topología, todos confirmados): Ciudad Deportiva (L9), Puebla (L9), Velódromo (L9).

**Adiciones.** Velódromo tiene sus accesos a nivel 0 en vez de +2, tres accesos en lugar de dos, y un elevador, el único de la familia. Es la variante, no la plantilla.

## Familia I — Elevada de LA (Los Reyes)

*(mi etiqueta: «elevada de LA»)*

**Firma esperada, sin confirmar.** Ninguna estación de la Línea A tiene topología levantada ni escaleras en el modelo legado. Por trazo y por forma del KML —polígonos compactos de 2 500 a 3 500 m², elongación entre 1,4 y 3— se espera la estación de superficie de dos andenes laterales con puente vestibular superior y dos accesos, que es la tipología del tren férreo de Los Reyes. Toda la familia es **provisional**.

**Estación modelo propuesta: Guelatao (LA).** No es terminal, no es correspondencia y su polígono está en la mediana de la línea. Es la que conviene levantar primero para convertir esta familia de provisional en confirmada; ninguna otra fuente la cubre.

**Miembros provisionales:** Acatitla, Agrícola Oriental, Canal de San Juan, Guelatao, La Paz (terminal), Los Reyes, Peñón Viejo, Santa Marta, Tepalcates.

**Advertencia.** La Paz, terminal de la línea, casi con seguridad no encaja: su polígono duplica el área del resto (6 664 m² contra ~3 000).

## Familia J — Elevada de L12 oriente (Tláhuac)

*(mi etiqueta: «elevada de L12 oriente»)*

**Firma esperada, sin confirmar.** Viaducto elevado sobre Tláhuac con andenes a +2 y vestíbulo intermedio a +1. Ninguna de las once tiene topología; el modelo legado `Stair` les asigna entre tres y cuatro escaleras cada una, cifra compatible con dos accesos y dos tramos de subida. Ninguna aparece en el KML de áreas de estación, así que aquí no hay ni siquiera evidencia de forma: la familia se sostiene solo en la unidad constructiva del tramo. Confianza **baja**.

**Estación modelo propuesta: Olivos (L12).** Está a media línea, no es terminal ni correspondencia.

**Miembros provisionales:** Calle 11, Culhuacán, Lomas Estrella, Nopalera, Olivos, Periférico Oriente, San Andrés Tomatlán, Tezonco, Tlaltenco, Tláhuac (terminal), Zapotitlán.

**Advertencia.** Periférico Oriente tiene ocho escaleras en el modelo legado, el doble que sus vecinas; probablemente no pertenece a la familia.

## Familia L — Elevada de LB norte

*(mi etiqueta: «elevada de LB norte»)*

**Firma esperada, sin confirmar.** El tramo de LB desde Deportivo Oceanía hasta Ciudad Azteca corre elevado; se espera andenes laterales sobre el viaducto con vestíbulo y torniquetes debajo, y accesos a nivel de calle. Sin topología ni escaleras legadas en ninguna de las once. Los polígonos del KML son consistentes entre sí (3 100 a 5 100 m², elongación de 2,6 a 5,3), lo que respalda la homogeneidad del tramo. Confianza **media-baja**.

**Estación modelo propuesta: Múzquiz (LB).** Intermedia, sin adiciones, con polígono representativo.

**Miembros provisionales:** Bosque de Aragón, Ciudad Azteca (terminal), Deportivo Oceanía, Ecatepec, Impulsora, Múzquiz, Nezahualcóyotl, Olímpica, Plaza Aragón, Río de los Remedios, Villa de Aragón.

**Advertencia.** El polígono de Impulsora en el KML mide 332 m² con elongación 10, un orden de magnitud fuera del resto: el trazo está mal, no la estación.

## Familia M — Cajón subterráneo sin levantar (L5 norte y L6 poniente)

*(mi etiqueta: «cajón subterráneo sin levantar»)*

**Firma esperada, sin confirmar.** Se espera la familia B —dos andenes laterales a -1, dos vestíbulos de andén, pasillo inferior de cambio de andén a -2, accesos directos a la calle—, que es lo que dan las tres estaciones vecinas de L6 que sí están levantadas: Lindavista, Norte 45 y Vallejo. Confianza **media**: la extrapolación es corta y el tramo es constructivamente homogéneo.

**Estación modelo propuesta: Misterios (L5).** Si prefieres no levantar nada nuevo, usa directamente Doctores (familia B) como plantilla y verifica caso por caso.

**Miembros provisionales:** Autobuses del Norte (L5), Ferrería y Arena Ciudad de México (L6), La Villa y Basílica (L6), Misterios (L5), Politécnico (L5, terminal), Tezozómoc (L6), UAM Azcapotzalco (L6), Valle Gómez (L5).

**Nota.** Esta familia probablemente deba disolverse dentro de la B una vez que se levante una sola de sus estaciones. La mantengo separada para no mezclar lo confirmado con lo inferido.

## Familia N — Superficie y elevada de L5 oriente

*(mi etiqueta: «superficie y elevada de L5 oriente»)*

**Firma esperada, sin confirmar.** El tramo de L5 entre Pantitlán y Consulado corre en superficie y elevado sobre el Río Consulado. Los polígonos de Aragón y Eduardo Molina son largos y estrechos (unos 180 × 62 m, elongación 5), típicos de estación de viaducto; Hangares y Terminal Aérea son más anchas. Confianza **baja**, y probablemente haya que partir la familia en dos.

**Estación modelo propuesta: Eduardo Molina (L5).**

**Miembros provisionales:** Aragón (L5), Eduardo Molina (L5), Hangares (L5), Terminal Aérea (L5).

## Familia O — Terminal con andenes de maniobra

*(mi etiqueta: «terminal con andenes de maniobra»)*

**Firma.** Estaciones cabecera con tres o más andenes (o dos andenes más vías de maniobra), vestíbulo grande, muchísimos accesos y, casi siempre, conexión con transporte de superficie. No comparten arquitectura entre sí: lo que comparten es que su condición de terminal domina cualquier parecido con la familia de su línea. Están juntas para señalar que **no se pueden duplicar de una plantilla**.

**Estación modelo: no aplica**; si necesitas una referencia levantada, Constitución de 1917 (L8) es la mejor documentada de las siete —tres andenes, dieciocho accesos, seis nodos— y Universidad (L3) la sigue con diez accesos.

**Miembros:** Buenavista (LB, provisional), Constitución de 1917 (L8, confirmada), Cuatro Caminos (L2, provisional), Indios Verdes (L3, provisional), Observatorio (L1, provisional), Tasqueña (L2, provisional), Universidad (L3, confirmada).

## Familia Z — Grandes nodos de transbordo

*(mi etiqueta: «grandes nodos de transbordo»)*

**Firma.** Correspondencias donde no hay una base reconocible que aislar: los pasillos de trasbordo, los andenes cruzados en varios niveles y los vestíbulos compartidos son la estructura, no una adición sobre ella. Cada una es un caso individual y hay que mapearla desde cero.

**Miembros con topología:** Candelaria (L1+L4), Chabacano (L2+L8+L9), Consulado (L4+L5), Deportivo 18 de Marzo (L3+L6), El Rosario (L6+L7), Garibaldi y Lagunilla (L8+LB), Instituto del Petróleo (L5+L6), Jamaica (L4+L9), Martín Carrera (L4+L6), Mixcoac (L7+L12), San Lázaro (L1+LB), Santa Anita (L4+L8), Tacubaya (L1+L7+L9).

**Miembros sin topología:** Atlalilco (L8+L12), La Raza (L3+L5), Oceanía (L5+LB), Pantitlán (L1+L5+L9+LA).

**La mejor documentada es Tacubaya**: cuarenta nodos, seis andenes en dos profundidades (-6 y -3), ochenta y tres aristas, veinticuatro escaleras eléctricas. Si vas a construir una de estas, empieza por ella, porque es la que más te enseña sobre cómo modelar niveles múltiples.

**Chabacano** merece mención aparte: nueve andenes en dos niveles, elevador, doce accesos y veintidós escaleras eléctricas. Es la estación más compleja del sistema y probablemente la última que conviene abordar.

---

## Casos que no encajan

**Estaciones con levantamiento incompleto en la base.** Deportivo 18 de Marzo tiene solo ocho nodos sueltos repartidos entre L3, L5 y L6 —y un fragmento etiquetado L5 en una estación que no tiene L5—, sin andenes de L6 ni grafo conexo. Martín Carrera tiene la mitad de L4 levantada y un único nodo de correspondencia por L6. Morelos tiene topología bajo el nodo de LB pero cero hijos bajo el de L4, más un nodo huérfano con prefijo `L1-`. Ninguna de las tres debe usarse como fuente hasta completarse.

**Errores de prefijo de línea en Miro.** Los cuatro andenes huérfanos con prefijo `L1-` de la familia F (Bondojito, Canal del Norte, Fray Servando, Talismán) y el nodo `L1-` de Morelos. Son cinco registros a corregir, todos del mismo tipo.

**Estaciones reimportadas mientras se escribía este documento.** Polanco, San Pedro de los Pinos, Tacubaya y Mixcoac estaban siendo recargadas en paralelo. Al momento del corte tenían 13, 13, 40 y 25 nodos respectivamente; el conteo de Mixcoac cambió en un nodo entre dos lecturas de la misma sesión, y en una lectura temprana sus identificadores llevaban prefijo `CMX` que después desapareció. Las asignaciones de familia de las cuatro son robustas frente a ese ruido (Polanco y San Pedro de los Pinos son inequívocamente familia G), pero **los conteos exactos de accesos y escaleras de esas cuatro deben releerse antes de usarse**.

**La Viga (L8).** Clasificada en B pero sin el pasillo inferior de cambio de andén a -2 que define la familia. Puede ser una diferencia real —hay estaciones donde el cambio de andén obliga a salir y volver a entrar— o un levantamiento incompleto. Verificar.

**Zócalo (L2).** Clasificada en C, pero su polígono KML (774 m de largo, elongación 27) indica que el área dibujada es la plaza y no la estación; cualquier razonamiento de forma sobre ella es inválido.

**Impulsora (LB) y La Paz (LA).** Polígonos KML inconsistentes con sus vecinas, por las razones ya dichas.

**Doce estaciones sin polígono KML:** todo el tramo elevado de L12 oriente (Tlaltenco, Zapotitlán, Nopalera, Olivos, Tezonco, Periférico Oriente, Calle 11, Lomas Estrella, San Andrés Tomatlán, Culhuacán), más San Juan de Letrán (L8) y Boulevard Puerto Aéreo (L1). Las dos últimas sí tienen topología, así que no importa; las diez de L12 se quedan sin ninguna evidencia geométrica.

**Cuarenta y cuatro estaciones sin topología y sin escaleras en el modelo legado.** Son las que solo tienen línea, tramo y forma: toda la Línea A, casi toda LB norte, buena parte de L5 y L6, más Merced, Observatorio, Buenavista, Tlatelolco, Potrero y La Raza. Sus asignaciones son las más frágiles del documento.

**Escuadrón 201 (L8).** Puesta en B por forma y vecindad, pero está justo entre Atlalilco (correspondencia con L12) y Aculco (viaducto elevado), en la transición de subterráneo a elevado. Podría pertenecer a E.

---

## Cómo corregir este documento

Este es un borrador para que lo edites a mano, no un resultado cerrado. La forma de corregirlo es directa: **mueve el nombre de una estación de la lista de una familia a la de otra**, y si hace falta ajusta la frase de «Firma» de la familia que recibe. No hace falta que mantengas coherencia con nada más del repositorio: este documento es la referencia [[2026-08-26-agrupamiento-estaciones-familias]] y no lo consume ningún proceso.

Si una familia te parece dos familias, pártela: dale un nombre a cada mitad y reparte los miembros. Si dos te parecen una, fúndelas y quédate con la estación modelo mejor documentada de las dos. Las candidatas más obvias a fusión son M dentro de B, y las tres subfamilias de G por profundidad dentro de una sola plantilla parametrizada. La candidata más obvia a partición es B, que con veintiocho miembros probablemente esconde dos variantes según si el pasillo inferior existe o no.

Si cambias la familia de una estación, cambia también su fila en `agrupamiento-estaciones.csv`, que tiene una fila por estación con las columnas `station, lines, family, confidence, has_topology, additions`. El CSV es la versión que conviene abrir en una hoja de cálculo para reordenar y filtrar; este documento es el que explica por qué.

Sobre las **estaciones modelo**: la propuesta es siempre la estación con menos adiciones dentro de la familia, para que la plantilla salga mínima y las demás se construyan agregando. Si prefieres el criterio contrario —modelar la más completa y quitar— la estación a elegir sería, por familia: Bellas Artes en A, Pino Suárez en B, Centro Médico en C, Ermita en D, Coyuya en E, Fray Servando en F, Camarones en G y Velódromo en H.

Las familias I, J, L, M y N no tienen ninguna estación levantada. **Levantar una sola estación de cada una convierte cinco familias provisionales en confirmadas y cubre cuarenta y tres estaciones**; es, con diferencia, el mejor uso del siguiente esfuerzo de levantamiento.
