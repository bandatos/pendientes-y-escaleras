---
type: task
id: task-34
title: "Validador de pares de escaleras eléctricas en L7: definir la regla y revisar las 7 solitarias que solo suben"
state: open
date: 2026-09-02
owner: ricardo
source: ["[[2026-09-02-sesion-integracion-osm-y-niveles]]"]
related: ["[[adr-0012]]", "[[task-24]]", "[[adr-0013]]"]
---

# Validador de pares de escaleras eléctricas en L7: definir la regla y revisar las 7 solitarias que solo suben

Ricardo, 2 de septiembre: en L7 las eléctricas van en pares (una que solo sube y una bidireccional que normalmente baja), salvo algunos pares de Mixcoac, Tacuba y Tacubaya; quiere un validador que avise cuando las flechas de Miró no cumplan, corrido una sola vez para verificar. Corrida exploratoria sobre 86 pares de nodos con eléctricas en L7: 38 con bidireccional + sube; 25 con solo una que sube y 18 con solo una que baja, de las cuales 36 están en Aquiles Serdán, Camarones y Refinería balanceadas (6 y 6, 8 y 8, 4 y 4) y Ricardo confirma que están bien, la de subida y la de bajada llegan a descansos distintos, así que un validador «por el mismo par de nodos» daría falsos positivos; Tacuba tiene dos pares con cuatro que suben y uno con dos bidireccionales y dos que suben; Tacubaya dos pares con dos que suben. Las 7 solitarias que solo suben sin gemela en ningún par son las que hay que validar: 1 en Barranca del Muerto, 2 en Mixcoac, 2 en San Joaquín y 2 en San Pedro de los Pinos. Falta que Ricardo defina la regla (¿por mismos dos niveles en la misma zona, no por mismos nodos?) antes de escribir el validador.

## Decisiones tomadas

- 21 de octubre de 2026, forma de las eléctricas de un solo sentido que bajan (50 en la red, 18 en L7, según [[adr-0012]]): Ricardo decidió mantener la vigente, dibujadas en el sentido de viaje, hacia abajo, con `conveying=forward` + `incline=down`; no se pasan a `conveying=backward` + `incline=up`. Evidencia: válida según Key:conveying y Key:incline de la wiki; en Overpass, al 20 de octubre de 2026, 3 440 ways así contra 1 471 con la alternativa. Queda como nota de enmienda en [[adr-0013]].

## Criterios de aceptación

- [ ] Regla definida por Ricardo
- [ ] Las 7 solitarias tienen veredicto: correctas o corregidas en Miró
