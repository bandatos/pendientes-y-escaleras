from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

# from profile_auth.models import User
# from api.views.auth.serializers import UserProfileSerializer

from stop.models import Stop, Station, Route
from api.views.stop.serializers import (
    StopCatSerializer, StationCatSerializer,
    RouteCatSerializer,
)

from stair.models import Stair
from api.views.stair.serializers import StairCatSerializer


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):

        metro_stops = Stop.objects.filter(location_type=1)
        all_stairs = Stair.objects.all().select_related('stop')
        all_stations = Station.objects.all().prefetch_related('stops')
        catalogs = {
            # "user": UserProfileSerializer(
            #     User.objects.all(), many=True).data,
            "routes": RouteCatSerializer(
                Route.objects.all(), many=True).data,
            "stops": StopCatSerializer(
                metro_stops, many=True).data,
            "stations": StationCatSerializer(
                all_stations, many=True).data,
            "stairs": StairCatSerializer(
                all_stairs, many=True).data,
        }
        return Response(catalogs)
