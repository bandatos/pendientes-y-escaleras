from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

# from api.views.catalogs.serializers import StatusControlSerializer

from profile_auth.models import User
from api.views.auth.serializers import UserProfileSerializer



class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):

        catalogs = {
            "user": UserProfileSerializer(
                User.objects.all(), many=True).data,

            # "source": SourceSerializer(
            #     Source.objects.all(), many=True).data,
            # "status_control": StatusControlSerializer(
            #     StatusControl.objects.all(), many=True).data,
        }
        return Response(catalogs)
