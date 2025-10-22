from rest_framework import serializers

from stair.models import Stair


class StairCatSerializer(serializers.ModelSerializer):
    station = serializers.CharField(
        source='stop.station', read_only=True)

    class Meta:
        model = Stair
        fields = [
            "id",
            "stop",
            "number",
        ]
