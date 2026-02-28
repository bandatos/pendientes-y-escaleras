# serializers.py

from rest_framework import serializers

from report.models import StairReport, EvidenceImage
from stair.models import Stair


class EvidenceImageSerializer(serializers.ModelSerializer):
    # name = serializers.ReadOnlyField(source="file.name")
    # url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = EvidenceImage
        fields = "__all__"


class EvidenceImageUrlsSerializer(serializers.RelatedField):
    def to_representation(self, value):
        url = value.image.url
        return url.replace(
            "https://bandatos.s3.us-west-2.amazonaws.com/escaleras",
            "https://apiescaleras.bandatos.org/media")


class StairExportSerializer(serializers.ModelSerializer):
    stop_name = serializers.ReadOnlyField(source="stop.stop_name")
    route_name = serializers.ReadOnlyField(source="stop.route.route_short_name")

    class Meta:
        model = Stair
        fields = [
            "id",
            "number",
            "original_direction",
            "original_location",
            "stop_name",
            "route_name",
        ]


class StairReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StairReport
        fields = "__all__"
        read_only_fields = ['user']  # El user se asigna automáticamente en el ViewSet


class StairReportExportSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source="user.first_name")
    stair = StairExportSerializer(read_only=True)
    images = EvidenceImageUrlsSerializer(many=True, read_only=True)
    # stop_name = serializers.ReadOnlyField(source="stair.stop.stop_name")

    class Meta:
        model = StairReport
        fields = [
            "id",
            "first_name",
            "stair",
            "status_maintenance",
            "other_status_maintenance",
            "code_identifiers",
            "route_start",
            "path_start",
            "path_end",
            "route_end",
            "is_working",
            "details",
            "direction_observed",
            "date_reported",
            "images",
        ]

