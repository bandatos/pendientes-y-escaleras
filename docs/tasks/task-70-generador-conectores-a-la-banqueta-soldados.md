---
type: task
id: task-70
title: "Generador: conectores a la banqueta soldados a mitad de banqueta y poda de candidatos que cruzan calzada o túnel"
state: open
date: 2026-10-30
owner: ai
source: ["[[2026-10-30-sesion-l2-superficie-seis-estaciones-y-plantilla]]"]
related: ["[[task-59]]", "[[task-35]]"]
---

# Generador: conectores a la banqueta soldados a mitad de banqueta y poda de candidatos que cruzan calzada o túnel

La regla vigente: un acceso lleva conector solo cuando hay un enlace corto y evidente a una banqueta mapeada ([[adr-0016]]); el automático de 45 m es provisional. En las seis estaciones del 27 de octubre de 2026 el automático tiró abanicos absurdos: Ermita 11 conectores a 31–44 m (a nodos del túnel, a una parada sobre la vía, a las puntas del puente); Viaducto tres que cruzaban la lateral o entraban al túnel 868793751; Nativitas uno que cruzaba el lóbulo. Los trazadores los podaron a mano.

- Los conectores solo van a vértices existentes; una banqueta larga de dos nodos da conectores de 40 m. Debería poder insertar un vértice en el pie de la perpendicular, y el esquema de `connector` aceptar «way + punto», no solo `osm_node`.
- La poda de candidatos que cruzan una calzada o entran a un túnel (`tunnel=yes` o `layer` distinto) es automatizable.
- Ricardo duda de la lógica en general: «siento que no se está usando una buena lógica, por ejemplo en el lado poniente» (de Xola). Revisarla con él a la luz de su `xola-02-rick.osm` ([[task-59]]) antes de implementar.
- Hallazgo del 27 de octubre: en Portales, con la puerta E-02 en la esquina, el automático saca tres conectores (22,6, 38,4 y 41,9 m); la 05 tiene uno hecho a mano.

## Criterios de aceptación

- [ ] Lógica de conexión revisada con Ricardo
- [ ] El generador no propone conectores que crucen calzada o entren a un túnel
- [ ] Un conector puede soldarse a mitad de una banqueta con un vértice nuevo
- [ ] Prueba en api/utils/osm
