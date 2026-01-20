from django.core.management.base import BaseCommand
from django.conf import settings
import os
import logging
import requests

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send a test email using MailerSend API (or Django send_mail fallback). Use --send to actually transmit.'

    def add_arguments(self, parser):
        parser.add_argument('--to', dest='to_email', required=True, help='Recipient email address for the test')
        parser.add_argument('--subject', dest='subject', default='Test email from Koya Nardz Shop', help='Email subject')
        parser.add_argument('--body', dest='body', default='This is a test email sent from the application.', help='Email body')
        parser.add_argument('--send', action='store_true', help='Actually send the email (omit to dry-run)')

    def handle(self, *args, **options):
        to_email = options['to_email']
        subject = options['subject']
        body = options['body']
        do_send = options['send']

        chosen_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
        self.stdout.write(f"Chosen from: {chosen_from}")

        if not chosen_from or '@' not in chosen_from:
            self.stdout.write(self.style.WARNING('Warning: chosen FROM address looks invalid. Set DEFAULT_FROM_EMAIL in env.'))

        payload = {
            'from': {'email': chosen_from or '', 'name': 'Koya Nardz Shop'},
            'to': [{'email': to_email}],
            'subject': subject,
            'text': body,
        }

        self.stdout.write('Constructed MailerSend payload:')
        self.stdout.write(str(payload))

        if not do_send:
            self.stdout.write(self.style.NOTICE('Dry-run mode: no network request performed. Add --send to actually transmit the message.'))
            return

        api_key = os.getenv('MAILERSEND_API_KEY', '').strip()
        if api_key:
            url = 'https://api.mailersend.com/v1/email'
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code not in (200, 201, 202):
                    self.stderr.write(self.style.ERROR(f'MailerSend API returned {resp.status_code}: {resp.text}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'MailerSend queued/sent to {to_email}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error sending via MailerSend: {e}'))
        else:
            # Fallback to Django send_mail
            try:
                from django.core.mail import send_mail
                send_mail(subject, body, chosen_from, [to_email], fail_silently=False)
                self.stdout.write(self.style.SUCCESS(f'Django email backend sent to {to_email}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to send via Django email backend: {e}'))
