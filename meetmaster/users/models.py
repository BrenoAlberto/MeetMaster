from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to="media/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
