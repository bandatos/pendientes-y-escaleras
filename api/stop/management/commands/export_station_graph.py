"""Management command: exporta el grafo de una estación a YAML.

Recolecta los stops (Station + hijos) y los pathways internos, y los
serializa a YAML con secciones legibles para que una IA construya un
esquema gráfico. Si se indica origen y destino, calcula además la ruta
canónica (BFS por número de saltos) y agrupa por tramo todos los
pathways paralelos disponibles, marcando los que solo se pueden recorrer
en sentido opuesto al de la ruta.
"""
from __future__ import annotations

from collections import defaultdict, deque
from html import unescape
from pathlib import Path
from typing import Any

import yaml
from django.core.management.base import BaseCommand, CommandError

from stop.models import Station, Stop
from stair.models import Pathway


# Slugs estables por id de PathwayMode (id en BD == GTFS pathway_mode).
PATHWAY_MODE_SLUG = {
    1: "pasillo",
    2: "escaleras_normales",
    3: "pasillo_movil",
    4: "escalera_electrica",
    5: "elevador",
    6: "torniquete_entrada",
    7: "torniquete_salida",
}

LOCATION_TYPE_SLUG = {
    "Stop/Platform": "platform",
    "Station": "station",
    "Entrance/Exit": "entrance_exit",
    "Generic Node": "generic_node",
    "Boarding Area": "boarding_area",
}


def short_stop_id(stop_id: str, station_token: str) -> str:
    """Quita el token de la estación del id GTFS para acortarlo.

    'L7-MIXCOAC-P-01' + 'MIXCOAC' -> 'L7-P-01'.
    """
    return stop_id.replace(f"-{station_token}-", "-")


# -------------------- Construcción del grafo --------------------

def _collect_stops(station: Station) -> tuple[list[int], list[dict]]:
    """Devuelve (ids, registros .values()) de la station y sus hijos."""
    parents = list(
        Stop.objects.filter(station=station).values_list("id", flat=True))
    children = list(
        Stop.objects.filter(parent_station_id__in=parents)
        .values_list("id", flat=True))
    all_ids = parents + children
    rows = list(
        Stop.objects.filter(id__in=all_ids)
        .values(
            "id", "stop_id", "stop_name", "location_type__name",
            "route__route_short_name", "level__level_id",
            "level__level_name", "level__level_index")
        .order_by(
            "level__level_index", "route__route_short_name", "stop_id"))
    return all_ids, rows


def _build_nodes_levels(
    rows: list[dict], token: str
) -> tuple[list[dict], list[dict], dict[int, str]]:
    levels_seen: dict[str, dict] = {}
    nodes: list[dict] = []
    id_to_short: dict[int, str] = {}
    for r in rows:
        sid = r["stop_id"]
        short = short_stop_id(sid, token) if sid else f"_db{r['id']}"
        id_to_short[r["id"]] = short
        lvl_id = r["level__level_id"]
        if lvl_id and lvl_id not in levels_seen:
            levels_seen[lvl_id] = {
                "id": lvl_id,
                "level_index": r["level__level_index"],
                "level_name": r["level__level_name"],
            }
        nodes.append({
            "id": short,
            "stop_id": sid,
            "name": unescape(r["stop_name"] or ""),
            "type": LOCATION_TYPE_SLUG.get(
                r["location_type__name"],
                r["location_type__name"] or "unknown"),
            "line": r["route__route_short_name"],
            "level": lvl_id,
        })
    levels = sorted(
        levels_seen.values(),
        key=lambda x: (x["level_index"] is None, x["level_index"]))
    return nodes, levels, id_to_short


def _build_edges(
    all_ids: list[int], id_to_short: dict[int, str]
) -> tuple[list[dict], int]:
    """Lista de aristas; omite duplicados exactos.

    Un duplicado se define por igual (from, to, mode, bidirectional,
    descripción). La omisión es indicación explícita del usuario.
    """
    rows = (
        Pathway.objects
        .filter(from_stop_id__in=all_ids, to_stop_id__in=all_ids)
        .values(
            "pathway_id", "from_stop_id", "to_stop_id",
            "pathway_mode__id", "is_bidirectional",
            "pathway_description", "miro_id")
        .order_by("pathway_id"))
    edges: list[dict] = []
    seen: set[tuple] = set()
    duplicates = 0
    for p in rows:
        sig = (
            p["from_stop_id"], p["to_stop_id"], p["pathway_mode__id"],
            p["is_bidirectional"], p["pathway_description"])
        if sig in seen:
            duplicates += 1
            continue
        seen.add(sig)
        edges.append({
            "pathway_id": p["pathway_id"],
            "from": id_to_short[p["from_stop_id"]],
            "to": id_to_short[p["to_stop_id"]],
            "mode_id": p["pathway_mode__id"],
            "mode": PATHWAY_MODE_SLUG.get(
                p["pathway_mode__id"], "desconocido"),
            "bidirectional": bool(p["is_bidirectional"]),
            "description": p["pathway_description"],
            "miro_id": p["miro_id"],
        })
    return edges, duplicates


# -------------------- BFS y armado de tramos --------------------

def _bfs_path(
    edges: list[dict], src: str, dst: str
) -> list[str]:
    adj: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        adj[e["from"]].append(e["to"])
        if e["bidirectional"]:
            adj[e["to"]].append(e["from"])
    prev: dict[str, str | None] = {src: None}
    q: deque[str] = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        raise CommandError(f"No hay ruta de {src!r} a {dst!r}")
    path: list[str] = []
    cur: str | None = dst
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def _segments_with_parallels(
    edges: list[dict], path: list[str], nodes_by_id: dict[str, dict]
) -> list[dict]:
    """Para cada par consecutivo, lista todos los pathways disponibles.

    Marca dirección relativa al recorrido:
    - ``with_path``: la arista permite ir a→b (bidireccional con
      cualquier almacenamiento, o unidireccional almacenada a→b).
    - ``against_path``: unidireccional almacenada b→a (paralela en
      sentido opuesto al recorrido — el usuario pidió mostrarlas).
    """
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for e in edges:
        by_pair[(e["from"], e["to"])].append(e)
    segments: list[dict] = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        seg_pw: list[dict] = []
        for e in by_pair.get((a, b), []):
            seg_pw.append({
                "pathway_id": e["pathway_id"],
                "mode": e["mode"],
                "bidirectional": e["bidirectional"],
                "direction": "with_path",
                "stored_as": "a_to_b",
                "description": e["description"],
            })
        for e in by_pair.get((b, a), []):
            entry = {
                "pathway_id": e["pathway_id"],
                "mode": e["mode"],
                "bidirectional": e["bidirectional"],
                "description": e["description"],
                "stored_as": "b_to_a",
            }
            if e["bidirectional"]:
                # arista bidireccional almacenada al revés:
                # también sirve para a→b
                entry["direction"] = "with_path"
            else:
                entry["direction"] = "against_path"
                entry["note"] = (
                    "paralela en sentido opuesto al recorrido")
            seg_pw.append(entry)
        a_node = nodes_by_id[a]
        b_node = nodes_by_id[b]
        segments.append({
            "hop": i + 1,
            "from": a,
            "to": b,
            "from_level": a_node["level"],
            "to_level": b_node["level"],
            "level_change": (
                a_node["level"] != b_node["level"]),
            "pathways_count": len(seg_pw),
            "pathways": seg_pw,
        })
    return segments


# -------------------- Command --------------------

class Command(BaseCommand):
    """Exporta a YAML el grafo de una estación.

    Ejemplos::

        python manage.py export_station_graph Mixcoac
        python manage.py export_station_graph Mixcoac \\
            --origin L7-MIXCOAC-P-01 \\
            --destination L12-MIXCOAC-P-01
    """

    help = (
        "Exporta a YAML los stops y pathways de una estación. "
        "Si se indica --origin y --destination calcula la ruta "
        "canónica y agrupa los pathways paralelos por tramo.")

    def add_arguments(self, parser) -> None:
        parser.add_argument("station_name", type=str)
        parser.add_argument(
            "--output", type=str, default=None,
            help="Ruta YAML de salida "
                 "(default: docs/<station>_graph.yaml).")
        parser.add_argument(
            "--origin", type=str, default=None,
            help="stop_id (largo o corto) del origen.")
        parser.add_argument(
            "--destination", type=str, default=None,
            help="stop_id (largo o corto) del destino.")

    def handle(self, *args, **opts) -> None:
        name = opts["station_name"]
        station = Station.objects.filter(name__iexact=name).first()
        if not station:
            raise CommandError(f"Estación {name!r} no encontrada")
        token = station.name.upper()

        all_ids, rows = _collect_stops(station)
        nodes, levels, id_to_short = _build_nodes_levels(rows, token)
        edges, duplicates = _build_edges(all_ids, id_to_short)
        nodes_by_id = {n["id"]: n for n in nodes}

        graph: dict[str, Any] = {
            "station": station.name,
            "station_db_id": station.id,
            "summary": {
                "stops": len(nodes),
                "pathways_unique": len(edges),
                "pathways_duplicates_omitted": duplicates,
                "levels": len(levels),
            },
            "pathway_modes": dict(sorted(PATHWAY_MODE_SLUG.items())),
            "levels": levels,
            "nodes": nodes,
            "edges": edges,
        }

        if opts.get("origin") and opts.get("destination"):
            graph["canonical_path"] = self._build_canonical(
                edges, nodes, nodes_by_id,
                opts["origin"], opts["destination"])

        out_arg = opts.get("output")
        out_path = Path(
            out_arg or f"docs/{name.lower()}_graph.yaml")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(
                graph, fh, sort_keys=False, allow_unicode=True,
                default_flow_style=False, width=100)
        self.stdout.write(self.style.SUCCESS(
            f"YAML escrito en: {out_path} "
            f"({len(nodes)} stops, {len(edges)} pathways"
            + (f", duplicados omitidos: {duplicates}"
               if duplicates else "")
            + ")"))

    def _build_canonical(
        self, edges: list[dict], nodes: list[dict],
        nodes_by_id: dict[str, dict], origin: str, destination: str,
    ) -> dict:
        long_to_short = {n["stop_id"]: n["id"] for n in nodes if n["stop_id"]}

        def resolve(x: str) -> str:
            if x in nodes_by_id:
                return x
            if x in long_to_short:
                return long_to_short[x]
            raise CommandError(f"Nodo {x!r} no encontrado")

        src = resolve(origin)
        dst = resolve(destination)
        path = _bfs_path(edges, src, dst)
        segments = _segments_with_parallels(edges, path, nodes_by_id)
        return {
            "origin": src,
            "destination": dst,
            "hops": len(path) - 1,
            "nodes_in_order": path,
            "segments": segments,
        }
