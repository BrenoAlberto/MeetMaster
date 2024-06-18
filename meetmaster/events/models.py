from datetime import datetime

from django.contrib.auth.models import User
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
    status = models.CharField(max_length=2, choices=Status.choices, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, related_name="attendees", blank=True)

    class Meta:
        ordering = ["-date", "-time"]
        indexes = [
            models.Index(fields=["-date", "-time", "status"]),
            models.Index(fields=["created_by"]),
        ]

    def save(self, *args, **kwargs):
        current_datetime = timezone.now()
        event_datetime = timezone.make_aware(datetime.combine(self.date, self.time), timezone.get_current_timezone())

        if event_datetime > current_datetime:
            self.status = self.Status.INCOMING
        else:
            self.status = self.Status.FINISHED

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.date} {self.time})"
