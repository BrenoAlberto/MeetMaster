from common.utils import model_data_prop_was_changed
from django.utils import timezone
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
        exclude = ["attendees"]
        read_only_fields = ["created", "updated", "status", "total_attendees"]

    def update(self, instance, validated_data):
        date_changed = model_data_prop_was_changed(instance, validated_data, "date")
        response = super().update(instance, validated_data)
        self._notify(date_changed, instance)
        return response

    def validate_date(self, value):
        current_datetime = timezone.now()
        if value < current_datetime:
            raise serializers.ValidationError("Events cannot be created in the past.")
        return value

    def _notify(self, date_changed, instance):
        if date_changed:
            message = f"The date for the event '{instance.title}' has been changed to {instance.date}."
            subject = "Event Date Change Notification"
            send_notification.delay(instance.id, message, subject)

    def get_total_attendees(self, obj):
        return obj.attendees.count()


class EventCancelSerializer(EventSerializer):
    class Meta:
        model = Event
        fields = []

    def update(self, instance, validated_data):
        instance.status = Event.Status.CANCELED
        instance.save()
        self._notify(instance)
        return instance

    def _notify(self, event):
        message = f"The event '{event.title}' has been canceled."
        subject = "Event Cancellation Notification"
        send_notification.delay(event.id, message, subject)
