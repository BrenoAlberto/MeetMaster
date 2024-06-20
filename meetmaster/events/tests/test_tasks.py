from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from events.models import Event, Notification
from events.tasks import send_notification

User = get_user_model()


@pytest.fixture
def create_users():
    user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
    user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")
    return user1, user2


@pytest.fixture
def event(create_users):
    user1, user2 = create_users
    event = Event.objects.create(
        title="Event 1",
        description="Description for event 1",
        date=timezone.now() + timezone.timedelta(days=1),
        location="Location 1",
        owner=user1,
    )
    event.attendees.add(user1, user2)
    return event


@pytest.mark.django_db
@patch("events.tasks.send_mail")
def test_send_notification(mock_send_mail, event, create_users):
    user1, user2 = create_users
    message = "This is a test notification."
    subject = "Test Subject"
    send_notification(event.id, message, subject)

    assert mock_send_mail.call_count == 2

    mock_send_mail.assert_any_call(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user1.email],
        fail_silently=False,
    )
    mock_send_mail.assert_any_call(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user2.email],
        fail_silently=False,
    )

    assert Notification.objects.filter(event=event, message=message).exists()


@pytest.mark.django_db
@patch("events.tasks.send_mail")
def test_send_notification_no_attendees(mock_send_mail, event):
    event.attendees.clear()
    message = "This is a test notification."
    subject = "Test Subject"
    send_notification(event.id, message, subject)

    assert mock_send_mail.call_count == 0

    assert Notification.objects.filter(event=event, message=message).exists()
