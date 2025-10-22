from rest_framework.decorators import action
from rest_framework import viewsets, permissions
# from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request

from report.models import StairReport
from api.views.report.serializers import (
    StairReportSerializer,
)


class StairReportViewSet(viewsets.ModelViewSet):

    request: Request
    queryset = StairReport.objects.all()
    # .select_related(
    #     'main_route', 'station', 'stop'
    # )

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['main_route__route_short_name']

    serializer_class = StairReportSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        user = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data)
