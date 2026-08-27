---
type: decision
id: adr-0006
title: "Plantillas por familia arquitectónica: correspondencia = familia base + adiciones"
state: accepted
date: 2026-08-26
origin: ricardo
deliberation: dialogued
rationale: recorded
source: ["[[2026-08-26-sesion-mapeo-osm]]"]
affects: ["docs/reference/2026-08-26-agrupamiento-estaciones-familias.md"]
---

# Plantillas por familia arquitectónica: correspondencia = familia base + adiciones

## Contexto

Muchas estaciones de una misma línea comparten arquitectura. Se calculó la firma topológica del grafo de cada estación (andenes, accesos, niveles, escaleras por tramo, simetría) para las 98 con datos de Miró. El subgrafo de L2 de Ermita resultó idéntico al de Portales, General Anaya, Nativitas, Viaducto, Villa de Cortés y Xola; la correspondencia a L12 es una adición.

## Resultado

Una plantilla por familia (JSON en coordenadas locales métricas relativas al centroide y eje del andén, con espejo opcional), instanciada por rotación al rumbo de la estación destino y traslación al centroide. Las correspondencias se asignan a la familia de su base y se les agregan las adiciones; solo las sin base reconocible quedan como «gran nodo de transbordo». Los pathways paralelos con mismo origen, destino y modo son elementos reales (cada uno con `miro_id` distinto: cuatro tramos de escalera en Portales) y no se deduplican. El agrupamiento vive en [[2026-08-26-agrupamiento-estaciones-familias]] y lo corrige Ricardo ([[task-8]]).

### Consecuencias

- **Bueno:** el espejo ya está probado en datos (San Pedro de los Pinos es exactamente simétrico).
- **Malo:** la geometría duplicada no fue observada en sitio; hay que decirlo en la consulta a la comunidad ([[task-11]]).

## Más información

[[2026-08-26-sesion-mapeo-osm]].
