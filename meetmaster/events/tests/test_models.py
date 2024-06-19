from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from events.models import Event


class EventModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpassword")

    def create_event(self, event_date, event_time):
        return Event.objects.create(
            title="Test Event",
            description="This is a test event",
            date=event_date,
            time=event_time,
            location="Test Location",
            created_by=self.user,
        )

    def test_event_status_incoming(self):
        future_date = date.today() + timedelta(days=1)
        event = self.create_event(future_date, time(10, 30))
        event.save()
        self.assertEqual(event.status, Event.Status.INCOMING)

    def test_event_status_finished(self):
        past_date = date.today() - timedelta(days=1)
        event = self.create_event(past_date, time(10, 30))
        event.save()
        self.assertEqual(event.status, Event.Status.FINISHED)

    def test_event_status_transition(self):
        event = self.create_event(date.today(), time(10, 30))

        event.date = date.today() + timedelta(days=1)
        event.save()
        self.assertEqual(event.status, Event.Status.INCOMING)

        event.date = date.today() - timedelta(days=1)
        event.save()
        self.assertEqual(event.status, Event.Status.FINISHED)
