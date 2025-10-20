from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect


admin.site.site_header = "Serpientes y Escaleras"
admin.site.site_title = "Serpientes y Escaleras"
admin.site.index_title = "Serpientes y Escaleras"


urlpatterns = [
    path('', lambda request: redirect('admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
