from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Event(models.Model):
    class Status(models.TextChoices):
        INCOMING = "IN", "Incoming"
        FINISHED = "FI", "Finished"
        CANCELED = "CA", "Canceled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.INCOMING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_events", on_delete=models.CASCADE)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="attended_events", blank=True)

    class Meta:
        ordering = ["-date", "-time"]
        indexes = [
            models.Index(fields=["-date", "-time", "status"]),
            models.Index(fields=["created_by"]),
        ]

    def clean(self):
        current_datetime = timezone.now()
        event_datetime = timezone.make_aware(datetime.combine(self.date, self.time), timezone.get_current_timezone())

        if event_datetime < current_datetime:
            raise ValidationError("Events cannot be created in the past.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self):
        if self.status == self.Status.INCOMING:
            self.status = self.Status.CANCELED
            self.save(update_fields=["status"])

    def __str__(self):
        return f"{self.title} ({self.date} {self.time})"


class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.event.title} at {self.created_at}"
