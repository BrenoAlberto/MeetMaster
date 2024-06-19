# Generated by Django 5.0.6 on 2024-06-19 15:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_notification"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="attendees",
            field=models.ManyToManyField(blank=True, related_name="attended_events", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="event",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="created_events", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="status",
            field=models.CharField(
                choices=[("IN", "Incoming"), ("FI", "Finished"), ("CA", "Canceled")], default="IN", max_length=2
            ),
        ),
    ]