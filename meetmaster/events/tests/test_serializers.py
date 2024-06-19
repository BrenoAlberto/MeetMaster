from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from events.models import Event
from events.serializers import EventSerializer


class EventSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.custom_user = get_user_model()
        cls.user = cls.custom_user.objects.create_user(username="testuser", password="testpassword")
        cls.event = Event.objects.create(
            title="Test Event",
            description="This is a test event",
            date=date.today() + timezone.timedelta(days=1),
            time=time(10, 30),
            location="Test Location",
            created_by=cls.user,
        )

    def test_total_attendees(self):
        serializer = EventSerializer(instance=self.event)
        self.assertEqual(serializer.data["total_attendees"], self.event.attendees.count())

    def test_status(self):
        serializer = EventSerializer(instance=self.event)
        self.assertEqual(serializer.data["status"], self.event.get_status_display())
