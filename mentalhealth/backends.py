"""
Custom email backends for CalmConnect.
"""

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
import logging

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend using Resend API (https://resend.com).
    Sends emails via Resend's HTTP API, bypassing SMTP restrictions on PaaS platforms.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.api_key:
            logger.error("RESEND_API_KEY not configured")
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY must be set in settings")
            return 0

        try:
            import resend
        except ImportError:
            logger.error("resend package not installed. Install with: pip install resend")
            if not self.fail_silently:
                raise ImportError("resend package is required. Install it with: pip install resend")
            return 0

        resend.api_key = self.api_key
        num_sent = 0

        for message in email_messages:
            try:
                # Build Resend API request
                payload = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                }

                # Handle plain text and HTML content
                if message.body:
                    payload["text"] = message.body
                if message.alternatives:
                    # If HTML version exists, use it
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            payload["html"] = content
                            break

                # Send via Resend API
                result = resend.Emails.send(payload)

                if result.get("id"):
                    logger.info(f"Email sent via Resend. Message ID: {result.get('id')}")
                    num_sent += 1
                else:
                    error_msg = result.get("message", "Unknown error")
                    logger.error(f"Resend API error: {error_msg}")
                    if not self.fail_silently:
                        raise ValueError(f"Resend API error: {error_msg}")

            except Exception as e:
                logger.exception(f"Failed to send email via Resend: {str(e)}")
                if not self.fail_silently:
                    raise

        return num_sent
