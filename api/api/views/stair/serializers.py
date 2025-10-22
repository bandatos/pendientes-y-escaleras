from rest_framework import serializers

from stair.models import Stair


class StairCatSerializer(serializers.ModelSerializer):
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
