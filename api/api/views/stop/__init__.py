from rest_framework.decorators import action
from rest_framework import viewsets, permissions
# from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request

from stop.models import Station
from api.views.stop.serializers import (
    StationFullSerializer, StationCatSerializer)


class StationViewSet(viewsets.ModelViewSet):

    request: Request
    queryset = Station.objects.all()

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['main_route__route_short_name']

    serializer_class = StationCatSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': StationFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
