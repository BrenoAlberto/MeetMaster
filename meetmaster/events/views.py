from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer
from .tasks import send_notification


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def change_date(self, request, pk=None):
        event = self.get_object()
        new_date = request.data.get("date")
        new_time = request.data.get("time")

        if not new_date or not new_time:
            return Response(
                {"detail": "Both date and time fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.date = new_date
        event.time = new_time
        event.full_clean()
        event.save()

        message = f"The date for the event '{event.title}' has been changed to {new_date}."
        subject = "Event Date Change Notification"
        send_notification.delay(event.id, message, subject)

        return Response({"status": "Date changed and notification sent"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        event = self.get_object()

        if event.status == Event.Status.CANCELED:
            return Response(
                {"detail": "This event has already been canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.cancel()
        message = f"The event '{event.title}' has been canceled."
        subject = "Event Cancellation Notification"
        send_notification.delay(event.id, message, subject)

        return Response({"status": "Event canceled and notification sent"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if request.user == event.owner or request.user in event.attendees.all():
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
