from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
# from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request
from api.views.action_export_xls import ExportXlsMixin
from report.models import StairReport, EvidenceImage
from api.views.report.serializers import (
    StairReportSerializer, EvidenceImageSerializer,
    StairReportExportSerializer
)


class StairReportViewSet(viewsets.ModelViewSet, ExportXlsMixin):

    request: Request
    queryset = StairReport.objects.all()
    # .select_related(
    #     'main_route', 'station', 'stop'
    # )

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering = ['main_route__route_short_name']

    serializer_class = StairReportSerializer

    xls_attrs = [
        {
            "name": "ID de Reporte",
            "width": 5,
            "field": "id"
        },
        {
            "name": "Fecha de reporte",
            "width": 15,
            "field": "date_reported"
        },
        {
            "name": "ID de escalera",
            "width": 5,
            "field": "stair__id"
        },
        {
            "name": "Estación",
            "width": 25,
            "field": "stair__stop_name",
        },
        {
            "name": "Nombre reportante",
            "width": 15,
            "field": "first_name"
        },
        {
            "name": "¿Está funcionando?",
            "width": 6,
            "field": "is_working"
        },
        {
            "name": "Dirección observada",
            "width": 8,
            "field": "direction_observed"
        },
        {
            "name": "Status de mantenimiento",
            "width": 15,
            "field": "status_maintenance"
        },
        {
            "name": "Códigos de identificación",
            "width": 20,
            "field": "code_identifiers"
        },
        {
            "name": "Inicio de la ruta",
            "width": 26,
            "field": "route_start"
        },
        {
            "name": "Dónde inicia la escalera",
            "width": 26,
            "field": "path_start"
        },
        {
            "name": "Dónde termina la escalera",
            "width": 26,
            "field": "path_end"
        },
        {
            "name": "Fin de la ruta",
            "width": 26,
            "field": "route_end"
        },
        {
            "name": "Dirección (Según STC-Metro)",
            "width": 22,
            "field": "stair__original_direction"
        },
        {
            "name": "Ubicación (Según STC-Metro)",
            "width": 22,
            "field": "stair__original_location"
        },
        {
            "name": "Línea (Según STC-Metro)",
            "width": 6,
            "field": "stair__route_name"
        },
        {
            "name": "Otros detalles",
            "width": 30,
            "field": "details"
        },
        {
            "name": "Imágenes de evidencia",
            "width": 50,
            "field": "images"
        }

    ]
    xls_name = "Todos los reportes de escaleras"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "export_xls":
            queryset = StairReport.objects.all().select_related(
                "stair__stop",
                "stair__stop__route",
                "user",
            )
        return queryset

    def get_serializer_class(self):
        action_serializer = {
            'export_xls': StairReportExportSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

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

