import logging
import time
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger('email_notifications')


def send_email_with_retry(subject, message, recipient_list, html_message=None, max_retries=3, retry_delay=5):
    """
    Sends an email with retry logic and logging.
    If html_message is provided, sends a multipart email (plain text + HTML).
    Returns True if the email was sent successfully, False otherwise.
    """
    for attempt in range(1, max_retries + 1):
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )
            if html_message:
                email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            logger.info(
                f"Email sent successfully to {recipient_list} | Subject: '{subject}' | Attempt: {attempt}"
            )
            return True
        except Exception as e:
            logger.warning(
                f"Email send FAILED to {recipient_list} | Subject: '{subject}' | Attempt: {attempt}/{max_retries} | Error: {e}"
            )
            if attempt < max_retries:
                time.sleep(retry_delay)

    logger.error(
        f"Email send permanently FAILED to {recipient_list} after {max_retries} attempts | Subject: '{subject}'"
    )
    return False