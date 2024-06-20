from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from events.models import Event, Notification
from events.tasks import send_notification

User = get_user_model()


class SendNotificationTaskTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")
        self.event = Event.objects.create(
            title="Event 1",
            description="Description for event 1",
            date=timezone.now().date() + timezone.timedelta(days=1),
            time=timezone.now().time(),
            location="Location 1",
            owner=self.user1,
        )
        self.event.attendees.add(self.user1, self.user2)

    @patch("events.tasks.send_mail")
    def test_send_notification(self, mock_send_mail):
        message = "This is a test notification."
        subject = "Test Subject"
        send_notification(self.event.id, message, subject)

        self.assertEqual(mock_send_mail.call_count, 2)

        mock_send_mail.assert_any_call(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user1.email],
            fail_silently=False,
        )
        mock_send_mail.assert_any_call(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user2.email],
            fail_silently=False,
        )

        self.assertTrue(Notification.objects.filter(event=self.event, message=message).exists())

    @patch("events.tasks.send_mail")
    def test_send_notification_no_attendees(self, mock_send_mail):
        self.event.attendees.clear()
        message = "This is a test notification."
        subject = "Test Subject"
        send_notification(self.event.id, message, subject)

        self.assertEqual(mock_send_mail.call_count, 0)

        self.assertTrue(Notification.objects.filter(event=self.event, message=message).exists())
