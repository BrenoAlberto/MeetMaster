from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from events.models import Event


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.custom_user = get_user_model()
        cls.user = cls.custom_user.objects.create_user(username="testuser", password="testpassword")

    def create_event(self, event_date, event_time):
        return Event.objects.create(
            title="Test Event",
            description="This is a test event",
            date=event_date,
            time=event_time,
            location="Test Location",
            owner=self.user,
        )

    def test_event_status_incoming(self):
        future_date = date.today() + timedelta(days=1)
        event = self.create_event(future_date, time(10, 30))
        event.save()
        self.assertEqual(event.status, Event.Status.INCOMING)

    def test_cancel_event(self):
        future_date = date.today() + timedelta(days=1)
        event = self.create_event(future_date, time(10, 30))
        event.save()
        event.cancel()
        self.assertEqual(event.status, Event.Status.CANCELED)
