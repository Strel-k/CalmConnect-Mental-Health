#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test email functionality"""
    try:
        send_mail(
            'Test Email from CalmConnect',
            'This is a test email to verify email functionality is working.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],  # This won't actually send, just tests the connection
            fail_silently=False
        )
        print("✅ Email test completed successfully!")
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        print(f"Email host: {settings.EMAIL_HOST}")
        print(f"Email port: {settings.EMAIL_PORT}")
        print(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")
    except Exception as e:
        print(f"❌ Email test failed: {e}")

if __name__ == "__main__":
    test_email() 