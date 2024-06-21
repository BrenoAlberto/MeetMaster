from common.permissions import IsAttendee, IsOwner
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import CreateEventSerializer, EventSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all events",
        description="Retrieve a list of all events.",
        responses={200: EventSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve an event",
        description="Retrieve detailed information about a specific event.",
        responses={200: EventSerializer},
    ),
    create=extend_schema(
        summary="Create a new event",
        description="Create a new event with the specified details.",
        request=EventSerializer,
        responses={201: EventSerializer},
    ),
    update=extend_schema(
        summary="Update an event",
        description="Update details of an existing event.",
        request=EventSerializer,
        responses={200: EventSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update an event",
        description="Partially update details of an existing event.",
        request=EventSerializer,
        responses={200: EventSerializer},
    ),
    destroy=extend_schema(summary="Delete an event", description="Delete an existing event.", responses={204: None}),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateEventSerializer
        return EventSerializer

    def get_permissions(self):
        permission_classes = {
            "list": [permissions.IsAuthenticatedOrReadOnly],
            "retrieve": [permissions.IsAuthenticatedOrReadOnly],
            "create": [permissions.IsAuthenticated],
            "update": [permissions.IsAuthenticated, IsOwner],
            "partial_update": [permissions.IsAuthenticated, IsOwner],
            "destroy": [permissions.IsAuthenticated, IsOwner],
            "change_date": [permissions.IsAuthenticated, IsOwner],
            "cancel": [permissions.IsAuthenticated, IsOwner],
            "attendees": [permissions.IsAuthenticated, IsOwner | IsAttendee],
            "attende": [permissions.IsAuthenticated],
            "remove_attendee": [permissions.IsAuthenticated],
        }
        self.permission_classes = permission_classes.get(self.action, [permissions.AllowAny])
        return super().get_permissions()

    @extend_schema(
        summary="List event attendees",
        description="List all attendees for an event.",
        responses={
            200: OpenApiResponse(description="List of attendees"),
            403: OpenApiResponse(description="Not authorized to view attendee details"),
        },
    )
    @action(detail=True, methods=["get"])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if request.user == event.owner or request.user in event.attendees.all():
            attendees = event.attendees.all()
            attendee_data = [{"id": attendee.id, "username": attendee.username} for attendee in attendees]
            return Response(attendee_data)
        else:
            return Response({"detail": "Not authorized to view attendee details"}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Add the current user as an attendee to the event.",
        responses={200: OpenApiResponse(description="Attendee added")},
    )
    @action(detail=True, methods=["post"])
    def attende(self, request, pk=None):
        event = self.get_object()
        event.attendees.add(request.user)
        event.save()
        return Response({"status": "attendee added"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Remove an attendee from an event",
        description="Remove the current user from the event's attendee list.",
        responses={200: OpenApiResponse(description="Attendee removed")},
    )
    @action(detail=True, methods=["post"])
    def remove_attendee(self, request, pk=None):
        event = self.get_object()
        event.attendees.remove(request.user)
        event.save()
        return Response({"status": "attendee removed"}, status=status.HTTP_200_OK)
