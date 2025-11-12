from rest_framework import serializers

from stop.models import Route, Station, Stop
from api.views.stair.serializers import StairSerializer
from stair.models import Stair


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


class StationFullSerializer(serializers.ModelSerializer):

    routes = RoutesSerializer(
        many=True, read_only=True, source='stops')
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
