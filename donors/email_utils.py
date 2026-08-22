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
    valid_recipients = [r for r in recipient_list if r and r.strip()]
    if not valid_recipients:
        logger.warning(
            f"Email NOT sent — no valid recipient address provided | Subject: '{subject}' | Original recipient_list: {recipient_list}"
        )
        return False

    for attempt in range(1, max_retries + 1):
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=valid_recipients,
            )
            if html_message:
                email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            logger.info(
                f"Email sent successfully to {valid_recipients} | Subject: '{subject}' | Attempt: {attempt}"
            )
            return True
        except Exception as e:
            logger.warning(
                f"Email send FAILED to {valid_recipients} | Subject: '{subject}' | Attempt: {attempt}/{max_retries} | Error: {e}"
            )
            if attempt < max_retries:
                time.sleep(retry_delay)

    logger.error(
        f"Email send permanently FAILED to {valid_recipients} after {max_retries} attempts | Subject: '{subject}'"
    )
    return False