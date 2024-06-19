from datetime import date, time

from django.urls import reverse
from django.utils import timezone
from events.models import Event
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser


class EventViewSetTests(APITestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username="user1", password="password123")
        self.user2 = CustomUser.objects.create_user(username="user2", password="password123")
        self.event1 = Event.objects.create(
            title="Event 1",
            description="Description for event 1",
            date=timezone.now().date(),
            time=timezone.now().time(),
            location="Location 1",
            created_by=self.user1,
        )

    def test_create_event(self):
        self.client.login(username="user1", password="password123")
        url = reverse("event-list")
        data = {
            "title": "New Event",
            "description": "Description for new event",
            "date": date.today(),
            "time": time(12, 0),
            "location": "Location 1",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_event = Event.objects.get(id=response.data["id"])
        self.assertEqual(new_event.created_by, self.user1)

    def test_list_events(self):
        response = self.client.get(reverse("event-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_details(self):
        response = self.client.get(reverse("event-detail", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.event1.title)

    def test_add_attendee(self):
        self.client.login(username="user2", password="password123")
        response = self.client.post(reverse("event-add-attendee", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event1.refresh_from_db()
        self.assertIn(self.user2, self.event1.attendees.all())

    def test_add_attendee_unauthenticated(self):
        response = self.client.post(reverse("event-add-attendee", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_attendee(self):
        self.event1.attendees.add(self.user2)
        self.client.login(username="user2", password="password123")
        response = self.client.post(reverse("event-remove-attendee", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event1.refresh_from_db()
        self.assertNotIn(self.user2, self.event1.attendees.all())

    def test_attendees_view_owner(self):
        self.client.login(username="user1", password="password123")
        response = self.client.get(reverse("event-attendees", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attendees_view_non_owner(self):
        self.client.login(username="user2", password="password123")
        response = self.client.get(reverse("event-attendees", kwargs={"pk": self.event1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
