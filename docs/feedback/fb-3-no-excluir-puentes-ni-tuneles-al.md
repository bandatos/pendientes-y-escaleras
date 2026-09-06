---
type: feedback
id: fb-3
title: No excluir puentes ni túneles al buscar vías peatonales cerca de un acceso del Metro
state: pending
date: 2026-09-02
created: "2026-09-02T17:51:17-06:00"
scope: local
kind: new
author:
  role: coordinator
mode: auto
session: 660b55e6-87b8-4085-ba9b-03d35629eb08
section: "candidatas de conexión · también: data/osm/README.md y CLAUDE.md"
target: api/utils/osm/overpass.py
from-repo: pendientes-y-escaleras
---

# No excluir puentes ni túneles al buscar vías peatonales cerca de un acceso del Metro

## Qué pasó

Trasladado desde el grafo global ([[global:fb-335]]) el 2026-09-05: la observación es una regla de dominio de este proyecto, no del harness.

Tras el hallazgo del crítico (los tramos de Portales se colgaban de un puente peatonal con bridge=yes y layer=2), el coordinador ordenó excluir puentes, túneles y toda way con layer o level distinto de 0 como candidatas de conexión. Ricardo lo revirtió: «hay muchos muchos accesos del metro que no están a nivel de calle, no estoy seguro de la decisión que tomaste de excluir puentes y túneles. Revierte eso, ya veré en la próxima sesión cómo arreglo eso que pasó en Portales».

## Propuesta

Regla de dominio para el proyecto: un acceso del Metro se conecta a la vía peatonal más cercana sea cual sea su nivel; el nivel del tramo de conexión se toma de la way destino, no se fija en 0. Es del CLAUDE.md del proyecto o del README de data/osm, no del harness global.

## Outcome
