from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_registration_confirmation(registration_id):
    from events.models import Registration
    try:
        registration = Registration.objects.select_related('user', 'event').get(id=registration_id)
        user = registration.user
        event = registration.event

        subject = f"Registration Confirmed: {event.title}"
        context = {
            'user': user,
            'event': event,
            'registration': registration,
        }

        html_content = render_to_string('emails/registration_confirmation.html', context)
        text_content = f"Hi {user.username}, you are registered for {event.title} on {event.start_date}."

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Registration.DoesNotExist:
        pass


@shared_task
def send_event_reminders():
    from events.models import Registration
    from django.contrib.auth import get_user_model

    tomorrow = timezone.now().date() + timedelta(days=1)

    registrations = Registration.objects.filter(
        status='confirmed',
        event__start_date__date=tomorrow
    ).select_related('user', 'event')

    for registration in registrations:
        user = registration.user
        event = registration.event

        subject = f"Reminder: {event.title} is tomorrow!"
        text_content = (
            f"Hi {user.username},\n\n"
            f"This is a reminder that '{event.title}' is happening tomorrow "
            f"at {event.start_date.strftime('%H:%M')}.\n\n"
            f"Location: {event.location or 'Online'}\n\n"
            f"See you there!"
        )

        from django.core.mail import send_mail
        send_mail(
            subject=subject,
            message=text_content,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )