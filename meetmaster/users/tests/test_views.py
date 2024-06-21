from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_users():
    custom_user = get_user_model()
    admin_user = custom_user.objects.create_superuser(
        username="admin_user", password="password", email="admin@example.com"
    )
    user1 = custom_user.objects.create_user(username="user1", password="password", email="user1@example.com")
    user2 = custom_user.objects.create_user(username="user2", password="password", email="user2@example.com")
    return {
        "custom_user": custom_user,
        "admin_user": admin_user,
        "user1": user1,
        "user2": user2,
    }


def login(api_client, username, password):
    api_client.login(username=username, password=password)


def create_test_image_file():
    file = BytesIO()
    image = Image.new("RGB", (100, 100), color=(73, 109, 137))
    image.save(file, "jpeg")
    file.seek(0)
    return SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")


@pytest.mark.django_db
class TestUserViewSet:

    def test_superuser_can_list_users(self, api_client, create_users):
        admin = create_users["admin_user"]
        login(api_client, admin.username, "password")
        url = reverse("customuser-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results")) == 3

    def test_non_superuser_cannot_list_users(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, user1.username, "password")
        url = reverse("customuser-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "username, password, expected_fields",
        [
            ("admin_user", "password", ["email", "is_superuser", "date_joined"]),
            ("user2", "password", []),
        ],
    )
    def test_user_retrieve_fields_based_on_permissions(
        self, api_client, create_users, username, password, expected_fields
    ):
        user1 = create_users["user1"]
        login(api_client, username, password)
        url = reverse("customuser-detail", kwargs={"pk": user1.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for field in ["email", "password", "is_superuser", "date_joined"]:
            if field in expected_fields:
                assert field in response.data
            else:
                assert field not in response.data

    def test_user_can_retrieve_own_profile(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, "user1", "password")
        url = reverse("customuser-detail", kwargs={"pk": user1.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "username" in response.data

    def test_user_can_update_own_profile(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, "user1", "password")
        url = reverse("customuser-detail", kwargs={"pk": user1.pk})
        data = {"first_name": "UpdatedName"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        user1.refresh_from_db()
        assert user1.first_name == "UpdatedName"

    def test_user_cannot_update_other_user_profile(self, api_client, create_users):
        user2 = create_users["user2"]
        login(api_client, "user1", "password")
        url = reverse("customuser-detail", kwargs={"pk": user2.pk})
        data = {"first_name": "UpdatedName"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_update_sensitive_fields(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, "user1", "password")
        url = reverse("customuser-detail", kwargs={"pk": user1.pk})
        data = {"is_superuser": True}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        user1.refresh_from_db()
        assert not user1.is_superuser

    @pytest.mark.parametrize(
        "username, password, pk_key, expected_status, expected_count",
        [
            ("user1", "password", "user1", status.HTTP_204_NO_CONTENT, 2),
            ("admin_user", "password", "user1", status.HTTP_204_NO_CONTENT, 2),
            ("user1", "password", "user2", status.HTTP_403_FORBIDDEN, 3),
        ],
    )
    def test_user_deletion_scenarios(
        self, api_client, create_users, username, password, pk_key, expected_status, expected_count
    ):
        custom_user = create_users["custom_user"]
        pk = create_users[pk_key].pk
        login(api_client, username, password)
        url = reverse("customuser-detail", kwargs={"pk": pk})
        response = api_client.delete(url)
        assert response.status_code == expected_status
        assert custom_user.objects.count() == expected_count

    def test_user_creation(self, api_client):
        url = reverse("customuser-list")
        data = {
            "username": "new_user",
            "password": "new_password",
            "email": "new_user@example.com",
        }
        response = api_client.post(url, data)
        new_user = get_user_model().objects.get(username="new_user")
        assert response.status_code == status.HTTP_201_CREATED
        assert new_user.email == data["email"]
        assert new_user.username == data["username"]

    def test_user_profile_image_upload(self, api_client, create_users):
        user1 = create_users["user1"]
        login(api_client, "user1", "password")
        url = reverse("customuser-detail", kwargs={"pk": user1.pk})
        image = create_test_image_file()
        data = {"profile_image": image}
        response = api_client.patch(url, data, format="multipart")
        print(response.data)
        assert response.status_code == status.HTTP_200_OK

    def test_email_uniqueness(self, api_client, create_users):
        url = reverse("customuser-list")
        data = {
            "username": "duplicate_email_user",
            "password": "new_password",
            "email": create_users["user1"].email,
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    # def test_user_can_change_password(self, api_client, create_users):
    #     user1 = create_users["user1"]
    #     login(api_client, "user1", "password")
    #     url = reverse("customuser-change-password", kwargs={"pk": user1.pk})
    #     data = {"old_password": "password", "new_password": "new_password"}
    #     response = api_client.post(url, data)
    #     assert response.status_code == status.HTTP_200_OK
    #     user1.refresh_from_db()
    #     assert user1.check_password("new_password")
