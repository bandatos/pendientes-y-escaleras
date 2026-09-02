"""Lectura del grafo de una estación desde la base, sin colapsar nada.

`export_station_graph` agrupa los pathways paralelos porque le sirve
para narrar rutas; aquí cada pathway paralelo es un objeto distinto que
hay que dibujar, así que se leen uno a uno.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape

from stop.models import Stop
from stair.models import Pathway

# 'L2-PORTALES-N-05' -> 'N-05'; la clave de plantilla es el sufijo, lo
# único estable entre estaciones hermanas de una misma familia.
_KEY_RE = re.compile(r"([A-Z]+-\d+)$")


@dataclass
class GraphStop:
    stop_id: str
    key: str
    name: str
    location_type_id: int
    level_index: float | None
    level_name: str | None
    entrance: str | None
    miro_id: str | None


@dataclass
class GraphPathway:
    pathway_id: str
    from_key: str
    to_key: str
    mode_id: int
    is_bidirectional: bool
    index: int
    miro_id: str | None


@dataclass
class StationGraph:
    station_name: str
    stop_id: str
    stops: dict[str, GraphStop]
    pathways: list[GraphPathway]


def stop_key(stop_id: str) -> str:
    m = _KEY_RE.search(stop_id or "")
    return m.group(1) if m else stop_id


def load_station_graph(station_stop_id: str) -> StationGraph:
    parent = Stop.objects.select_related("station").get(
        stop_id=station_stop_id)
    rows = (Stop.objects.filter(parent_station=parent)
            .select_related("level", "location_type"))
    stops: dict[str, GraphStop] = {}
    by_db_id: dict[int, GraphStop] = {}
    for s in rows:
        gs = GraphStop(
            stop_id=s.stop_id,
            key=stop_key(s.stop_id),
            name=unescape(s.stop_name or ""),
            location_type_id=s.location_type_id,
            level_index=s.level and s.level.level_index,
            level_name=s.level and s.level.level_name,
            entrance=s.entrance,
            miro_id=s.miro_id,
        )
        stops[gs.key] = gs
        by_db_id[s.id] = gs
    db_ids = list(by_db_id)
    pathways = []
    groups: dict[tuple, int] = {}
    qs = (Pathway.objects.filter(from_stop_id__in=db_ids,
                                 to_stop_id__in=db_ids)
          .order_by("miro_id", "id"))
    for p in qs:
        f = by_db_id[p.from_stop_id]
        t = by_db_id[p.to_stop_id]
        # El par va ordenado: dos pathways paralelos del mismo modo son
        # el mismo grupo aunque la base los guarde en sentidos opuestos,
        # y así el índice que los distingue no depende de ese sentido.
        group = (tuple(sorted((f.key, t.key))), p.pathway_mode_id)
        idx = groups.get(group, 0)
        groups[group] = idx + 1
        pathways.append(GraphPathway(
            pathway_id=p.pathway_id,
            from_key=f.key,
            to_key=t.key,
            mode_id=p.pathway_mode_id,
            is_bidirectional=bool(p.is_bidirectional),
            index=idx,
            miro_id=p.miro_id,
        ))
    name = parent.station.name if parent.station else unescape(
        parent.stop_name or "")
    return StationGraph(name, parent.stop_id, stops, pathways)
