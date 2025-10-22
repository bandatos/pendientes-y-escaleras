from django.db import models


class Route(models.Model):
    """
    Modelo basado en routes.txt del estándar GTFS.
    Representa una ruta de transporte.
    """

    ROUTE_TYPE_CHOICES = [
        (0, 'Tram, Streetcar, Light rail'),
        (1, 'Subway, Metro'),
        (2, 'Rail'),
        (3, 'Bus'),
        (4, 'Ferry'),
        (5, 'Cable tram'),
        (6, 'Aerial lift, suspended cable car'),
        (7, 'Funicular'),
        (11, 'Trolleybus'),
        (12, 'Monorail'),
    ]

    route_id = models.CharField(
        max_length=255,
        unique=True,

        db_index=True,
        help_text="Identifies a route"
    )

    # Temporalmente deshabilitado porque todos son del Metro CDMX
    # agency_id = models.ForeignKey(
    #     'Agency', on_delete=models.CASCADE, blank=True, null=True,
    #     related_name='routes', help_text="Empresa/organización que opera la ruta"
    # )

    route_short_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Nombre corto",
        help_text="Short name of a route (e.g., '32', '100X', 'Green')"
    )

    route_long_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nombre largo",
        help_text="Full name of a route"
    )

    route_desc = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Description of a route that provides useful,"
                  "quality information"
    )
    route_type = models.IntegerField(
        choices=ROUTE_TYPE_CHOICES, default=1,
        help_text="Indicates the type of transportation used on a route"
    )
    route_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL",
        help_text="URL of a web page about the particular route"
    )
    route_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        default='FFFFFF',
        help_text="Route color designation (hex color without #)"
    )
    route_text_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        default='000000',
        help_text="Legible color to use for text drawn against route_color"
    )
    route_sort_order = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Orders the routes for presentation to customers"
    )

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        indexes = [
            models.Index(fields=['route_type']),
            models.Index(fields=['route_short_name']),
        ]

    def __str__(self):
        if self.route_short_name and self.route_long_name:
            return f"{self.route_short_name} - {self.route_long_name}"
        return self.route_short_name or self.route_long_name or self.route_id


class Shape(models.Model):
    """
    Modelo basado en shapes.txt del estándar GTFS.
    Define puntos que describen el camino que sigue un vehículo.
    Cada registro representa un punto en la forma geográfica de la ruta.
    """

    shape_id = models.CharField(max_length=255, db_index=True)
    shape_pt_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitud del punto",
        help_text="Latitude of a shape point"
    )
    shape_pt_lon = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Longitud del punto",
        help_text="Longitude of a shape point"
    )
    shape_pt_sequence = models.PositiveIntegerField(
        verbose_name="Secuencia del punto",
        help_text="Sequence in which the shape points connect to form the shape"
    )
    shape_dist_traveled = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Distancia recorrida",
        help_text="Actual distance traveled along the shape from the first shape point"
    )

    class Meta:
        verbose_name = 'Shape'
        verbose_name_plural = 'Shapes'
        unique_together = [['shape_id', 'shape_pt_sequence']]
        indexes = [
            models.Index(fields=['shape_id', 'shape_pt_sequence']),
        ]
        ordering = ['shape_id', 'shape_pt_sequence']

    def __str__(self):
        return f"{self.shape_id} - Point {self.shape_pt_sequence}"


class Trip(models.Model):
    """
    Modelo basado en trips.txt del estándar GTFS.
    Representa un viaje de un vehículo a lo largo de una ruta.
    """

    DIRECTION_ID_CHOICES = [
        (0, 'Outbound travel'),
        (1, 'Inbound travel'),
    ]

    WHEELCHAIR_ACCESSIBLE_CHOICES = [
        (0, 'No accessibility information'),
        (1, 'Vehicle can accommodate at least one wheelchair'),
        (2, 'No wheelchairs can be accommodated'),
    ]

    trip_id = models.CharField(max_length=255, unique=True, db_index=True)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name='trips',
        verbose_name="Ruta",
    )

    trip_headsign = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Headsign",
        help_text="Text that appears on signage identifying the trip's destination"
    )

    trip_short_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Nombre corto del viaje",
        help_text="Public facing text used to identify the trip to riders"
    )

    direction_id = models.IntegerField(
        choices=DIRECTION_ID_CHOICES,
        blank=True,
        null=True,
        help_text="Indicates the direction of travel for a trip"
    )
    shape_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Identifies a geospatial shape describing the vehicle travel path"
    )
    # shape = models.ForeignKey(
    #     Shape,
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     related_name='trips',
    #     help_text="Identifies a geospatial shape describing the vehicle travel path"
    # )
    wheelchair_accessible = models.IntegerField(
        choices=WHEELCHAIR_ACCESSIBLE_CHOICES,
        default=0,
        blank=True,
        null=True,
        help_text="Indicates wheelchair accessibility"
    )

    class Meta:
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        # indexes = [
        #     models.Index(fields=['route', 'direction_id']),
        #     models.Index(fields=['block_id']),
        # ]

    def __str__(self):
        return f"{self.trip_id} - {self.trip_headsign or 'No headsign'}"


class Station(models.Model):

    name = models.CharField(max_length=255)
    main_route = models.ForeignKey(
        Route, on_delete=models.CASCADE,
        blank=True, null=True, related_name='main_stations'
    )
    x_position = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name="Posición X",
    )
    y_position = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name="Posición Y",
    )
    end_anchor = models.BooleanField(default=False)
    rotation = models.SmallIntegerField(blank=True, null=True)
    viz_params = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    class Meta:
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'


class Stop(models.Model):
    """
    Modelo basado en stops.txt del estándar GTFS.
    Representa ubicaciones: paradas/plataformas, estaciones, entradas/salidas,
    nodos genéricos o áreas de embarque.
    """

    LOCATION_TYPE_CHOICES = [
        (0, 'Stop/Platform'),
        (1, 'Station'),
        (2, 'Entrance/Exit'),
        (3, 'Generic Node'),
        (4, 'Boarding Area'),
    ]
    WHEELCHAIR_BOARDING_CHOICES = [
        (0, 'No accessibility information'),
        (1, 'Wheelchair accessible'),
        (2, 'Not wheelchair accessible'),
    ]
    # STOP_ACCESS_CHOICES = [
    #     (0, 'Cannot be directly accessed from street'),
    #     (1, 'Direct access from street'),
    # ]

    stop_id = models.CharField(
        max_length=255, unique=True, db_index=True,
        help_text="Identifies a location: stop/platform, station, "
                  "entrance/exit, generic node or boarding area"
    )
    station = models.ForeignKey(
        Station, on_delete=models.CASCADE,
        blank=True, null=True, related_name='stops'
    )
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE,
        blank=True, null=True, related_name='stops',
        help_text="Ruta principal (solo METRO CDMX)"
    )
    stop_code = models.CharField(
        max_length=50, blank=True, null=True,
        verbose_name="Código",
        help_text="Short text or number that identifies the location "
                  "for riders"
    )
    stop_name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="Nombre"
    )
    stop_desc = models.TextField(
        blank=True, null=True,
        verbose_name="Descripción",
    )

    stop_lat = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name="Latitud",
    )
    stop_lon = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True, verbose_name="Longitud",
    )
    zone_id = models.CharField(
        max_length=255,
        blank=True, null=True,
        help_text="Identifies the fare zone for a stop"
    )
    location_type = models.IntegerField(
        choices=LOCATION_TYPE_CHOICES, default=0,
        blank=True, null=True, help_text="Location type"
    )

    # parent_station = models.ForeignKey(
    #     'self', on_delete=models.CASCADE, blank=True, null=True,
    #     related_name='child_stops',
    #     help_text="Defines hierarchy between different locations"
    # )
    wheelchair_boarding = models.IntegerField(
        choices=WHEELCHAIR_BOARDING_CHOICES,
        default=0,
        blank=True, null=True,
        help_text="Indicates whether wheelchair boardings are possible"
    )

    # stop_access = models.IntegerField(
    #     choices=STOP_ACCESS_CHOICES,
    #     blank=True, null=True,
    #     help_text="Indicates how the stop is accessed for a particular station"
    # )

    class Meta:
        verbose_name = 'Stop'
        verbose_name_plural = 'Stops'
        # indexes = [
        #     models.Index(fields=['location_type']),
        #     models.Index(fields=['parent_station']),
        # ]

    def __str__(self):
        return f"{self.stop_id} - {self.stop_name or 'Unnamed'}"


class StopTime(models.Model):
    """
    Modelo basado en stop_times.txt del estándar GTFS.
    Representa los horarios en que un vehículo llega y parte de las paradas
    individuales para cada viaje.
    """

    TIMEPOINT_CHOICES = [
        (0, 'Times are considered approximate'),
        (1, 'Times are considered exact'),
    ]

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='stop_times',
        help_text="Identifies a trip"
    )

    arrival_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Hora de llegada",
        help_text="Arrival time at the stop for a specific trip (format: HH:MM:SS)"
    )

    departure_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Hora de salida",
        help_text="Departure time from the stop for a specific trip (format: HH:MM:SS)"
    )

    stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='stop_times',
        help_text="Identifies the serviced stop"
    )

    timepoint = models.IntegerField(
        choices=TIMEPOINT_CHOICES,
        default=1,
        blank=True,
        null=True,
        help_text="Indicates if times are strictly adhered to or approximate"
    )

    stop_sequence = models.PositiveIntegerField(
        help_text="Order of stops for a particular trip"
    )

    class Meta:
        verbose_name = 'Stop Time'
        verbose_name_plural = 'Stop Times'
        unique_together = [['trip', 'stop_sequence']]
        indexes = [
            models.Index(fields=['trip', 'stop_sequence']),
            models.Index(fields=['stop']),
            models.Index(fields=['arrival_time']),
            models.Index(fields=['departure_time']),
        ]
        ordering = ['trip', 'stop_sequence']

    def __str__(self):
        stop_name = self.stop.stop_name if self.stop else 'Unknown stop'
        return f"{self.trip.trip_id} - {stop_name} (seq: {self.stop_sequence})"


