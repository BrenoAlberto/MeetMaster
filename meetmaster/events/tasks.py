from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from events.models import Event, Notification


@shared_task
def send_notification(event_id, message, subject):
    event = Event.objects.get(id=event_id)
    attendees = event.attendees.all()
    from_email = settings.DEFAULT_FROM_EMAIL

    for attendee in attendees:
        send_mail(
            subject,
            message,
            from_email,
            [attendee.email],
            fail_silently=False,
        )
    Notification.objects.create(event=event, message=message)
