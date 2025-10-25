from django.db import models
from profile_auth.models import User
from stop.models import Station
from stair.models import Stair


# class StationReport(models.Model):
#
#     station = models.ForeignKey(
#         Station, on_delete=models.CASCADE,
#         verbose_name="Estación reportada"
#     )
#
#     def __str__(self):
#         return f"Reporte de estación {self.station} por {self.user}"
#
#     class Meta:
#         verbose_name = "Reporte de estación"
#         verbose_name_plural = "Reportes de estaciones"


class StairReport(models.Model):

    # maintenance
    STATUS_MAINTENANCE_CHOICES = (
        ('full', 'En Reconstrucción'),
        ('medium', 'Mantenimiento Mayor (Tablas)'),
        ('minor', 'Mantenimiento Menor (Sin tablas)'),
        ('other', 'Otro tipo de mantenimiento'),
    )

    DIRECTION_CHOICES = (
        ('up', 'Hacia arriba'),
        ('down', 'Hacia abajo'),
    )

    stair = models.ForeignKey(
        Stair, on_delete=models.CASCADE,
        verbose_name="Escalera reportada"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # station_report = models.ForeignKey(
    #     StationReport, on_delete=models.CASCADE,
    #     verbose_name="Reporte de estación asociado"
    # )
    status_maintenance = models.CharField(
        max_length=10, choices=STATUS_MAINTENANCE_CHOICES,
        blank=True, null=True, verbose_name="Estado de mantenimiento"
    )
    other_status_maintenance = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Otro estado de mantenimiento"
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
    is_working = models.BooleanField(
        blank=True, null=True, verbose_name="¿Está funcionando?"
    )
    details = models.TextField(
        blank=True, null=True, verbose_name="Detalles adicionales"
    )
    direction_observed = models.CharField(
        max_length=10, choices=DIRECTION_CHOICES,
        blank=True, null=True, verbose_name="Dirección observada"
    )
    date_reported = models.DateTimeField(
        auto_now=True, verbose_name="Fecha/hora de reporte"
    )
    date_received = models.DateTimeField(
        auto_now=True, verbose_name="Fecha/hora de recepción"
    )

    def __str__(self):
        return f"Reporte de escalera {self.stair} por {self.user}"

    class Meta:
        verbose_name = "Reporte de escalera"
        verbose_name_plural = "Reportes de escaleras"


class EvidenceImage(models.Model):
    stair_report = models.ForeignKey(
        StairReport, on_delete=models.CASCADE,
        verbose_name="Reporte de escalera asociado"
    )
    image = models.ImageField(
        upload_to='evidence_images/',
        verbose_name="Imagen de evidencia"
    )

    def __str__(self):
        return f"Imagen de evidencia para {self.stair_report}"

    class Meta:
        verbose_name = "Imagen de evidencia"
        verbose_name_plural = "Imágenes de evidencia"


