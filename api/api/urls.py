from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import health_check
from api.views.auth.login_views import UserLoginAPIView
from api.views.stop import StationViewSet
from api.views.report import StairReportViewSet


router = DefaultRouter()

router.register(r'station', StationViewSet, basename='station')
router.register(r'stair_report', StairReportViewSet, basename='stair_report')


urlpatterns = [
    # path('login/', obtain_auth_token, name='api-login'),
    path('health/', health_check, name='health_check'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.views.catalogs.urls')),
    # path('space_time/', include('api.views.space_time.urls')),
    path('', include(router.urls)),
]
