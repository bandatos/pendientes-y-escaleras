from rest_framework import serializers

from stair.models import Pathway, Stair


class PathwaySerializer(serializers.ModelSerializer):
    """Serializer for Pathway — used by MiroSchemaBuilder and preview."""

    from_stop = serializers.CharField(source='from_stop.stop_id')
    to_stop = serializers.CharField(source='to_stop.stop_id')
    pathway_mode = serializers.IntegerField(source='pathway_mode_id')

    class Meta:
        model = Pathway
        fields = [
            'id',
            'pathway_id',
            'from_stop',
            'to_stop',
            'pathway_mode',
            'is_bidirectional',
            'pathway_description',
            'miro_id',
        ]


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
