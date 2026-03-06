from django.db import models
from stop.models import Station, Stop

PATHWAY_MODE_CHOICES = [
    (1, 'Walkway'),
    (2, 'Stairs'),
    (3, 'Moving sidewalk/travelator'),
    (4, 'Escalator'),
    (5, 'Elevator'),
    (6, 'Fare gate'),
    (7, 'Exit gate'),
]


class PathwayMode(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        max_length=255, verbose_name="Nombre")
    gtfs_name = models.CharField(
        max_length=255, verbose_name="Nombre en GTFS",)
    icon = models.CharField(
        max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Pathway Mode'
        verbose_name_plural = 'Pathway Modes'

    def __str__(self):
        return f"{self.id} - {self.name}"


IS_BIDIRECTIONAL_CHOICES = [
    (0, 'Unidirectional'),
    (1, 'Bidirectional'),
]

class Pathway(models.Model):
    """
    Modelo basado en pathways.txt del estándar GTFS.
    Define las rutas/caminos dentro de las estaciones para navegación.
    Usa representación de grafo: nodos (locations) y aristas (pathways).
    """

    pathway_id = models.CharField(
        max_length=255, unique=True, db_index=True)
    from_stop = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name='pathways_from')
    to_stop = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name='pathways_to')
    pathway_mode = models.ForeignKey(
        PathwayMode, on_delete=models.CASCADE, blank=True, null=True)
    pathway_description = models.CharField(
        max_length=255, blank=True, null=True)
    is_bidirectional = models.IntegerField(choices=IS_BIDIRECTIONAL_CHOICES)
    length = models.FloatField(
        blank=True, null=True, help_text="Horizontal length in meters")
    traversal_time = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Average time in seconds needed to walk through the pathway")
    stair_count = models.IntegerField(
        blank=True, null=True,
        help_text="Number of stairs (positive=up, negative=down from from_stop to to_stop)")
    max_slope = models.FloatField(
        blank=True, null=True,
        help_text="Maximum slope ratio (positive=upwards, negative=downwards)")
    code_identifiers = models.JSONField(
        blank=True, null=True, default=list,
        verbose_name="Todos los códigos identificadores")
    validated = models.BooleanField(default=False)
    miro_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Pathway'
        verbose_name_plural = 'Pathways'
        indexes = [
            models.Index(fields=['from_stop']),
            models.Index(fields=['to_stop']),
            models.Index(fields=['pathway_mode']),
        ]

    def __str__(self):
        return (f"Pathway {self.pathway_id} from "
                f"{self.from_stop} to {self.to_stop}")


class Stair(models.Model):
    number = models.SmallIntegerField()
    # station = models.ForeignKey(
    #     Station, on_delete=models.CASCADE, related_name='stairs')
    stop = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name='stairs',
        verbose_name="Estación (stop)")
    code_identifiers = models.JSONField(
        blank=True, null=True, default=list,
        verbose_name="Todos los códigos identificadores")
    original_direction = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Dirección según metro")
    original_location = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Ubicación según metro")
    route_blur = models.BooleanField(
        default=False, verbose_name="Línea poco clara")
    validated = models.BooleanField(default=False)

    def __str__(self):
        return f"Escalera {self.number} en {self.stop.stop_name}"

    class Meta:
        verbose_name = "Escalera"
        verbose_name_plural = "Escaleras"






