"""StopMixin: stop detection and creation logic for MiroSchemaBuilder."""
from __future__ import annotations
from collections import defaultdict
from typing import TYPE_CHECKING
from stop.models import Stop

from utils.miro.parsers import _item_center, _parse_content, _resolve_line

if TYPE_CHECKING:
    from utils.miro.builder import MiroSchemaBuilder


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

    def _create_stops(
            self: MiroSchemaBuilder, stop_codes: dict[str, str]
    ) -> None:
        self._skipped: list[dict] = []
        seq_counters: dict[tuple, int] = defaultdict(int)

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

        obj, _ = Stop.objects.get_or_create(
            stop_id=stop_id,
            defaults={
                'miro_id': item['id'],
                'stop_name': parsed['name'],
                'stop_desc': parsed['desc'],
                'is_closed': parsed['is_closed'],
                'location_type': self._get_loc_type(loc_type_id),
                'parent_station': parent,
                'route': route,
                'level': level_obj,
                'stop_code': stop_codes.get(item['id']),
            }
        )
        self._stop_obj_map[item['id']] = obj