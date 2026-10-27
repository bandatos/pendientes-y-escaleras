"""Validaciones del documento antes de escribirlo."""
from __future__ import annotations

import math
from collections import Counter, defaultdict, deque

from . import tags as T
from .document import OsmDocument, OsmRelation
from .geometry import (point_in_polygon, point_in_polygon_tol,
                       ring_self_intersections, segment_intersection)

MIN_NODE_DISTANCE_M = 0.3
# Margen con el que se juzga si un objeto cae dentro del área: el anillo
# viene de un trazo sobre imagen satelital, no de una medición.
INSIDE_AREA_TOLERANCE_M = 0.3

# Superficies: no son aristas de la red peatonal, así que ni llevan
# `level` ni tienen que compartir nodo con nadie para no ser islas.
SURFACE_KINDS = ("platform", "plaza", "building", "station_area")
# El andén sí lleva `level`; el resto de las superficies no son aristas
# de circulación y no tienen a qué nivel pertenecer.
LEVELLESS_KINDS = ("plaza", "building", "station_area")
# Lo que vive a la intemperie: el edificio de acceso, su explanada y los
# tramos a la banqueta están fuera del área de la estación por
# definición, así que no entran en la regla de estar dentro.
OUTDOOR_KINDS = ("plaza", "building", "building_way", "connector",
                 "station_area")


def validate(doc: OsmDocument) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []

    # Los objetos ajenos entran con su id real y sus etiquetas tal como
    # están en OSM: las reglas de abajo son sobre lo que dibujamos.
    ids = [n.id for n in doc.nodes.values() if not n.foreign]
    ids += [w.id for w in doc.ways if not w.foreign]
    ids += [r.id for r in doc.relations.values() if not r.foreign]
    if len(ids) != len(set(ids)):
        errors.append("hay ids repetidos entre nodos, ways y relaciones")
    if any(i >= 0 for i in ids):
        errors.append("hay ids no negativos")

    # Los anillos de un multipolígono van sin etiquetas: las lleva la
    # relación.
    members = _own_relation_members(doc)
    for way in doc.ways:
        for nid in way.nodes:
            if nid not in doc.nodes:
                errors.append(f"way {way.id} referencia el nodo {nid}")
        if way.foreign:
            continue
        if len(way.nodes) < 2:
            errors.append(f"way {way.id} tiene menos de dos nodos")
        if not way.tags and way.id not in members:
            errors.append(f"way {way.id} no tiene etiquetas")
        if "level" not in way.tags and way.kind not in LEVELLESS_KINDS:
            errors.append(f"way {way.id} no tiene level")

    # El contexto entra en la comparación: el error que hay que cazar es
    # emitir un nodo nuestro encima de uno que ya existe en OSM. Dos
    # nodos ajenos juntos son cosa de OSM y no nuestra.
    # Un nodo que sale con `action='delete'` ya no estará ahí después de
    # subir: chocar con él no es un error del archivo.
    nodes = [n for n in doc.nodes.values() if n.action != "delete"]
    loose = _area_vertex_pairs_exempt(doc)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if nodes[i].frozen and nodes[j].frozen:
                continue
            if loose(nodes[i], nodes[j]):
                continue
            d = math.hypot(nodes[i].u - nodes[j].u, nodes[i].v - nodes[j].v)
            if d < MIN_NODE_DISTANCE_M:
                errors.append(
                    f"nodos {nodes[i].id} y {nodes[j].id} a {d:.2f} m")

    for node in doc.nodes.values():
        if node.foreign:
            continue
        if node.tags.get("railway") == "subway_entrance" or (
                node.tags.get("barrier") == "turnstile"):
            if "level" not in node.tags:
                errors.append(f"nodo {node.id} sin level")

    errors += _check_incline(doc)
    errors += _check_incline_order(doc)
    warnings += _check_cross_level_nodes(doc)
    warnings += _check_bank_tips(doc)
    errors += _check_area_rings(doc)
    errors += _check_inside_area(doc)
    errors += _check_connectivity(doc)

    return errors, warnings, _summary(doc)


def _area_vertex_pairs_exempt(doc: OsmDocument):
    """¿Es el par un vértice del área con un nodo de OSM que no es de
    edificio?

    El área solo comparte nodos con edificios (el resto de OSM sigue otra
    lógica: banquetas, jardines), así que un vértice suyo a centímetros
    de una banqueta no es un gemelo mal emitido sino dos objetos que no
    se tocan. En San Antonio un vértice del KML cae a 0.23 m de un nodo
    de banqueta.
    """
    area, used_elsewhere, building = set(), set(), set()
    for way in doc.ways:
        if way.kind == "station_area":
            area.update(way.nodes)
        else:
            used_elsewhere.update(way.nodes)
        if "building" in way.tags:
            building.update(way.nodes)
    pure_area = area - used_elsewhere

    def exempt(a, b) -> bool:
        for mine, other in ((a, b), (b, a)):
            if (mine.id in pure_area and other.foreign
                    and other.id not in building):
                return True
        return False
    return exempt


def _own_relation_members(doc: OsmDocument) -> set[int]:
    out = set()
    for rel in doc.relations.values():
        if rel.foreign:
            continue
        for kind, ref, _ in rel.members:
            if kind != "way":
                continue
            out.add(ref)
    return out


def _station_area(doc: OsmDocument):
    """(relación o way, [(rol, way, anillo)]) del área de estación.

    El área es un multipolígono solo cuando tiene islas; sin ellas es un
    way cerrado con las etiquetas, que aquí cuenta como su único outer.
    None si el archivo va sin área.
    """
    rel = next((r for r in doc.relations.values()
                if r.kind == "station_area"), None)
    if rel is None:
        way = next((w for w in doc.ways if w.kind == "station_area"), None)
        if way is None:
            return None
        return way, [("outer", way, _way_ring(doc, way))]
    ways = {w.id: w for w in doc.ways}
    rings = []
    for kind, ref, role in rel.members:
        way = ways.get(ref) if kind == "way" else None
        if way is None:
            continue
        rings.append((role, way, _way_ring(doc, way)))
    return rel, rings


def _way_ring(doc: OsmDocument, way):
    ring = [(doc.nodes[n].u, doc.nodes[n].v) for n in way.nodes
            if n in doc.nodes]
    if len(ring) > 2 and ring[0] == ring[-1]:
        ring = ring[:-1]
    return ring


def _station_area_rings(doc: OsmDocument):
    """[exterior, *islas] del área, para medir dentro y fuera."""
    found = _station_area(doc)
    if found is None:
        return None
    _, rings = found
    outer = [r for role, _, r in rings if role == "outer" and len(r) >= 3]
    inner = [r for role, _, r in rings if role == "inner" and len(r) >= 3]
    if len(outer) != 1:
        return None
    return [outer[0], *inner]


def _check_area_rings(doc: OsmDocument) -> list[str]:
    """El área tiene que ser una que JOSM acepte.

    Un outer, anillos cerrados que no se cruzan a sí mismos ni entre
    ellos, y cada isla dentro del outer: es lo que antes se escondía en
    los cortes de ancho cero del anillo único. Un área sin islas es un
    solo way y le aplica lo mismo que a un outer.
    """
    found = _station_area(doc)
    if found is None:
        return []
    rel, rings = found
    out = []
    members = rel.members if isinstance(rel, OsmRelation) else []
    refs = {ref for kind, ref, _ in members if kind == "way"}
    missing = refs - {w.id for w in doc.ways}
    if missing:
        out.append(f"el multipolígono del área {rel.id} referencia ways "
                   f"que no están: {sorted(missing)}")
    outers = [r for role, _, r in rings if role == "outer"]
    if len(outers) != 1:
        out.append(f"el multipolígono del área {rel.id} tiene "
                   f"{len(outers)} anillos outer; debe tener uno")
    for role, way, ring in rings:
        if role not in ("outer", "inner"):
            out.append(f"way {way.id} del área con rol «{role}»")
        if way.nodes[0] != way.nodes[-1] or len(ring) < 3:
            out.append(f"el anillo {role} {way.id} del área no es un way "
                       f"cerrado de al menos tres vértices")
            continue
        crossings = ring_self_intersections(ring)
        if crossings:
            out.append(f"el anillo {role} {way.id} del área se cruza a sí "
                       f"mismo en {len(crossings)} pares de lados")
    if len(outers) == 1:
        for role, way, ring in rings:
            if role != "inner" or len(ring) < 3:
                continue
            if not all(point_in_polygon(outers[0], p) for p in ring):
                out.append(f"la isla {way.id} del área no cae entera "
                           f"dentro del outer")
            elif _rings_cross(outers[0], ring):
                out.append(f"la isla {way.id} del área cruza el outer")
    inners = [(way, r) for role, way, r in rings if role == "inner"]
    for i, (wa, a) in enumerate(inners):
        for wb, b in inners[i + 1:]:
            if _rings_cross(a, b):
                out.append(f"las islas {wa.id} y {wb.id} del área se "
                           f"cruzan")
    return out


def _rings_cross(a, b) -> bool:
    for i in range(len(a)):
        for j in range(len(b)):
            if segment_intersection(a[i], a[(i + 1) % len(a)], b[j],
                                    b[(j + 1) % len(b)]) is not None:
                return True
    return False


def _check_inside_area(doc: OsmDocument) -> list[str]:
    """Todo el interior de la estación tiene que caber en su área.

    El área del KML delimita dónde está la estación, así que un andén,
    un pasillo, una escalera o un torniquete que se sale de ella es un
    error de trazo. Ricardo: «todos los trazos deberían caber dentro del
    área de la estación». El área es el outer menos sus islas: lo que
    cae en una isla está fuera. Es error, no aviso; el archivo se escribe antes
    de validar, así que se puede abrir y ver qué se salió.
    """
    ring = _station_area_rings(doc)
    if ring is None:
        return []
    candidates: dict[int, str] = {}
    for way in doc.ways:
        if way.foreign or way.kind in OUTDOOR_KINDS:
            continue
        if (way.kind in ("platform", "spine")
                or way.tags.get("indoor") == "yes"
                or way.tags.get("highway") == "steps"):
            for nid in way.nodes:
                candidates.setdefault(nid, way.label or str(way.id))
    for node in doc.nodes.values():
        if node.tags.get("barrier") == "turnstile":
            candidates.setdefault(node.id, "torniquete")
    exempt = set(doc.outdoor)
    for way in doc.ways:
        if way.kind in OUTDOOR_KINDS:
            exempt |= set(way.nodes)
    out = []
    offenders = []
    for nid, label in sorted(candidates.items()):
        node = doc.nodes.get(nid)
        if node is None or node.foreign or nid in exempt:
            continue
        if node.tags.get("railway") == "subway_entrance" or (
                node.tags.get("disused:railway") == "subway_entrance"):
            continue
        inside, distance = point_in_polygon_tol(
            ring, (node.u, node.v), INSIDE_AREA_TOLERANCE_M)
        if not inside:
            offenders.append((distance, nid, label))
    if offenders:
        offenders.sort(reverse=True)
        detail = "; ".join(f"{nid} en {label} ({d:.1f} m)"
                           for d, nid, label in offenders)
        out.append(
            f"{len(offenders)} nodos del interior de la estación caen "
            f"fuera del área: {detail}")
    return out


def _check_incline(doc: OsmDocument) -> list[str]:
    out = []
    for way in doc.ways:
        # Una escalera de OSM que entra como escenografía trae las
        # etiquetas de quien la mapeó (en General Anaya, sin level).
        if way.foreign:
            continue
        levels = way.tags.get("level", "")
        parts = [int(p) for p in levels.split(";") if p.strip()]
        incline = way.tags.get("incline")
        if way.tags.get("highway") == "steps":
            if len(parts) != 2:
                out.append(f"way {way.id}: steps con level='{levels}'")
            if incline not in ("up", "down"):
                out.append(f"way {way.id}: steps sin incline válido")
            conveying = way.tags.get("conveying")
            if conveying not in (None, "forward", "backward", "reversible"):
                out.append(f"way {way.id}: conveying '{conveying}'")
            if conveying == "reversible" and incline != "up":
                out.append(
                    f"way {way.id}: escalera reversible no dibujada de "
                    f"abajo hacia arriba")
        elif len(parts) == 2 and incline is None:
            out.append(f"way {way.id}: cambia de nivel y no trae incline")
    return out


def _node_levels(doc: OsmDocument) -> dict:
    """Nivel de cada nodo: el que comparten todos los ways que lo tocan.

    Un nodo donde se juntan una escalera -3;-2 y otra -2;-1 solo puede
    estar en el -2. Cuando la intersección no da un único nivel el nodo
    queda fuera: no hay de dónde deducirlo.
    """
    owners = defaultdict(list)
    for way in doc.ways:
        if way.foreign or not way.levels:
            continue
        for nid in way.nodes:
            owners[nid].append(way)
    out = {}
    for nid, ways in owners.items():
        common = set(ways[0].levels)
        for w in ways[1:]:
            common &= set(w.levels)
        if len(common) == 1:
            out[nid] = common.pop()
    return out


def _check_incline_order(doc: OsmDocument) -> list[str]:
    """El `incline` tiene que concordar con dónde caen los extremos.

    `incline` sale del orden de los niveles y el orden de los nodos sale
    de la geometría de la plantilla; si esa geometría se escribió al
    revés, las dos cosas dejan de coincidir y el archivo dice que se
    sube por donde se baja. Solo se compara cuando los dos extremos
    tienen un nivel deducible y distinto entre sí.
    """
    levels = _node_levels(doc)
    out = []
    for way in doc.ways:
        if way.tags.get("highway") != "steps":
            continue
        incline = way.tags.get("incline")
        if incline not in ("up", "down"):
            continue
        start = levels.get(way.nodes[0])
        end = levels.get(way.nodes[-1])
        if start is None or end is None or start == end:
            continue
        drawn = "up" if end > start else "down"
        if drawn != incline:
            out.append(
                f"way {way.id} ({way.label}): incline={incline} pero se "
                f"dibuja del nivel {start:g} al {end:g}; la geometría de "
                f"la plantilla parece escrita al revés")
    return out


def _check_cross_level_nodes(doc: OsmDocument) -> list[str]:
    """Nodo compartido por ways sin ningún nivel en común: sospechoso."""
    owners = defaultdict(list)
    for way in doc.ways:
        if way.foreign or not way.levels:
            continue
        for nid in way.nodes:
            owners[nid].append(way)
    out = []
    for nid, ways in owners.items():
        if len(ways) < 2:
            continue
        common = set(ways[0].levels)
        for w in ways[1:]:
            common &= set(w.levels)
        if not common:
            out.append(
                f"nodo {nid} une ways sin nivel común: "
                + ", ".join(f"{w.id}({w.label})" for w in ways))
    return out


def _check_bank_tips(doc: OsmDocument) -> list[str]:
    """Footway que pasa por la punta de una escalera de banco.

    La punta solo debe tocar su tramo corto hacia el nodo de encuentro;
    si un pasillo la lleva como vértice intermedio, se engancha a la
    escalera y duplica ese tramo.
    """
    out = []
    for way in doc.ways:
        if way.foreign or way.tags.get("highway") != "footway":
            continue
        for nid in way.nodes[1:-1]:
            if nid in doc.bank_tips:
                out.append(
                    f"el footway {way.id} ({way.label}) pasa por la punta "
                    f"{nid} de una escalera de banco")
    return out


def _check_connectivity(doc: OsmDocument) -> list[str]:
    adj = defaultdict(set)
    for way in doc.ways:
        for a, b in zip(way.nodes, way.nodes[1:]):
            adj[a].add(b)
            adj[b].add(a)
    entrances = [n.id for n in doc.nodes.values()
                 if n.tags.get("railway") == "subway_entrance"]
    # El andén se alcanza por su línea de circulación: el polígono del
    # andén es superficie, no arista del grafo peatonal.
    spines = [w for w in doc.ways if w.kind == "spine"]
    out = []
    if not entrances:
        out.append("no hay nodos de acceso")
    if not spines:
        out.append("ningún andén tiene línea de circulación")
    for start in entrances:
        seen = {start}
        q = deque([start])
        while q:
            cur = q.popleft()
            for nxt in adj[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        for way in spines:
            if not seen & set(way.nodes):
                out.append(
                    f"desde el acceso {start} no se llega al andén "
                    f"{way.label}")
    islands = [w.id for w in doc.ways
               if w.kind not in SURFACE_KINDS and not w.foreign
               and not (set(w.nodes) & _all_other_nodes(doc, w))]
    if islands:
        out.append(f"ways sin nodo compartido con ningún otro: {islands}")
    return out


def _all_other_nodes(doc: OsmDocument, way) -> set:
    out = set()
    for other in doc.ways:
        if other is not way:
            out |= set(other.nodes)
    return out


def _summary(doc: OsmDocument) -> dict:
    counts = Counter()
    # Los anillos solo se cuentan aparte cuando son de un multipolígono:
    # un área sin islas es un way etiquetado y se cuenta por su etiqueta.
    area = _station_area(doc)
    roles = ({way.id: role for role, way, _ in area[1]}
             if area and isinstance(area[0], OsmRelation) else {})
    for rel in doc.relations.values():
        if rel.kind == "station_area":
            counts["public_transport=station (área, multipolígono)"] += 1
    for way in doc.ways:
        if way.id in roles:
            counts[f"área de estación: anillo {roles[way.id]}"] += 1
        elif way.tags.get("railway") == "platform":
            counts["railway=platform"] += 1
        elif way.tags.get("highway") == "steps":
            conv = way.tags.get("conveying")
            counts["highway=steps" + (f" conveying={conv}" if conv else "")
                   ] += 1
        elif way.tags.get("highway") == "footway":
            counts["highway=footway"] += 1
        elif way.tags.get("highway") == "pedestrian":
            counts["highway=pedestrian (explanada)"] += 1
        elif way.tags.get("public_transport") == "station":
            counts["public_transport=station (área)"] += 1
        elif way.tags.get("building"):
            counts["building"] += 1
        else:
            counts["way sin clasificar"] += 1
    for node in doc.nodes.values():
        if node.tags.get("railway") == "subway_entrance":
            counts["railway=subway_entrance"] += 1
        elif node.tags.get("barrier") == "turnstile":
            counts["barrier=turnstile"] += 1
    counts["nodos (total)"] = len(doc.nodes)
    counts["ways (total)"] = len(doc.ways)
    counts["nodos nuevos"] = sum(1 for n in doc.nodes.values()
                                 if not n.foreign)
    counts["nodos de OSM (contexto)"] = sum(
        1 for n in doc.nodes.values() if n.foreign and n.frozen)
    counts["nodos de OSM modificados"] = sum(
        1 for n in doc.nodes.values() if n.foreign and not n.frozen)
    counts["nodos de OSM dados de baja"] = sum(
        1 for n in doc.nodes.values() if n.action == "delete")
    counts["ways nuevos"] = sum(1 for w in doc.ways if not w.foreign)
    counts["ways de OSM (contexto)"] = sum(
        1 for w in doc.ways if w.foreign and w.frozen)
    counts["ways de OSM modificados"] = sum(
        1 for w in doc.ways if w.foreign and not w.frozen)
    counts["relaciones nuevas"] = sum(
        1 for r in doc.relations.values() if not r.foreign)
    counts["objetos con etiqueta de traza"] = sum(
        1 for o in list(doc.ways) + list(doc.nodes.values())
        if any(k in o.tags for k in T.TRACE_KEYS))
    return dict(counts)
