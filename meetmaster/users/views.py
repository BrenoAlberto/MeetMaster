from common.permissions import IsSuperUser, IsSuperUserOrSelf
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser
from .serializers import DetailedUserSerializer, PublicUserSerializer, UserCreateSerializer, UserUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        description="Only accessible by superusers.",
        responses={
            200: PublicUserSerializer(many=True),
            403: None,
        },
    ),
    retrieve=extend_schema(
        summary="Retrieve a user",
        description="Superusers can see detailed user info, others see public info.",
        responses={
            200: DetailedUserSerializer,
            403: None,
        },
    ),
    create=extend_schema(
        summary="Create a new user",
        description="Allows creation of a new user.",
        request=UserCreateSerializer,
        responses={
            201: DetailedUserSerializer,
            400: None,
        },
    ),
    update=extend_schema(
        summary="Update a user",
        description="Superusers can update detailed user info, others can update their own info.",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            403: None,
        },
    ),
    partial_update=extend_schema(
        summary="Partially update a user",
        description="Superusers can partially update detailed user info, others can partially update their own info.",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            403: None,
        },
    ),
    destroy=extend_schema(
        summary="Delete a user",
        description="Superusers can delete any user, others can only delete their own account.",
        responses={
            204: None,
            403: None,
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return DetailedUserSerializer if self.request.user.is_superuser else PublicUserSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return PublicUserSerializer

    def get_permissions(self):
        permission_classes = {
            "list": [IsAuthenticated, IsSuperUser],
            "retrieve": [IsAuthenticated],
            "create": [AllowAny],
            "update": [IsAuthenticated, IsSuperUserOrSelf],
            "partial_update": [IsAuthenticated, IsSuperUserOrSelf],
            "destroy": [IsAuthenticated, IsSuperUserOrSelf],
        }
        self.permission_classes = permission_classes.get(self.action, [AllowAny])
        return super().get_permissions()
