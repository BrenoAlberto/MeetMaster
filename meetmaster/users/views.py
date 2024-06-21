from common.permissions import IsSuperUser, IsSuperUserOrSelf
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser
from .serializers import DetailedUserSerializer, PublicUserSerializer, UserCreateSerializer, UserUpdateSerializer


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
