from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from events.models import Event
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_users():
    custom_user = get_user_model()
    user1 = custom_user.objects.create_user(username="user1", email="email1@mail.com", password="password")
    user2 = custom_user.objects.create_user(username="user2", email="email2@mail.com", password="password")
    return {"user1": user1, "user2": user2}


@pytest.fixture
def create_event(create_users):
    return Event.objects.create(
        title="Event 1",
        description="Description for event 1",
        date=timezone.now() + timezone.timedelta(days=1),
        location="Location 1",
        owner=create_users["user1"],
    )


@pytest.fixture
def mock_send_notification():
    with patch("events.tasks.send_notification.delay") as mock:
        yield mock


def login(api_client, username, password):
    api_client.login(username=username, password=password)


def post_event(api_client, data):
    url = reverse("event-list")
    return api_client.post(url, data)


def put_event(api_client, event_id, data):
    url = reverse("event-detail", kwargs={"pk": event_id})
    return api_client.put(url, data)


def patch_event(api_client, event_id, data):
    url = reverse("event-detail", kwargs={"pk": event_id})
    return api_client.patch(url, data)


def get_event(api_client, event_id):
    url = reverse("event-detail", kwargs={"pk": event_id})
    return api_client.get(url)


@pytest.mark.django_db
class TestEventViewSet:

    def test_auth_user_can_create_event(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {
            "title": "New Event",
            "description": "Description for new event",
            "date": timezone.now() + timezone.timedelta(days=1),
            "location": "Location 1",
        }
        response = post_event(api_client, data)
        assert response.status_code == status.HTTP_201_CREATED
        new_event = Event.objects.get(id=response.data["id"])
        assert new_event.owner == user1
        assert new_event.status == Event.Status.INCOMING

    def test_auth_user_cannot_create_event_with_past_date(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {
            "title": "Past Event",
            "description": "This event is in the past",
            "date": timezone.now() - timezone.timedelta(days=1),
            "location": "Location 1",
        }
        response = post_event(api_client, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Events cannot be created in the past." in response.data["date"]

    def test_auth_user_cannot_create_event_with_status_canceled(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {
            "title": "Canceled Event",
            "description": "This event is canceled",
            "date": timezone.now() + timezone.timedelta(days=1),
            "location": "Location 1",
            "status": Event.Status.CANCELED,
        }
        response = post_event(api_client, data)
        assert response.status_code == status.HTTP_201_CREATED
        new_event = Event.objects.get(id=response.data["id"])
        assert new_event.status == Event.Status.INCOMING

    def test_auth_user_can_update_event(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        updated_date = create_event.date + timezone.timedelta(days=1)
        data = {
            "title": "Updated Event",
            "description": "Updated description",
            "date": updated_date,
            "location": "Updated location",
        }
        response = put_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_200_OK
        create_event.refresh_from_db()
        assert create_event.title == "Updated Event"
        assert create_event.description == "Updated description"
        assert create_event.location == "Updated location"
        assert create_event.date == updated_date

    def test_auth_user_cannot_update_event_with_past_date(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {
            "title": create_event.title,
            "description": create_event.description,
            "date": date.today() - timezone.timedelta(days=1),
            "location": create_event.location,
        }
        response = put_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_auth_user_cannot_patch_event_with_past_date(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {"date": date.today() - timezone.timedelta(days=1)}
        response = patch_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Events cannot be created in the past." in response.data["date"]

    def test_auth_user_can_only_patch_status_to_cancel(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {"status": Event.Status.CANCELED}
        response = patch_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_200_OK
        create_event.refresh_from_db()
        assert create_event.status == Event.Status.CANCELED

        data = {"status": Event.Status.INCOMING}
        response = patch_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Status can only be updated to 'Canceled'." in response.data["status"]

    def test_not_notified_twice_on_double_cancel(self, api_client, create_users, create_event, mock_send_notification):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {"status": Event.Status.CANCELED}
        patch_event(api_client, create_event.pk, data)
        create_event.refresh_from_db()

        mock_send_notification.assert_called_once()
        mock_send_notification.reset_mock()

        patch_event(api_client, create_event.pk, data)
        create_event.refresh_from_db()

        mock_send_notification.assert_not_called()

    def test_auth_user_can_only_update_status_to_cancel(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        data = {
            "title": create_event.title,
            "description": create_event.description,
            "date": create_event.date,
            "location": create_event.location,
            "status": Event.Status.CANCELED,
        }
        response = put_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_200_OK
        create_event.refresh_from_db()
        assert create_event.status == Event.Status.CANCELED

        data["status"] = Event.Status.INCOMING
        response = put_event(api_client, create_event.pk, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Status can only be updated to 'Canceled'." in response.data["status"]

    def test_any_user_can_list_events(self, api_client):
        response = api_client.get(reverse("event-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_can_retrieve_event_details(self, api_client, create_event):
        response = get_event(api_client, create_event.pk)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == create_event.title

    def test_auth_user_can_attende_to_event(self, api_client, create_users, create_event):
        user2 = create_users["user2"]
        login(api_client, user2.username, "password")
        response = api_client.post(reverse("event-attende", kwargs={"pk": create_event.pk}))
        assert response.status_code == status.HTTP_200_OK
        create_event.refresh_from_db()
        assert user2 in create_event.attendees.all()

    def test_unauth_user_cannot_attende(self, api_client, create_event):
        response = api_client.post(reverse("event-attende", kwargs={"pk": create_event.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_user_can_remove_attendee_from_event(self, api_client, create_users, create_event):
        user2 = create_users["user2"]
        create_event.attendees.add(user2)
        login(api_client, user2.username, "password")
        response = api_client.post(reverse("event-remove-attendee", kwargs={"pk": create_event.pk}))
        assert response.status_code == status.HTTP_200_OK
        create_event.refresh_from_db()
        assert user2 not in create_event.attendees.all()

    def test_event_owner_can_view_attendees(self, api_client, create_users, create_event):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        response = api_client.get(reverse("event-attendees", kwargs={"pk": create_event.pk}))
        assert response.status_code == status.HTTP_200_OK

    def test_non_owner_cannot_view_attendees(self, api_client, create_users, create_event):
        user2 = create_users["user2"]
        login(api_client, user2.username, "password")
        response = api_client.get(reverse("event-attendees", kwargs={"pk": create_event.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN
