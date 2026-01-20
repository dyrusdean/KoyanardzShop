from django.conf import settings
import os
import requests
import logging

logger = logging.getLogger(__name__)


def send_email(subject, text='', html=None, from_email=None, recipient_list=None):
    """Send email using MailerSend API when configured, otherwise fall back to Django send_mail.

    Raises an exception on failure so callers can catch and log appropriately.
    """
    if not recipient_list:
        raise ValueError("recipient_list must be provided and non-empty")

    chosen_from = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

    api_key = os.getenv('MAILERSEND_API_KEY', '').strip()
    if api_key:
        payload = {
            'from': {'email': chosen_from or '', 'name': 'Koya Nardz Shop'},
            'to': [{'email': r} for r in recipient_list],
            'subject': subject,
            'text': text,
        }
        if html:
            payload['html'] = html

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        try:
            resp = requests.post('https://api.mailersend.com/v1/email', json=payload, headers=headers, timeout=10)
            if resp.status_code not in (200, 201, 202):
                logger.error("MailerSend API returned %s: %s", resp.status_code, resp.text)
                raise RuntimeError(f"MailerSend API returned {resp.status_code}: {resp.text}")
            logger.info("MailerSend: email queued/sent to %s", recipient_list)
            return True
        except Exception:
            logger.exception("Failed to send via MailerSend to %s", recipient_list)
            raise

    # Fallback to Django's send_mail
    from django.core.mail import send_mail
    try:
        send_mail(subject, text, chosen_from, recipient_list, fail_silently=False, html_message=html)
        logger.info("Django email backend sent to %s", recipient_list)
        return True
    except Exception:
        logger.exception("Failed to send email via Django backend to %s", recipient_list)
        raise
