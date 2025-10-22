from rest_framework import serializers

from stop.models import Route, Station, Stop


class RouteCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class StationCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"


class StopCatSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='stop_name')

    class Meta:
        model = Stop
        fields = [
            "stop_id",
            "name",
            "station",
            "route"
        ]
