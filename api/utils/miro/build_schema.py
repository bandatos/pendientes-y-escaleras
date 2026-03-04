import re
import unicodedata
from collections import defaultdict

from utils.miro.frames import (
    search_frame_by_title, get_frame_items, get_frame_connectors)
from stop.models import LocationType, Stop, Level, Route
from stair.models import Pathway, PathwayMode


# ---------------------------------------------------------------------------
# Module-level helpers (pure functions, no DB)
# ---------------------------------------------------------------------------

def _strip_html(html: str) -> str:
    text = re.sub(r'<br[^>]*/?>|<br>', ' ', html, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _parse_content(html: str) -> dict:
    """Returns {name, desc, is_closed} from a Miro shape HTML content."""
    text = _strip_html(html)
    paren_parts = re.findall(r'\(([^)]+)\)', text)
    desc = '; '.join(paren_parts) if paren_parts else None
    is_closed = bool(re.search(r'\[CLAUSURADA\]', text, re.IGNORECASE))
    name = re.sub(r'\s*\([^)]*\)', '', text)
    name = re.sub(r'\s*\[[^]]*\]', '', name).strip()
    return {'name': name, 'desc': desc, 'is_closed': is_closed}


def _item_center(item: dict) -> tuple[float, float]:
    """Returns (x, y) center. position.origin='center' → x,y already IS the center."""
    pos = item.get('position', {})
    return pos.get('x', 0.0), pos.get('y', 0.0)


def _slugify(text: str) -> str:
    text = unicodedata.normalize('NFD', text.upper())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', text)


_LINE_RE = re.compile(r'^(L\d{1,2}[AB]?)\b')
_LEVEL_TEXT_RE = re.compile(
    r'(L\d{1,2}[AB]?)\s+Nivel\s+(Andenes\s+)?([-\d]+|superficie\s+\d+)',
    re.IGNORECASE,
)

def _get_line_prefix(text: str) -> str | None:
    m = _LINE_RE.match(text.strip())
    return m.group(1) if m else None


def get_items_by_shape(items: list, shape: str) -> list:
    return [i for i in items if i.get('data', {}).get('shape') == shape]


# ---------------------------------------------------------------------------
# MiroSchemaBuilder
# ---------------------------------------------------------------------------

class MiroSchemaBuilder:
    """
    Converts a Miro frame into Stop, Level, and Pathway DB records.

    Usage:
        result = MiroSchemaBuilder("Mixcoac").run(dry_run=True)
        result = MiroSchemaBuilder("Mixcoac").run()
    """

    def __init__(self, frame_title: str):
        self.frame_title = frame_title
        self.station_slug = _slugify(frame_title)

        # Set during run()
        self._items: list = []
        self._item_map: dict[str, dict] = {}
        self._item_y_map: dict[str, float] = {}
        self._connectors: list = []
        self._station_stops: list = []
        self._level_texts: dict[str, list[dict]] = {}
        self._line_centroids: dict[str, float] = {}
        self._level_obj_map: dict[str, Level] = {}
        self._stop_obj_map: dict[str, Stop] = {}
        self._dry_run = False

        # DB caches
        self._route_cache: dict[str, Route | None] = {}
        self._loc_type_cache: dict[int, LocationType | None] = {}
        self._mode_cache: dict[int, PathwayMode | None] = {}

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, dry_run: bool = False) -> dict | None:
        """
        Builds Stop, Level, and Pathway records from the Miro frame.

        Returns a dict with keys 'levels', 'stops', 'pathways', 'skipped',
        or None if the frame / station is not found.
        """
        self._dry_run = dry_run

        frame = search_frame_by_title(self.frame_title)
        if not frame:
            print(f"Frame '{self.frame_title}' no encontrado.")
            return None

        self._station_stops = list(
            Stop.objects.filter(stop_name__iexact=self.frame_title))
        if not self._station_stops:
            print(f"Stops para '{self.frame_title}' no encontrados en la base de datos.")
            return None

        self._items = get_frame_items(frame['id'])
        self._connectors = get_frame_connectors(frame['id'], self._items)
        self._item_map = {item['id']: item for item in self._items}
        self._item_y_map = {iid: _item_center(item)[1]
                            for iid, item in self._item_map.items()}

        text_items = [i for i in self._items if i.get('type') == 'text']
        self._level_texts = self._parse_level_texts(text_items)
        self._line_centroids = self._build_line_centroids()

        levels = self._create_levels()
        stop_codes = self._get_double_stop_codes()
        stops = self._create_stops(stop_codes)
        pathways = self._create_pathways()

        return {
            'levels': levels,
            'stops': stops,
            'pathways': pathways,
            'skipped': self._skipped,
        }

    # ------------------------------------------------------------------
    # Level detection
    # ------------------------------------------------------------------

    def _parse_level_texts(self, text_items: list) -> dict[str, list[dict]]:
        """Returns {line: [{y, index, has_andenes}, ...]} sorted by y."""
        result: dict[str, list] = defaultdict(list)
        for item in text_items:
            raw = _strip_html(item.get('data', {}).get('content', ''))
            m = _LEVEL_TEXT_RE.search(raw)
            if not m:
                continue
            line = m.group(1)
            has_andenes = bool(m.group(2))
            raw_index = m.group(3).strip()
            if raw_index.lower().startswith('superficie'):
                idx = float(re.search(r'[-\d]+', raw_index).group())
            else:
                idx = float(raw_index)
            _, y = _item_center(item)
            result[line].append({'y': y, 'index': idx, 'has_andenes': has_andenes})
        for line in result:
            result[line].sort(key=lambda e: e['y'])
        return dict(result)

    def _nearest_level(self, item_y: float, line: str) -> dict | None:
        entries = self._level_texts.get(line, [])
        if not entries:
            return None
        return min(entries, key=lambda e: abs(e['y'] - item_y))

    def _make_level_id(self, line: str, entry: dict) -> str:
        idx = int(entry['index'])
        suffix = f'ANDENES{idx}' if entry['has_andenes'] else str(idx)
        return f'{self.station_slug}-{line}-{suffix}'

    # ------------------------------------------------------------------
    # Route / line resolution
    # ------------------------------------------------------------------

    def _build_line_centroids(self) -> dict[str, float]:
        """Returns {line_prefix: mean_x} for shapes that have a line prefix."""
        xs: dict[str, list] = defaultdict(list)
        for item in self._items:
            if item.get('type') != 'shape':
                continue
            content = _strip_html(item.get('data', {}).get('content', ''))
            prefix = _get_line_prefix(content)
            if prefix:
                x, _ = _item_center(item)
                xs[prefix].append(x)
        return {line: sum(vals) / len(vals) for line, vals in xs.items()}

    def _resolve_line(self, item: dict) -> str | None:
        content = _strip_html(item.get('data', {}).get('content', ''))
        prefix = _get_line_prefix(content)
        if prefix:
            return prefix
        all_lines = list(self._line_centroids)
        if len(all_lines) == 1:
            return all_lines[0]
        x, _ = _item_center(item)
        if not self._line_centroids:
            return None
        return min(self._line_centroids, key=lambda ln: abs(self._line_centroids[ln] - x))

    def _get_route(self, line_prefix: str) -> Route | None:
        if line_prefix not in self._route_cache:
            try:
                self._route_cache[line_prefix] = Route.objects.get(
                    route_short_name__iexact=line_prefix)
            except Route.DoesNotExist:
                self._route_cache[line_prefix] = None
        return self._route_cache[line_prefix]

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------

    def _get_loc_type(self, id_: int) -> LocationType | None:
        if id_ not in self._loc_type_cache:
            try:
                self._loc_type_cache[id_] = LocationType.objects.get(id=id_)
            except LocationType.DoesNotExist:
                self._loc_type_cache[id_] = None
        return self._loc_type_cache[id_]

    def _get_mode(self, id_: int) -> PathwayMode | None:
        if id_ not in self._mode_cache:
            try:
                self._mode_cache[id_] = PathwayMode.objects.get(id=id_)
            except PathwayMode.DoesNotExist:
                self._mode_cache[id_] = None
        return self._mode_cache[id_]

    def _get_stop_for_miro_id(self, miro_id: str) -> Stop | None:
        if miro_id in self._stop_obj_map:
            return self._stop_obj_map[miro_id]
        try:
            return Stop.objects.get(miro_id=miro_id)
        except Stop.DoesNotExist:
            return None

    # ------------------------------------------------------------------
    # Step 1: Levels
    # ------------------------------------------------------------------

    def _create_levels(self) -> list[dict]:
        preview = []
        for line, entries in self._level_texts.items():
            route = self._get_route(line)
            for entry in entries:
                level_id = self._make_level_id(line, entry)
                level_name = 'Andenes' if entry['has_andenes'] else None
                preview.append({
                    'level_id': level_id,
                    'level_index': entry['index'],
                    'level_name': level_name,
                    'route': line,
                })
                if not self._dry_run:
                    obj, _ = Level.objects.get_or_create(
                        level_id=level_id,
                        defaults={
                            'level_index': entry['index'],
                            'level_name': level_name,
                            'route': route,
                        }
                    )
                    self._level_obj_map[level_id] = obj
        return preview

    # ------------------------------------------------------------------
    # Step 2: Double entrance detection
    # ------------------------------------------------------------------

    def _find_double_pairs(self) -> list[tuple[str, str]]:
        """Returns [(id1, id2)] for entrances connected by dashed+diamond connectors."""
        item_id_set = set(self._item_map)
        pairs = []
        for conn in self._connectors:
            style = conn.get('style', {})
            if style.get('strokeStyle') != 'dashed':
                continue
            if style.get('startStrokeCap') != 'diamond' or style.get('endStrokeCap') != 'diamond':
                continue
            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if start_id and end_id and start_id in item_id_set and end_id in item_id_set:
                pairs.append((start_id, end_id))
        return pairs

    def _get_double_stop_codes(self) -> dict[str, str]:
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

    # ------------------------------------------------------------------
    # Step 3: Stops
    # ------------------------------------------------------------------

    def _create_stops(self, stop_codes: dict[str, str]) -> list[dict]:
        self._skipped: list[dict] = []
        seq_counters: dict[tuple, int] = defaultdict(int)
        preview = []

        shapes = [
            (get_items_by_shape(self._items, 'round_rectangle'), 0, 'P'),
            (get_items_by_shape(self._items, 'rectangle'),       2, 'E'),
            (get_items_by_shape(self._items, 'circle'),          3, 'N'),
        ]

        for item_list, loc_type_id, type_abbrev in shapes:
            for item in item_list:
                record = self._build_stop_record(
                    item, loc_type_id, type_abbrev, stop_codes, seq_counters)
                if record:
                    preview.append(record)

        return preview

    def _build_stop_record(
        self,
        item: dict,
        loc_type_id: int,
        type_abbrev: str,
        stop_codes: dict[str, str],
        seq_counters: dict,
    ) -> dict | None:
        parsed = _parse_content(item.get('data', {}).get('content', ''))
        line = self._resolve_line(item)
        if not line:
            self._skipped.append({'miro_id': item['id'], 'reason': 'no line prefix detected'})
            return None

        route = self._get_route(line)
        route_id = route.route_id if route else line

        parent = next(
            (s for s in self._station_stops
             if s.route and s.route.route_short_name == line),
            self._station_stops[0],
        )

        item_y = self._item_y_map[item['id']]
        level_entry = self._nearest_level(item_y, line)
        level_obj = None
        if level_entry:
            level_id = self._make_level_id(line, level_entry)
            level_obj = self._level_obj_map.get(level_id)

        seq_key = (route_id, type_abbrev)
        seq_counters[seq_key] += 1
        stop_id = f'{route_id}-{self.station_slug}-{type_abbrev}-{seq_counters[seq_key]:02d}'

        record = {
            'stop_id': stop_id,
            'miro_id': item['id'],
            'stop_name': parsed['name'],
            'stop_desc': parsed['desc'],
            'is_closed': parsed['is_closed'],
            'location_type_id': loc_type_id,
            'parent_station_stop_id': parent.stop_id,
            'route': line,
            'level_index': level_entry['index'] if level_entry else None,
            'stop_code': stop_codes.get(item['id']),
        }

        if not self._dry_run:
            obj, _ = Stop.objects.get_or_create(
                miro_id=item['id'],
                defaults={
                    'stop_id': stop_id,
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

        return record

    # ------------------------------------------------------------------
    # Step 4: Pathways
    # ------------------------------------------------------------------

    def _get_pathway_mode(self, connector: dict) -> int | None:
        style = connector.get('style', {})
        color = style.get('strokeColor', '').lower()
        start_cap = style.get('startStrokeCap', 'none')
        end_cap = style.get('endStrokeCap', 'none')

        if style.get('strokeStyle') == 'dashed':
            return None
        if color == '#6631d7':
            return 4  # Escalator
        if color == '#305bab':
            return 5  # Elevator
        if color == '#067429':
            return 3  # Moving sidewalk
        if color == '#b0b0b0':
            if start_cap == 'oval' and end_cap == 'oval':
                return 1  # Walkway
            return 2  # Stairs
        return None

    def _build_escalator_pairs(self) -> dict[frozenset, list]:
        pairs: dict[frozenset, list] = defaultdict(list)
        for conn in self._connectors:
            if self._get_pathway_mode(conn) != 4:
                continue
            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if start_id and end_id:
                pairs[frozenset([start_id, end_id])].append(conn)
        return dict(pairs)

    def _get_bidirectional(
        self, connector: dict, mode: int, escalator_pairs: dict,
    ) -> int:
        if mode in (1, 5):  # Walkway, Elevator
            return 1
        if mode == 3:        # Moving sidewalk
            return 0
        if mode == 4:        # Escalator
            start_id = connector['startItem']['id']
            end_id = connector['endItem']['id']
            pair_key = frozenset([start_id, end_id])
            if len(escalator_pairs.get(pair_key, [])) == 2:
                from_y = self._item_y_map.get(start_id, 0)
                to_y = self._item_y_map.get(end_id, 0)
                return 1 if from_y < to_y else 0
            return 0
        # Stairs: unidirectional if one cap is 'none'
        style = connector.get('style', {})
        if style.get('startStrokeCap') == 'none' or style.get('endStrokeCap') == 'none':
            return 0
        return 1

    @staticmethod
    def _extract_description(connector: dict) -> str | None:
        parts = []
        for caption in connector.get('captions', []):
            text = _strip_html(caption.get('content', ''))
            parts.extend(re.findall(r'\(([^)]+)\)', text))
        return '; '.join(parts) if parts else None

    def _create_pathways(self) -> list[dict]:
        escalator_pairs = self._build_escalator_pairs()
        preview = []

        for conn in self._connectors:
            mode_id = self._get_pathway_mode(conn)
            if mode_id is None:
                continue

            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if not start_id or not end_id:
                self._skipped.append(
                    {'miro_id': conn['id'], 'reason': 'connector missing endpoint'})
                continue

            is_bidir = self._get_bidirectional(conn, mode_id, escalator_pairs)
            description = self._extract_description(conn)

            if self._dry_run:
                preview.append({
                    'pathway_id': f'(miro:{start_id})--(miro:{end_id})',
                    'miro_id': conn['id'],
                    'from_stop': f'miro:{start_id}',
                    'to_stop': f'miro:{end_id}',
                    'pathway_mode': mode_id,
                    'is_bidirectional': is_bidir,
                    'pathway_description': description,
                })
                continue

            from_stop = self._get_stop_for_miro_id(start_id)
            to_stop = self._get_stop_for_miro_id(end_id)
            if not from_stop or not to_stop:
                self._skipped.append({
                    'miro_id': conn['id'],
                    'reason': f'stop not found for miro_id {start_id} or {end_id}',
                })
                continue

            pathway_id = f'{from_stop.stop_id}--{to_stop.stop_id}'
            record = {
                'pathway_id': pathway_id,
                'miro_id': conn['id'],
                'from_stop': from_stop.stop_id,
                'to_stop': to_stop.stop_id,
                'pathway_mode': mode_id,
                'is_bidirectional': is_bidir,
                'pathway_description': description,
            }
            preview.append(record)

            Pathway.objects.get_or_create(
                miro_id=conn['id'],
                defaults={
                    'pathway_id': pathway_id,
                    'from_stop': from_stop,
                    'to_stop': to_stop,
                    'pathway_mode': self._get_mode(mode_id),
                    'is_bidirectional': is_bidir,
                    'pathway_description': description,
                }
            )

        return preview


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def build_schema(frame_title: str, dry_run: bool = False) -> dict | None:
    return MiroSchemaBuilder(frame_title).run(dry_run=dry_run)