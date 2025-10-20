from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from profile_auth.models import User


class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'})
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())])
    checkCondiction = serializers.BooleanField(
        required=False)
    key = serializers.CharField(required=False)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(
        required=True, style={'input_type': 'password'})
    key = serializers.CharField(required=False)


class UserDataSerializer(serializers.ModelSerializer):
    fullname = serializers.ReadOnlyField(source="full_name")
    token = serializers.ReadOnlyField(source="auth_token.key")

    class Meta(object):
        model = User
        fields = [
            "id", 'email', 'username', "first_name", "last_name",
            "token", "fullname", "full_editor", "is_staff",
            "is_superuser", "is_full_editor"]


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "is_superuser",
            "first_name",
            "last_name",
            "full_editor",
            "full_name",
        ]
