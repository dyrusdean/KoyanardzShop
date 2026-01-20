from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, timedelta
from .models import Appointment

@shared_task
def send_appointment_reminders():
    target_date = date.today() + timedelta(days=3)
    appointments = Appointment.objects.filter(date=target_date)

    for appt in appointments:
        html = render_to_string('emails/appointment_reminder.html', {
            'first_name': appt.first_name,
            'reference_number': appt.reference_number,
            'date': appt.date,
            'time': appt.time,
        })

        send_mail(
            subject=f"Reminder: Your Appointment in 3 Days (Ref #{appt.reference_number})",
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[appt.email],
            html_message=html,
        )

    return f"Sent reminders for {appointments.count()} appointments"
