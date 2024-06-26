from common.utils import model_data_prop_was_changed
from django.utils import timezone
from rest_framework import serializers

from .models import Event
from .tasks import send_notification_to_all_attendees, send_notification_to_attendee


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
            send_notification_to_all_attendees.delay(instance.id, message, subject)

    def get_total_attendees(self, obj):
        return obj.attendees.count()


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = []

    def add_attendee(self, instance):
        user = self.context["request"].user
        instance.attendees.add(user)
        instance.save()
        self._notify_add(instance, user)
        return instance

    def remove_attendee(self, instance):
        user = self.context["request"].user
        instance.attendees.remove(user)
        instance.save()
        self._notify_remove(instance, user)
        return instance

    def _notify_add(self, event, user):
        message = f"You have been added as an attendee to the event '{event.title}'."
        subject = "Event Attendee Notification"
        send_notification_to_attendee.delay(user.id, event.id, message, subject)

    def _notify_remove(self, event, user):
        message = f"You have been removed as an attendee from the event '{event.title}'."
        subject = "Event Attendee Removal Notification"
        send_notification_to_attendee.delay(user.id, event.id, message, subject)


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
        send_notification_to_all_attendees.delay(event.id, message, subject)
