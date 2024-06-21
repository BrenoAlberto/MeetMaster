from common.permissions import IsAttendee, IsOwner
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventAttendeeSerializer, EventCancelSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()

    def get_serializer_class(self):
        if self.action == "cancel":
            return EventCancelSerializer
        elif self.action in ["attende", "remove_attendee"]:
            return EventAttendeeSerializer
        return EventSerializer

    def get_permissions(self):
        permission_classes = {
            "list": [permissions.IsAuthenticatedOrReadOnly],
            "retrieve": [permissions.IsAuthenticatedOrReadOnly],
            "create": [permissions.IsAuthenticated],
            "update": [permissions.IsAuthenticated, IsOwner],
            "partial_update": [permissions.IsAuthenticated, IsOwner],
            "destroy": [permissions.IsAuthenticated, IsOwner],
            "cancel": [permissions.IsAuthenticated, IsOwner],
            "attendees": [permissions.IsAuthenticated, IsOwner | IsAttendee],
            "attende": [permissions.IsAuthenticated],
            "remove_attendee": [permissions.IsAuthenticated],
        }
        self.permission_classes = permission_classes.get(self.action, [permissions.AllowAny])
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if request.user == event.owner or request.user in event.attendees.all():
            attendees = event.attendees.all()
            attendee_data = [{"id": attendee.id, "username": attendee.username} for attendee in attendees]
            return Response(attendee_data, status=status.HTTP_200_OK)
        return Response({"detail": "Not authorized to view attendee details"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["post"])
    def attende(self, request, pk=None):
        event = self.get_object()
        if request.user in event.attendees.all():
            return Response({"detail": "User is already an attendee."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.add_attendee(event)
        return Response({"status": "attendee added"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def remove_attendee(self, request, pk=None):
        event = self.get_object()
        if request.user not in event.attendees.all():
            return Response({"detail": "User is not an attendee."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.remove_attendee(event)
        return Response({"status": "attendee removed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        event = self.get_object()
        if event.status == Event.Status.CANCELED:
            return Response({"detail": "Event is already canceled."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "event canceled"}, status=status.HTTP_200_OK)
