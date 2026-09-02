"""StopMixin: stop detection and creation logic for MiroSchemaBuilder."""
from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING
from stop.models import Stop

from utils.miro.parsers import (
    _direction_text, _is_other_system, _item_center, _normalize_title,
    _parse_content, _resolve_line)

if TYPE_CHECKING:
    from utils.miro.builder import MiroSchemaBuilder


def assign_platform_entrances(
    platforms: list[tuple[str, str, str | None]],
    station_names: set[str],
) -> list[str]:
    """Decide el `entrance` OSM de cada andén de una estación.

    En el Metro de la CDMX el sentido de circulación de los andenes no es
    libre: en una terminal el andén cuyo letrero anuncia la propia estación
    solo recibe trenes (los pasajeros bajan, `exit`) y el otro solo los
    despacha (`entrance`); donde la línea tiene tres andenes, el central
    es el de descenso y los dos laterales los de ascenso. Con uno o dos
    andenes sin esas marcas el andén sirve en ambos sentidos (`yes`).

    Args:
        platforms: `(línea, nombre del andén, destino tras la flecha)`.
        station_names: `stop_name` y `short_name` de la estación padre.

    Returns:
        Un valor de `ENTRANCE_CHOICES` por andén, en el mismo orden.
    """
    names = {_normalize_title(n) for n in station_names if n}
    by_line: dict[str, list[int]] = defaultdict(list)
    for idx, (line, _, _) in enumerate(platforms):
        by_line[line].append(idx)

    result = ['yes'] * len(platforms)
    for indexes in by_line.values():
        terminals = [
            i for i in indexes
            if platforms[i][2] and _normalize_title(platforms[i][2]) in names
        ]
        if len(indexes) == 2 and len(terminals) == 1:
            for i in indexes:
                result[i] = 'exit' if i in terminals else 'entrance'
            continue
        centrals = [
            i for i in indexes
            if 'central' in _normalize_title(platforms[i][1])
        ]
        if len(indexes) == 3 and len(centrals) == 1:
            for i in indexes:
                result[i] = 'exit' if i in centrals else 'entrance'
    return result


class StopMixin:
    """Mixin that provides Stop-related methods to MiroSchemaBuilder."""

    def _find_double_pairs(self: MiroSchemaBuilder) -> list[tuple[str, str]]:
        """Returns [(id1, id2)] for entrances connected by dashed+diamond."""
        item_id_set = set(self._item_map)
        pairs = []
        for conn in self._connectors:
            style = conn.get('style', {})
            if style.get('strokeStyle') != 'dashed':
                continue
            if (style.get('startStrokeCap') != 'diamond'
                    or style.get('endStrokeCap') != 'diamond'):
                continue
            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if (start_id and end_id
                    and start_id in item_id_set
                    and end_id in item_id_set):
                pairs.append((start_id, end_id))
        return pairs

    def _get_double_stop_codes(self: MiroSchemaBuilder) -> dict[str, str]:
        """Returns {item_id: 'A' or 'B'} for double entrance pairs."""
        codes: dict[str, str] = {}
        for id1, id2 in self._find_double_pairs():
            x1, _ = _item_center(self._item_map[id1])
            x2, _ = _item_center(self._item_map[id2])
            if x1 <= x2:
                codes[id1], codes[id2] = 'A', 'B'
            else:
                codes[id1], codes[id2] = 'B', 'A'
        return codes

    def _station_names(self: MiroSchemaBuilder) -> set[str]:
        names = {self.frame_title}
        for stop in self._station_stops:
            names.update({stop.stop_name, stop.short_name})
        return {n for n in names if n}

    def _platform_entrances(self: MiroSchemaBuilder) -> dict[str, str]:
        """Returns {item_id: entrance} for the frame's platform shapes."""
        items = self.get_items_by_shape('round_rectangle')
        rows: list[tuple[str, str, str | None]] = []
        ids: list[str] = []
        for item in items:
            if _is_other_system(item):
                continue
            line = _resolve_line(item)
            if not line and (route := self._get_route(None)):
                line = f"L{route.route_short_name}"
            if not line:
                continue
            name = _parse_content(item.get('data', {}).get('content', ''))
            rows.append((line, name['name'], _direction_text(name['name'])))
            ids.append(item['id'])
        values = assign_platform_entrances(rows, self._station_names())
        return dict(zip(ids, values))

    def _create_stops(
            self: MiroSchemaBuilder, stop_codes: dict[str, str]
    ) -> None:
        self._skipped: list[dict] = []
        seq_counters: dict[tuple, int] = defaultdict(int)
        self._platform_entrance_map = self._platform_entrances()

        shapes = [
            (self.get_items_by_shape('round_rectangle'), 0, 'P'),
            (self.get_items_by_shape('rectangle'),       2, 'E'),
            (self.get_items_by_shape('circle'),          3, 'N'),
        ]

        for item_list, loc_type_id, type_abbrev in shapes:
            for item in item_list:
                self._build_stop_record(
                    item, loc_type_id, type_abbrev,
                    stop_codes, seq_counters)

    def _build_stop_record(
        self: MiroSchemaBuilder,
        item: dict,
        loc_type_id: int,
        type_abbrev: str,
        stop_codes: dict,
        seq_counters: dict,
    ) -> None:
        if _is_other_system(item):
            self._skipped.append({
                'miro_id': item['id'],
                'reason': 'other transit system',
            })
            return

        parsed = _parse_content(item.get('data', {}).get('content', ''))
        line = _resolve_line(item)
        route = self._get_route(line)
        if not line and route:
            line = f"L{route.route_short_name}"

        if not line:
            self._skipped.append({
                'miro_id': item['id'],
                'reason': 'no line prefix detected',
            })
            return


        parent = next(
            (s for s in self._station_stops
             if s.route and s.route.route_short_name == line),
            self._station_stops[0],
        )

        item_y = self._item_y_map[item['id']]
        level_entry = self._find_level_for_y(item_y, line)
        level_obj = None
        if level_entry:
            level_id = self._make_level_id(line, level_entry)
            level_obj = self._level_obj_map.get(level_id)

        seq_key = (line, type_abbrev)
        seq_counters[seq_key] += 1
        stop_id = (f'{line}-{self.station_slug}'
                   f'-{type_abbrev}-{seq_counters[seq_key]:02d}')

        if loc_type_id == 2:
            entrance = parsed['direction'] or 'yes'
        elif loc_type_id == 0:
            entrance = self._platform_entrance_map.get(item['id'])
        else:
            entrance = None

        obj, _ = Stop.objects.update_or_create(
            stop_id=stop_id,
            defaults={
                'miro_id': item['id'],
                'stop_name': parsed['name'],
                'entrance': entrance,
                'stop_desc': parsed['desc'],
                'is_closed': parsed['is_closed'],
                'is_double': parsed['is_double'],
                'location_type': self._get_loc_type(loc_type_id),
                'parent_station': parent,
                'route': route,
                'level': level_obj,
                'stop_code': stop_codes.get(item['id']),
            }
        )
        self._stop_obj_map[item['id']] = obj