---
type: task
id: task-76
title: Decidir con Pablo la vía de L7 (layer, level) y el seccionamiento de las líneas en relaciones
state: open
date: 2026-10-30
owner: ricardo
source: ["[[2026-10-30-sesion-layer-nodos-de-anden-y-snapshots-post-publicacion]]"]
related: ["[[task-28]]", "[[task-10]]", "[[adr-0019]]"]
---

# Decidir con Pablo la vía de L7 (layer, level) y el seccionamiento de las líneas en relaciones

No es una discusión simple y Ricardo quiere resolverla con Pablo con calma. Lo que ya está acordado el 30 de octubre de 2026: es consenso quitar `level` a la vía; Pablo cree que eventualmente los mapeadores tendrán que seccionar la línea en tramos y juntarlos en una relación («como debe ser»); Ricardo piensa que el resto de L7 debería quedar en `layer=-2` (hay pasos a desnivel a lo largo de la ruta que no cabrían bien en −1), con Rosario a nivel de superficie; y nosotros **nunca tocamos el `layer` de las vías** (ya en [[adr-0019]] y en el skill).

Datos para la plática. El way 320892187 es toda la L7 en una sola línea de 17 km; su `layer` fue −5 (2015, creación), −1 (2019), −3 (2023), −4 (2024), y el `level=-4` lo añadió un mapeador en febrero de 2025 copiando el layer; es la única vía del Metro con `level` negativo (8 de unos 1100 ways de vía llevan `level`, casi todos `level=1` en viaductos). Los tramos en túnel de las demás líneas usan −1 o −2, con −3 y −4 sueltos en L3, L8 y L B; el wiki de `tunnel` sugiere `layer=-2` para metros, dejando el −1 a los pasos peatonales. L2 en Tlalpan (San Antonio Abad a Tasqueña) es superficial, ni túnel ni puente, salvo dos puntos donde baja para pasar bajo avenidas transversales (serían tramos propios con `tunnel` y `layer=-1`); sus ways llevan `layer=1` sin `bridge`, que ya está en [[task-28]].

Los cuatro bloques de argumentos que el coordinador preparó:

1. **`layer` igual a `level` en nuestros ways subterráneos** (ya acordado). `level` es número de piso dentro de la estación y lo fija cada estación (−3 la mayoría; −6 Tacubaya; −5 Camarones; −4 Constituyentes, Refinería y Aquiles Serdán; 0 Rosario); `layer` solo ordena lo que se cruza en planta. Igualarlos es una convención nuestra, no una ley: el único requisito del `layer` es ser distinto del de lo que cruzamos a otra altura y en el orden correcto. Entre nuestros propios ways el `layer` no importa en iD (interiores con `level` distinto quedan exentos); nos separa de lo que no es interior: calles, edificios, la vía, túneles ajenos.
2. **La vía de L7.** Una vía de 17 km no puede tener un `level`: pasa por once estaciones con pisos distintos y fuera de ellas no hay piso que contar; por eso nuestros andenes en −3 no tienen que negociar con su −4. Opciones: proponer a la comunidad quitarle `level` y poner `layer=-2`, avisando a mdelatorre (la tocó dos veces) o en el foro ([[task-10]]); o dejarla. Si pasa a −2, el choque con nuestro pasillo bajo las vías desaparece, pero nada impide que alguien la vuelva a cambiar.
3. **Parche local o regla general para el pasillo bajo las vías.** Opciones: `layer` una unidad por debajo de la vía desde la plantilla de L7 (dice la verdad física; se rompe si la vía cambia), aceptar el aviso (lo elegido hoy; riesgo de que alguien lo «arregle» desde iD partiendo el pasillo), o no ponerle `layer` a ese way. Cualquiera es frágil porque depende de un dato ajeno; lo que protege es que el generador prediga los avisos de iD con el contexto real ([[task-78]]).
4. **Nodo compartido pasillo–andén.** Resuelto hoy como regla del generador ([[adr-0020]]).

Pregunta transversal: ¿defender en la comunidad que las vías no llevan `level`, o aceptar `level` por tramos coincidiendo con cada estación? El coordinador defendería lo primero; lo segundo obliga a partir la vía en cada estación y mantenerlo.

## Criterios de aceptación

- [ ] Ricardo trae la decisión con Pablo: qué se propone a la comunidad sobre la vía de L7 (level, layer, seccionamiento) y quién lo lleva
- [ ] Si cambia algo de nuestro esquema de `layer`, se abre su ADR y la task de implementación
