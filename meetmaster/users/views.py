from common.permissions import IsSuperUser, IsSuperUserOrSelf
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .serializers import (
    ChangePasswordSerializer, DetailedUserSerializer, PublicUserSerializer, UserSerializer, UserUpdateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        elif self.action == "retrieve":
            return (
                DetailedUserSerializer
                if self.request.user.is_superuser or self.request.user == self.get_object()
                else PublicUserSerializer
            )
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        return PublicUserSerializer

    def get_permissions(self):
        permission_classes = {
            "list": [IsAuthenticated, IsSuperUser],
            "retrieve": [IsAuthenticated],
            "create": [AllowAny],
            "update": [IsAuthenticated, IsSuperUserOrSelf],
            "partial_update": [IsAuthenticated, IsSuperUserOrSelf],
            "destroy": [IsAuthenticated, IsSuperUserOrSelf],
            "change_password": [IsAuthenticated, IsSuperUserOrSelf],
        }
        self.permission_classes = permission_classes.get(self.action, [AllowAny])
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Wrong password."}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"status": "password changed"}, status=200)
