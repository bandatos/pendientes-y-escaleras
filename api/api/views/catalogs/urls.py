from django.urls import include, path
from rest_framework import routers

from api.views.catalogs.all import CatalogsView

router = routers.DefaultRouter()

# router.register(r'source', SourceViewSet, basename='catalog_source')
# router.register(r'status_control', StatusControlViewSet, basename='catalog_status_control')


urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]