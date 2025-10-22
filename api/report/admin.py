from django.contrib import admin
from .models import StairReport, EvidenceImage


class EvidenceImageAdmin(admin.ModelAdmin):
    list_display = ('stair_report', 'image')
    search_fields = ('stair_report__id',)


class EvidenceImageInline(admin.TabularInline):
    model = EvidenceImage
    extra = 0


class StairReportAdmin(admin.ModelAdmin):
    list_display = (
        'stair', 'user', 'status_maintenance', 'is_working', 'date_reported')
    search_fields = ('user__email', 'status_maintenance')
    list_filter = (
        'status_maintenance', 'is_working', 'date_reported', 'stair__stop__route')
    inlines = [EvidenceImageInline]


admin.site.register(StairReport, StairReportAdmin)
admin.site.register(EvidenceImage, EvidenceImageAdmin)
