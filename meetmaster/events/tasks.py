from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from events.models import Event, Notification

User = get_user_model()


@shared_task
def send_notification_to_all_attendees(event_id, message, subject):
    event = Event.objects.get(id=event_id)
    attendees = event.attendees.all()
    from_email = settings.DEFAULT_FROM_EMAIL

    for attendee in attendees:
        print(f"Sending notification to {attendee.email}")
        send_mail(
            subject,
            message,
            from_email,
            [attendee.email],
            fail_silently=False,
        )
    Notification.objects.create(event=event, message=message)


@shared_task
def send_notification_to_attendee(attendee_id, event_id, message, subject):
    event = Event.objects.get(id=event_id)
    attendee = User.objects.get(id=attendee_id)
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [attendee.email],
        fail_silently=False,
    )
    Notification.objects.create(event=event, message=message)


@shared_task
def update_event_statuses(batch_size=1000):
    now = timezone.now()
    while True:
        event_ids = list(
            Event.objects.filter(status=Event.Status.INCOMING, date__lt=now).values_list("id", flat=True)[:batch_size]
        )
        if not event_ids:
            break
        Event.objects.filter(id__in=event_ids).update(status=Event.Status.FINISHED)
