from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if request.user == event.created_by:
            attendees = event.attendees.all()
            attendee_data = [{"id": attendee.id, "username": attendee.username} for attendee in attendees]
            return Response(attendee_data)
        else:
            return Response({"detail": "Not authorized to view attendee details"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["post"])
    def add_attendee(self, request, pk=None):
        event = self.get_object()
        attendee = request.user
        event.attendees.add(attendee)
        return Response({"status": "attendee added"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def remove_attendee(self, request, pk=None):
        event = self.get_object()
        attendee = request.user
        event.attendees.remove(attendee)
        return Response({"status": "attendee removed"}, status=status.HTTP_200_OK)
