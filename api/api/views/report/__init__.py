from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
# from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request

from report.models import StairReport, EvidenceImage
from api.views.report.serializers import (
    StairReportSerializer, EvidenceImageSerializer
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


class AscertainableViewSet(viewsets.ModelViewSet):
    queryset = EvidenceImage.objects.all()
    serializer_class = EvidenceImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    # action_serializers = {
    #     "list": EvidenceImageSerializer,
    #     "retrieve": serializers.DataFileEditSerializer,
    #     "create": EvidenceImageSerializer,
    #     "update": serializers.DataFileEditSerializer,
    #     "delete": EvidenceImageSerializer,
    # }

    def create(self, request, stair_report_id=False, **kwargs):

        image_file = request.data

        stair_report = StairReport.objects.get(id=stair_report_id)
        image_file['stair_report'] = stair_report.id

        serializer_image_file = self.get_serializer_class()(data=image_file)
        if serializer_image_file.is_valid():
            serializer_image_file.save()
        else:
            return Response({"errors": serializer_image_file.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            serializer_image_file.data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):

        image_file = self.get_object()
        data = request.data

        serializer_image_file = self.get_serializer_class()(
            image_file, data=data)
        if serializer_image_file.is_valid():
            serializer_image_file.save()
        else:
            return Response({"errors": serializer_image_file.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            serializer_image_file.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def destroy(self, request, **kwargs):
        image_file = self.get_object()
        self.perform_destroy(image_file)
        return Response(status=status.HTTP_200_OK)

