# serializers.py

from rest_framework import serializers

from report.models import StairReport


class StairReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StairReport
        fields = "__all__"

