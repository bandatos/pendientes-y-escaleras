from rest_framework import serializers

from stair.models import Stair


class StairSerializer(serializers.ModelSerializer):
    station = serializers.IntegerField(
        source='stop.station_id', read_only=True)

    class Meta:
        model = Stair
        fields = [
            "id",
            "number",
            "stop",
            "station",
        ]

class StairCatSerializer(serializers.ModelSerializer):
    station = serializers.IntegerField(
        source='stop.station_id', read_only=True)
    is_working = serializers.BooleanField(read_only=True)
    status_maintenance = serializers.CharField(read_only=True)
    date_reported = serializers.DateTimeField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Stair
        fields = [
            "id",
            "number",
            "stop",
            "station",
            "is_working",
            "status_maintenance",
            "date_reported",
            "user_id",
        ]
