---
type: task
id: task-31
title: "Escaleras con ambos extremos en el mismo nivel: revisar los 64 casos restantes con Pablo"
state: open
date: 2026-09-02
owner: ricardo
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
related: ["[[task-13]]", "[[task-24]]", "[[adr-0012]]"]
---

# Escaleras con ambos extremos en el mismo nivel: revisar los 64 casos restantes con Pablo

Tras corregir el parser de niveles de Miró («Nivel Andenes superficie 0» no se leía) y reimportar sin `--reset` El Rosario, Universidad, Constitución de 1917, Ermita, Morelos y Jamaica, la lista de escaleras fijas y eléctricas cuyos dos extremos caen en el mismo `level_index` bajó de 132 a 64 filas. La lista vive en `data/analysis/escaleras-mismo-nivel.csv` (columnas modo, estación, pathway_id, stops de origen y destino con nombre, nivel, bidireccional); se regenera consultando `Pathway` con modo 2 o 4 y `from_stop.level.level_index == to_stop.level.level_index`.

Grupos restantes, por qué siguen planos y qué se decidió ya:

- **Chabacano (14) y Mixcoac (4)**: mezzanines intermedios que el tablero nombra sin darles banda de nivel. Decidido por Ricardo el 2 de septiembre: no reciben nivel propio. Para OSM una escalera dentro de un mismo nivel es válida (`highway=steps` con el mismo `level` en ambos extremos); las cuatro eléctricas al mismo nivel están aquí (Mixcoac 1, Chabacano 3), todas vestíbulo ↔ mezzanine.
- **Pasillos de correspondencia**: Guerrero (6), Balderas (3), Centro Médico (1), Bellas Artes (1), Jamaica (1 de L9): el pasillo va a la misma profundidad nominal que el andén.
- **Edificio de acceso ↔ acceso**: Allende (4), Isabel la Católica (4), Garibaldi y Lagunilla (2), Tacubaya (2): edificio y puerta en la misma banda; la escalera es el tramo desde la banqueta.
- **Tramos cortos andén ↔ vestíbulo**: Santa Anita (6), La Viga (4), Fray Servando (4), Jamaica (2 de L9), Insurgentes Sur (1), Consulado (3): genuinamente dentro de un nivel.
- **Consulado (+2)**: «L4 Pasillo superior dir. Santa Anita NTE» ↔ andén «L4 <= Santa Anita», ambos dentro de la banda de andenes; su flecha de nivel ya estaba bien puesta. Ricardo lo resuelve después: ¿ese pasillo va en +3 o de verdad está al nivel del andén?
- **Candelaria (1)**: el conector de Miró va de «L4 Vestíbulo principal» a sí mismo; la estación no tiene ningún stop con «objetos perdidos» en la base, así que el otro extremo del conector es una figura que no se importa como stop. Se corrige en Miró.

Ricardo revisa los grupos con Pablo. Los mezzanines de Mixcoac y Chabacano no se vuelven a proponer.

## Criterios de aceptación

- [ ] Cada grupo tiene veredicto: correcto como está, corregido en Miró, o convertido en task
- [ ] Consulado +2 resuelto
- [ ] Candelaria corregido en Miró y reimportado
