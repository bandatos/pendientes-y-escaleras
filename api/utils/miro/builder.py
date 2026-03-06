"""MiroSchemaBuilder: converts a Miro frame into Stop/Level/Pathway records."""
from stop.models import LocationType, Stop, Route, Level
from stair.models import Pathway, PathwayMode

from .frames import search_frame_by_title, get_frame_items, get_frame_connectors
from .parsers import _slugify, _item_center
from .level_mixin import LevelMixin
from .stop_mixin import StopMixin
from .pathway_mixin import PathwayMixin


class MiroSchemaBuilder(LevelMixin, StopMixin, PathwayMixin):
    """
    Converts a Miro frame into Stop, Level, and Pathway DB records.

    Usage:
        result = MiroSchemaBuilder("Mixcoac").run()
    """

    def __init__(self, frame_title: str):
        self.frame_title = frame_title
        self.station_slug = _slugify(frame_title)

        # Set during run()
        self.frame: dict | None = None
        self._items: list = []
        self._item_map: dict[str, dict] = {}
        self._item_y_map: dict[str, float] = {}
        self._connectors: list = []
        self._station_stops: list = []
        self.routes: dict[str, Route] = {}
        self.unique_route: Route | None = None
        self._level_texts: dict[str, list[dict]] = {}
        self._level_obj_map: dict[str, object] = {}
        self._stop_obj_map: dict[str, Stop] = {}
        self._pathway_objs: list[Pathway] = []
        self._skipped: list[dict] = []

        # DB caches
        self._route_cache: dict[str, Route | None] = {}
        self._loc_type_cache: dict[int, LocationType | None] = {}
        self._mode_cache: dict[int, PathwayMode | None] = {}

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, reset_bd=False) -> dict | None:
        """
        Builds Stop, Level, and Pathway records from the Miro frame.

        Returns a dict with keys 'levels', 'stops', 'pathways', 'skipped',
        or None if the frame / station is not found.
        """
        from django.db.models import Q
        self.frame = search_frame_by_title(self.frame_title)
        if not self.frame:
            print(f"Frame '{self.frame_title}' no encontrado.")
            return None

        self._station_stops = list(
            Stop.objects.filter(stop_name__iexact=self.frame_title))
        if reset_bd:
            print("Resetting DB records for this station...")
            Stop.objects.filter(
                miro_id__isnull=False,
                parent_station__in=self._station_stops
            ).delete()
            Level.objects.all().delete()
            Pathway.objects.filter(
                Q(from_stop__in=self._station_stops)
                | Q(to_stop__in=self._station_stops)
            ).delete()
            # Levels and Pathways will cascade delete
        if not self._station_stops:
            print(f"Stops para '{self.frame_title}' "
                  f"no encontrados en la base de datos.")
            return None
        for station_stop in self._station_stops:
            if route := station_stop.route:
                self.routes[f"L{route.route_short_name}"] = route
            else:
                raise ValueError(
                    f"Stop '{station_stop.stop_id}' no tiene ruta asignada.")
        if len(self.routes) == 1:
            self.unique_route = next(iter(self.routes.values()))

        frame_id = self.frame.get('id')
        self._items = get_frame_items(frame_id)
        self._connectors = get_frame_connectors(frame_id, self._items)
        self._item_map = {item['id']: item for item in self._items}
        self._item_y_map = {
            iid: _item_center(item)[1]
            for iid, item in self._item_map.items()
        }

        text_items = [i for i in self._items if i.get('type') == 'text']
        self._level_texts = self._parse_level_texts(text_items)

        self._create_levels()
        stop_codes = self._get_double_stop_codes()
        self._create_stops(stop_codes)
        self._create_pathways()

        # Import here to avoid circular imports at module load time
        from api.views.stop.serializers import LevelSerializer, StopCatSerializer
        from api.views.stair.serializers import PathwaySerializer

        return {
            'levels': LevelSerializer(
                self._level_obj_map.values(), many=True).data,
            'stops': StopCatSerializer(
                self._stop_obj_map.values(), many=True).data,
            'pathways': PathwaySerializer(
                self._pathway_objs, many=True).data,
            'skipped': self._skipped,
        }

    # ------------------------------------------------------------------
    # Route / line resolution
    # ------------------------------------------------------------------

    def _get_route(self, line_prefix: str) -> Route | None:
        if self.unique_route:
            return self.unique_route
        line_prefix = line_prefix.upper()
        if line_prefix in self.routes:
            return self.routes[line_prefix]
        return None

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


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def build_schema(frame_title: str) -> dict | None:
    """Convenience wrapper for MiroSchemaBuilder.run()."""
    return MiroSchemaBuilder(frame_title).run()