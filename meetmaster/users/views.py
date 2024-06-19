from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser
from .permissions import IsSuperUserOrSelf
from .serializers import DetailedUserSerializer, PublicUserSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == "list":
            if self.request.user.is_superuser:
                return CustomUser.objects.all()
            raise PermissionDenied("You do not have permission to list users.")
        return CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            if self.request.user.is_superuser:
                return DetailedUserSerializer
            return PublicUserSerializer
        elif self.action in ["update", "partial_update"]:
            if self.request.user.is_superuser:
                return DetailedUserSerializer
            return UserUpdateSerializer
        return PublicUserSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsSuperUserOrSelf]
        elif self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_update(self, serializer):
        if not self.request.user.is_superuser and serializer.instance != self.request.user:
            raise PermissionDenied("You do not have permission to edit this user.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser and instance != self.request.user:
            raise PermissionDenied("You do not have permission to delete this user.")
        instance.delete()
