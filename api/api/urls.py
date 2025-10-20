from django.urls import include, path

from api.views.auth.login_views import UserLoginAPIView

# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import health_check

router = DefaultRouter()


# router.register(r'note', NoteViewSet, basename='note')
# router.register(r'note_file', NoteFileViewSet, basename='note file')
# router.register(r'article', ArticleViewSet, basename='article')


urlpatterns = [
    # path('login/', obtain_auth_token, name='api-login'),
    path('health/', health_check, name='health_check'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.views.catalogs.urls')),
    # path('space_time/', include('api.views.space_time.urls')),
    path('', include(router.urls)),
]
