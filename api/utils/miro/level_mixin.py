"""LevelMixin: level detection and creation logic for MiroSchemaBuilder."""
from __future__ import annotations
import html as html_module
from collections import defaultdict
from typing import TYPE_CHECKING

from stop.models import Level

from .parsers import _item_center, _strip_html, _LEVEL_TEXT_RE

if TYPE_CHECKING:
    from utils.miro.builder import MiroSchemaBuilder


class LevelMixin:
    """Mixin that provides Level-related methods to MiroSchemaBuilder."""

    def get_items_by_shape(self, shape: str) -> list:
        return [
            i for i in self._items
            if i.get('data', {}).get('shape') == shape
        ]

    def _get_limit_levels(self: MiroSchemaBuilder) -> list[dict]:
        """Returns [{'top': y1, 'bottom': y2}] bands delimited by right_arrow.

        The first band starts at frame top (y=0) and the last ends at
        frame bottom (geometry.height).
        """
        shape_divisors = self.get_items_by_shape('right_arrow')
        frame_top = 0
        frame_bottom = self.frame.get('geometry', {}).get('height', 0)
        sorted_arrows = sorted(
            shape_divisors, key=lambda s: _item_center(s)[1])
        level_limits = []
        last_top = frame_top
        for shape in sorted_arrows:
            _, y = _item_center(shape)
            level_limits.append({'top': last_top, 'bottom': y})
            last_top = y
        level_limits.append({'top': last_top, 'bottom': frame_bottom})
        return level_limits

    def _parse_level_texts(
        self: MiroSchemaBuilder, text_items: list,
    ) -> dict[str, list[dict]]:
        """Returns {line: [{top, bottom, index, has_andenes}]} sorted by top.

        Each entry represents a level band bounded by right_arrow divisors.
        If a text has no line prefix, self.unique_route is used; if that is
        also None, a ValueError is raised.
        """
        level_limits = self._get_limit_levels()
        result: dict[str, list] = defaultdict(list)

        for item in text_items:
            raw = html_module.unescape(
                _strip_html(item.get('data', {}).get('content', '')))
            m = _LEVEL_TEXT_RE.search(raw)
            if not m:
                print(f"No se pudo parsear nivel de texto: '{raw}'")
                continue
            line = m.group('line')
            if not line:
                if self.unique_route is None:
                    raise ValueError(
                        f"Texto de nivel sin línea y sin unique_route:"
                        f" '{raw}'")
                line = f"L{self.unique_route.route_short_name}"
            has_andenes = bool(m.group('andenes'))
            idx = m.group('level')
            _, y = _item_center(item)
            band = next(
                (lim for lim in level_limits
                 if lim['top'] <= y <= lim['bottom']),
                None,
            )
            if band is None:
                band = min(
                    level_limits,
                    key=lambda lim: min(
                        abs(y - lim['top']), abs(y - lim['bottom'])),
                )
            result[line].append({
                'top': band['top'],
                'bottom': band['bottom'],
                'index': idx,
                'has_andenes': has_andenes,
            })

        for line in result:
            result[line].sort(key=lambda e: e['top'])
        return dict(result)

    def _find_level_for_y(self: MiroSchemaBuilder, item_y: float, line: str) -> dict | None:
        """Returns the level band containing item_y for the given line.

        Falls back to the band whose center is nearest if none contains
        item_y.
        """
        entries = self._level_texts.get(line, [])
        if not entries:
            return None
        entry = next(
            (e for e in entries if e['top'] <= item_y <= e['bottom']),
            None,
        )
        if entry is not None:
            return entry
        return min(
            entries,
            key=lambda e: abs((e['top'] + e['bottom']) / 2 - item_y),
        )

    def _make_level_id(self: MiroSchemaBuilder, line: str, entry: dict) -> str:
        idx = entry['index']
        suffix = f'ANDENES{idx}' if entry['has_andenes'] else str(idx)
        return f'{self.station_slug}-{line}-{suffix}'

    def _create_levels(self: MiroSchemaBuilder) -> None:
        for line, entries in self._level_texts.items():
            route = self._get_route(line)
            for entry in entries:
                level_id = self._make_level_id(line, entry)
                level_name = 'Andenes' if entry['has_andenes'] else None
                obj, _ = Level.objects.get_or_create(
                    level_id=level_id,
                    defaults={
                        'level_index': entry['index'],
                        'level_name': level_name,
                        'route': route,
                    }
                )
                self._level_obj_map[level_id] = obj