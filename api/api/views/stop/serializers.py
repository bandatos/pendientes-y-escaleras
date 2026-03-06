from rest_framework import serializers

from stop.models import Level, Route, Station, Stop
from api.views.stair.serializers import StairSerializer
from stair.models import Stair

class RouteCatSerializer(serializers.ModelSerializer):
    route_miro_name = serializers.SerializerMethodField()
    
    def get_route_miro_name(self, obj) -> str | None:
        """Returns route as 'L<short_name>' (e.g. 'L7', 'L12')."""
        if obj.route_short_name:
            return f"L{obj.route_short_name}"
        return None

    class Meta:
        model = Route
        fields = [
            "id",
            "route_id",
            "route_short_name",
            "route_long_name",
            "route_miro_name",
            "route_desc",
            "route_color",
            "route_text_color",
        ]
        
        
class LevelSerializer(serializers.ModelSerializer):
    """Serializer for Level — used by MiroSchemaBuilder and preview.

    ``route`` devuelve el PK entero de la ruta (FK).
    ``route_line`` devuelve la etiqueta 'L<N>' usada en el grafo de preview.
    ``route_full`` devuelve el objeto Route completo.
    """

    route_full = RouteCatSerializer(read_only=True, source='route')
    route_line = serializers.SerializerMethodField()

    def get_route_line(self, obj) -> str | None:
        """Returns route as 'L<short_name>' (e.g. 'L7', 'L12')."""
        if obj.route and obj.route.route_short_name:
            sn = obj.route.route_short_name
            return sn if sn.startswith('L') else f"L{sn}"
        return None

    class Meta:
        model = Level
        fields = [
            'id', 'level_id', 'level_index', 'level_name',
            'route', 'route_line', 'route_full',
        ]


class RoutesSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        return value.route_id


class StationCatSerializer(serializers.ModelSerializer):

    routes = RoutesSerializer(
        many=True, read_only=True, source='stops')
    # stairs = serializers.SerializerMethodField()

    def get_stairs(self, obj):
        stairs = StairSerializer(
            Stair.objects.filter(stop__station=obj), many=True).data
        return stairs

    class Meta:
        model = Station
        fields = "__all__"
        read_only_fields = [
            "routes",
            # "stairs",
        ]


class StationFullSerializer(StationCatSerializer):

    stairs = serializers.SerializerMethodField()

    def get_stairs(self, obj):
        stairs = StairSerializer(
            Stair.objects.filter(stop__station=obj), many=True).data
        return stairs

    class Meta:
        model = Station
        fields = "__all__"
        read_only_fields = [
            "routes",
            "stairs",
        ]


class StopCatSerializer(serializers.ModelSerializer):
    """Serializer for Stop catalog and Miro builder preview.

    The ``route`` field returns the FK integer PK (existing API behavior).
    Use ``route_line`` for the human-readable 'L<N>' label needed by the
    Miro preview graph.
    """

    name = serializers.CharField(source='stop_name')
    level_index = serializers.FloatField(
        source='level.level_index', read_only=True, allow_null=True)
    route_line = serializers.SerializerMethodField()

    def get_route_line(self, obj) -> str | None:
        """Returns route as 'L<short_name>' (e.g. 'L7', 'L12')."""
        if obj.route and obj.route.route_short_name:
            sn = obj.route.route_short_name
            return sn if sn.startswith('L') else f"L{sn}"
        return None

    class Meta:
        model = Stop
        fields = [
            "id",
            "stop_id",
            "name",
            "stop_name",
            "stop_desc",
            "miro_id",
            "is_closed",
            "stop_code",
            "location_type",
            "level_index",
            "route_line",
            "station",
            "route",
        ]
