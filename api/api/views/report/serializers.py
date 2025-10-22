# serializers.py

from rest_framework import serializers

from report.models import StairReport, EvidenceImage


class StairReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StairReport
        fields = "__all__"


class EvidenceImageSerializer(serializers.ModelSerializer):
    # name = serializers.ReadOnlyField(source="file.name")
    # url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = EvidenceImage
        fields = "__all__"
