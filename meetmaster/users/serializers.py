from django.contrib.auth import get_user_model
from rest_framework import serializers

CustomUser = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "profile_image"]


class DetailedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "email", "profile_image", "date_joined", "is_superuser"]


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ["username", "password", "email", "first_name", "last_name", "profile_image"]

    # def create(self, validated_data):
    #     user = CustomUser.objects.create_user(
    #         username=validated_data["username"],
    #         email=validated_data["email"],
    #         password=validated_data["password"],
    #         first_name=validated_data.get("first_name"),
    #         last_name=validated_data.get("last_name"),
    #         profile_image=validated_data.get("profile_image", None),
    #     )
    #     return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "profile_image", "email"]
