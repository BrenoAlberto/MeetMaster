from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserViewSetTests(APITestCase):

    def setUp(self):
        self.custom_user = get_user_model()
        self.admin_user = self.custom_user.objects.create_superuser(
            username="admin", password="adminpassword123", email="admin@example.com"
        )
        self.user1 = self.custom_user.objects.create_user(
            username="user1", password="password123", email="user1@example.com"
        )
        self.user2 = self.custom_user.objects.create_user(
            username="user2", password="password123", email="user2@example.com"
        )

    def test_list_users_as_superuser(self):
        self.client.login(username="admin", password="adminpassword123")
        url = reverse("customuser-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

    def test_list_users_as_non_superuser(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_as_superuser(self):
        self.client.login(username="admin", password="adminpassword123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertNotIn("password", response.data)
        self.assertIn("is_superuser", response.data)
        self.assertIn("date_joined", response.data)

    def test_retrieve_user_as_non_superuser(self):
        self.client.login(username="user2", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("email", response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("is_superuser", response.data)
        self.assertNotIn("date_joined", response.data)

    def test_retrieve_own_profile(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data)

    def test_update_user_as_self(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        data = {"first_name": "UpdatedName"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "UpdatedName")

    def test_update_user_as_other(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user2.pk})
        data = {"first_name": "UpdatedName"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_cannot_edit_sensitive_fields(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        data = {"is_superuser": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_superuser)

    def test_delete_user_as_self(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.custom_user.objects.count(), 2)

    def test_delete_user_as_superuser(self):
        self.client.login(username="admin", password="adminpassword123")
        url = reverse("customuser-detail", kwargs={"pk": self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.custom_user.objects.count(), 2)

    def test_delete_user_as_other(self):
        self.client.login(username="user1", password="password123")
        url = reverse("customuser-detail", kwargs={"pk": self.user2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
