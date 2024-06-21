from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "profile_image")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
