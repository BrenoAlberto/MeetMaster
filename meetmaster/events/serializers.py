from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    total_attendees = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display", read_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "time",
            "location",
            "updated",
            "status",
            "owner",
            "total_attendees",
        ]

    def get_total_attendees(self, obj):
        return obj.attendees.count()
