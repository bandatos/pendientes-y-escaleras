from django.db import models
from stop.models import Station, Stop


class Pathway(models.Model):
    """
    Modelo basado en pathways.txt del estándar GTFS.
    Define las rutas/caminos dentro de las estaciones para navegación.
    Usa representación de grafo: nodos (locations) y aristas (pathways).
    """

    PATHWAY_MODE_CHOICES = [
        (1, 'Walkway'),
        (2, 'Stairs'),
        (3, 'Moving sidewalk/travelator'),
        (4, 'Escalator'),
        (5, 'Elevator'),
        (6, 'Fare gate'),
        (7, 'Exit gate'),
    ]

    # Choices para is_bidirectional
    IS_BIDIRECTIONAL_CHOICES = [
        (0, 'Unidirectional'),
        (1, 'Bidirectional'),
    ]

    # Primary key - pathway_id
    pathway_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Identifies a pathway"
    )

    from_stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        related_name='pathways_from',
        db_column='from_stop_id',
        help_text="Location at which the pathway begins"
    )

    to_stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        related_name='pathways_to',
        db_column='to_stop_id',
        help_text="Location at which the pathway ends"
    )

    pathway_mode = models.IntegerField(
        choices=PATHWAY_MODE_CHOICES,
    )

    is_bidirectional = models.IntegerField(
        choices=IS_BIDIRECTIONAL_CHOICES,
        help_text="0=Unidirectional (from→to only), 1=Bidirectional"
    )

    length = models.FloatField(
        blank=True, null=True,
        help_text="Horizontal length in meters of the pathway"
    )

    traversal_time = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Average time in seconds needed to walk through the pathway"
    )

    stair_count = models.IntegerField(
        blank=True, null=True,
        help_text="Number of stairs (positive=up, negative=down from from_stop to to_stop)"
    )

    max_slope = models.FloatField(
        blank=True, null=True,
        help_text="Maximum slope ratio (positive=upwards, negative=downwards)"
    )

    min_width = models.FloatField(
        blank=True, null=True,
        help_text="Minimum width of the pathway in meters"
    )

    signposted_as = models.TextField(
        blank=True, null=True,
        help_text="Public facing text from physical signage visible to riders"
    )

    reversed_signposted_as = models.TextField(
        blank=True, null=True,
        help_text="Signage text when pathway is used from to_stop to from_stop"
    )

    class Meta:
        verbose_name = 'Pathway'
        verbose_name_plural = 'Pathways'
        indexes = [
            models.Index(fields=['from_stop']),
            models.Index(fields=['to_stop']),
            models.Index(fields=['pathway_mode']),
        ]

    def __str__(self):
        mode_name = dict(self.PATHWAY_MODE_CHOICES).get(self.pathway_mode, 'Unknown')
        return f"{self.pathway_id}: {self.from_stop.stop_id} → {self.to_stop.stop_id} ({mode_name})"


class Stair(models.Model):
    number = models.SmallIntegerField()
    # station = models.ForeignKey(
    #     Station, on_delete=models.CASCADE, related_name='stairs')
    stop = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name='stairs',
        verbose_name="Estación (stop)"
    )
    code_identifiers = models.JSONField(
        blank=True, null=True, default=list,
        verbose_name="Todos los códigos identificadores"
    )
    original_direction = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Dirección según metro"
    )
    original_location = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Ubicación según metro"
    )
    validated = models.BooleanField(default=False)

    def __str__(self):
        return f"Escalera {self.number} en {self.stop.stop_name}"

    class Meta:
        verbose_name = "Escalera"
        verbose_name_plural = "Escaleras"






