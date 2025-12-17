"""
Custom email backends for CalmConnect.
"""

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
import logging
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class GmailAPIEmailBackend(BaseEmailBackend):
    """
    Email backend using Gmail API (https://developers.google.com/gmail/api).
    Sends emails via Gmail API HTTP endpoint, bypassing SMTP restrictions on PaaS platforms.
    
    Requires:
    - GMAIL_API_CREDENTIALS: JSON string or base64-encoded service account key
    - GMAIL_FROM_EMAIL: Email address to send from (must match the Gmail account)
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.credentials_str = settings.GMAIL_API_CREDENTIALS
        self.from_email = getattr(settings, 'GMAIL_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.credentials_str:
            logger.error("GMAIL_API_CREDENTIALS not configured")
            if not self.fail_silently:
                raise ValueError("GMAIL_API_CREDENTIALS must be set in settings")
            return 0

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("google-auth-oauthlib and google-api-python-client packages not installed")
            if not self.fail_silently:
                raise ImportError("Install with: pip install google-auth-oauthlib google-api-python-client")
            return 0

        num_sent = 0

        try:
            # Parse credentials (try JSON first, then base64)
            try:
                credentials_dict = json.loads(self.credentials_str)
            except json.JSONDecodeError:
                # Try base64 decode
                credentials_dict = json.loads(base64.b64decode(self.credentials_str))

            # Build service using service account
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
            service = build('gmail', 'v1', credentials=credentials)

            for message in email_messages:
                try:
                    # Build MIME message
                    mime_message = MIMEMultipart('alternative')
                    mime_message['To'] = ', '.join(message.to)
                    mime_message['From'] = self.from_email
                    mime_message['Subject'] = message.subject

                    # Add plain text
                    if message.body:
                        mime_message.attach(MIMEText(message.body, 'plain'))

                    # Add HTML if available
                    if message.alternatives:
                        for content, mimetype in message.alternatives:
                            if mimetype == "text/html":
                                mime_message.attach(MIMEText(content, 'html'))
                                break

                    # Encode and send
                    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
                    send_message = {
                        'raw': raw_message
                    }

                    result = service.users().messages().send(
                        userId='me',
                        body=send_message
                    ).execute()

                    logger.info(f"Email sent via Gmail API. Message ID: {result.get('id')}")
                    num_sent += 1

                except Exception as e:
                    logger.exception(f"Failed to send email via Gmail API: {str(e)}")
                    if not self.fail_silently:
                        raise

        except Exception as e:
            logger.exception(f"Gmail API backend error: {str(e)}")
            if not self.fail_silently:
                raise

        return num_sent
