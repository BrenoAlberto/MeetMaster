from common.utils import model_data_prop_was_changed
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers

from .models import Event
from .tasks import send_notification


class EventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    total_attendees = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Event.Status.choices, read_only=True, source="get_status_display")
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["created", "updated", "status", "total_attendees"]

    def update(self, instance, validated_data):
        status_changed = model_data_prop_was_changed(instance, validated_data, "status")
        date_changed = model_data_prop_was_changed(instance, validated_data, "date")
        response = super().update(instance, validated_data)
        self._notify(status_changed, date_changed, instance)
        return response

    def validate_status(self, value):
        if value != Event.Status.CANCELED:
            raise serializers.ValidationError("Status can only be updated to 'Canceled'.")
        return value

    def validate_date(self, value):
        current_datetime = timezone.now()
        if value < current_datetime:
            raise serializers.ValidationError("Events cannot be created in the past.")
        return value

    def _notify(self, status_changed, date_changed, instance):
        if status_changed:
            message = f"The event '{instance.title}' has been canceled."
            subject = "Event Cancellation Notification"
            print("Sending notification")
            send_notification.delay(instance.id, message, subject)
        if date_changed:
            message = f"The date for the event '{instance.title}' has been changed to {instance.date}."
            subject = "Event Date Change Notification"
            send_notification.delay(instance.id, message, subject)

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_attendees(self, obj):
        return obj.attendees.count()


class CreateEventSerializer(EventSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "description", "date", "location", "status", "owner"]
