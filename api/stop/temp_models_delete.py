from django.db import models


# class Route(models.Model):
#     route_id = models.CharField(max_length=255, unique=True)
#     route_short_name = models.CharField(max_length=50)
#     route_long_name = models.CharField(max_length=255)
#     route_type = models.IntegerField()
#     route_color = models.CharField(max_length=6, blank=True, null=True)
#     route_text_color = models.CharField(max_length=6, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.route_id} - {self.route_short_name}"


# route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,shape_id
# CMX0200L2,3,02300L2000_1,Cuatro Caminos,Línea 2 to Cuatro Caminos,1,SH0200L2000_1
# CMX0200L2,3,02300L2000_0,Tasqueña,Línea 2 to Tasqueña,0,SH0200L2000_0
# CMX0200L2,2,02200L2000_1,Cuatro Caminos,Línea 2 to Cuatro Caminos,1,SH0200L2000_1


# trip_id,timepoint,stop_id,stop_sequence,arrival_time,departure_time
# 02100L1000_0,0,0200L1-OBSERVATORIO,1,00:00:00,00:00:00
# 02100L1000_0,0,0200L1-TACUBAYA,2,00:02:50,00:02:50
# 02100L1000_0,0,0200L1-JUANACATLAN,3,00:05:24,00:05:24
# 02100L1000_0,0,0200L1-CHAPULTEPEC,4,00:07:36,00:07:36

