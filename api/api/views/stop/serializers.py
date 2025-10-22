from rest_framework import serializers

from stop.models import Route, Station, Stop


class RouteCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id",
            "route_id",
            "route_short_name",
            "route_long_name",
            "route_desc",
            "route_color",
            "route_text_color",
        ]


class StationCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"


class StopCatSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='stop_name')

    class Meta:
        model = Stop
        fields = [
            "id",
            "stop_id",
            "name",
            "station",
            "route"
        ]
