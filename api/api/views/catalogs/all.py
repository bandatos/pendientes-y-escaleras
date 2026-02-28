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
from django.db.models import OuterRef, Subquery

from stair.models import Stair
from report.models import StairReport
from api.views.stair.serializers import StairCatSerializer


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):

        metro_stops = Stop.objects.filter(location_type=1)
        # all_stairs = Stair.objects.all().select_related('stop')
        all_stations = Station.objects.all().prefetch_related('stops')
        latest_report = StairReport.objects.filter(
            stair=OuterRef('pk')
        ).order_by('-id')
        all_stairs = Stair.objects.annotate(
            is_working=Subquery(latest_report.values('is_working')[:1]),
            status_maintenance=Subquery(latest_report.values('status_maintenance')[:1]),
            date_reported=Subquery(latest_report.values('date_reported')[:1]),
            user_id=Subquery(latest_report.values('user_id')[:1]),
        ).select_related('stop')

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


        # query_stair = { 'stair': OuterRef('id') }
        # last_report = StairReport.objects.filter(**query_stair) \
        #     .order_by('-id')
        # annotations = {
        #     "stair_report_id": Subquery(last_report.values('id')[:1]),
        #     "stair_report__is_working": Subquery(
        #         last_report.values('is_working')[:1]),
        #     "stair_report__status_maintenance": Subquery(
        #         last_report.values('status_maintenance')[:1]),
        #     "stair_report__date_reported": Subquery(
        #         last_report.values('date_reported')[:1]),
        # }
        # queryset_stairs = Stair.objects.filter(stair_reports__isnull=False) \
        #     .annotate(annotations)


        return Response(catalogs)
