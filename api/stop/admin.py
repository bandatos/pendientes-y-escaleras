from django.contrib import admin

# Register your models here.
from stop.models import Station


#
# class Station(models.Model):
#
#     name = models.CharField(max_length=255)
#     main_route = models.ForeignKey(
#         Route, on_delete=models.CASCADE,
#         blank=True, null=True, related_name='main_stations'
#     )
#     x_position = models.DecimalField(
#         max_digits=9, decimal_places=6,
#         blank=True, null=True, verbose_name="Posición X",
#     )
#     y_position = models.DecimalField(
#         max_digits=9, decimal_places=6,
#         blank=True, null=True, verbose_name="Posición Y",
#     )
#     end_anchor = models.BooleanField(default=False)
#     rotation = models.SmallIntegerField(blank=True, null=True)
#     viz_params = models.JSONField(default=dict, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.name} (ID: {self.id})"
#
#     class Meta:
#         verbose_name = 'Station'
#         verbose_name_plural = 'Stations'



class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_route', 'x_position', 'y_position', 'end_anchor')
    search_fields = ('name',)
    list_filter = ('main_route', 'end_anchor')


admin.site.register(Station, StationAdmin)