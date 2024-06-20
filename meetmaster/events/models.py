from django.conf import settings
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        INCOMING = "IN", "Incoming"
        FINISHED = "FI", "Finished"
        CANCELED = "CA", "Canceled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.INCOMING)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_events", on_delete=models.CASCADE)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="attended_events", blank=True)

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["-date", "status"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.date})"


class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.event.title} at {self.created_at}"
