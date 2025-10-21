from django.db import models
from profile_auth.models import User
from stop.models import Station
from stair.models import Stair


class StationReport(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(
        Station, on_delete=models.CASCADE,
        verbose_name="Estación reportada"
    )
    date_reported = models.DateTimeField(
        auto_now=True, verbose_name="Fecha/hora de reporte"
    )
    date_received = models.DateTimeField(
        auto_now=True, verbose_name="Fecha/hora de recepción"
    )

    def __str__(self):
        return f"Reporte de estación {self.station} por {self.user}"

    class Meta:
        verbose_name = "Reporte de estación"
        verbose_name_plural = "Reportes de estaciones"


class StairReport(models.Model):
    stair = models.ForeignKey(
        Stair, on_delete=models.CASCADE,
        verbose_name="Escalera reportada"
    )
    code_identifiers = models.JSONField(
        blank=True, null=True, default=list,
        verbose_name="Todos los códigos identificadores"
    )
    route_start = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Inicio de la ruta"
    )
    path_start = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Dónde inicia de escalera"
    )
    path_end = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Dónde termina la escalera"
    )
    route_end = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Fin de la ruta"
    )
    is_aligned = models.BooleanField(
        default=False, verbose_name="¿Está alineada con el ID"
    )



