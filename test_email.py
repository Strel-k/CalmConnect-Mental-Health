#!/usr/bin/env python
"""
Email Configuration Test Script for CalmConnect
Tests SMTP email sending to verify configuration works
"""

import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

def test_email_configuration():
    """Test email configuration and send a test email"""
    print("🧪 Testing Email Configuration...")
    print("=" * 50)

    # Display current email settings (without password)
    print("📧 Current Email Settings:")
    print(f"   HOST: {settings.EMAIL_HOST}")
    print(f"   PORT: {settings.EMAIL_PORT}")
    print(f"   USER: {settings.EMAIL_HOST_USER}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   SSL: {settings.EMAIL_USE_SSL}")
    print(f"   FROM: {settings.DEFAULT_FROM_EMAIL}")
    print()

    # Check if using Mailtrap (development)
    if 'mailtrap' in settings.EMAIL_HOST.lower():
        print("⚠️  WARNING: Using Mailtrap (development) - emails won't reach real addresses!")
        print("   To send real emails, configure a production SMTP server.")
        print()

    # Test basic email sending
    try:
        print("📤 Sending test email...")

        # Test email to yourself first
        test_subject = "CalmConnect Email Test"
        test_message = """
        Hello!

        This is a test email from CalmConnect.

        If you received this, your email configuration is working correctly!

        Best regards,
        CalmConnect Team
        """

        # Send test email
        result = send_mail(
            subject=test_subject,
            message=test_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Send to yourself
            fail_silently=False
        )

        if result == 1:
            print("✅ Test email sent successfully!")
            print("   Check your inbox for the test email.")
        else:
            print("❌ Email sending failed - no emails sent")

    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print()
        print("🔧 Troubleshooting Tips:")
        print("   1. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print("   2. For Gmail: Use App Passwords, not your regular password")
        print("   3. Verify EMAIL_PORT and EMAIL_USE_TLS settings")
        print("   4. Check if your SMTP provider requires special configuration")
        return False

    print()
    print("🎯 Next Steps:")
    print("   1. If test email worked, configure real recipient emails")
    print("   2. Update Railway environment variables with production SMTP settings")
    print("   3. Test with actual student emails")

    return True

def test_gmail_app_password():
    """Help with Gmail App Password setup"""
    print()
    print("🔐 Gmail App Password Setup:")
    print("   1. Go to https://myaccount.google.com/security")
    print("   2. Enable 2-Factor Authentication")
    print("   3. Go to 'App passwords' section")
    print("   4. Generate password for 'Mail'")
    print("   5. Use that 16-character password as EMAIL_HOST_PASSWORD")
    print()

if __name__ == '__main__':
    print("🚀 CalmConnect Email Configuration Test")
    print("=" * 50)

    success = test_email_configuration()

    if 'gmail' in settings.EMAIL_HOST.lower() and not success:
        test_gmail_app_password()

    print()
    print("✨ Test completed!")
    sys.exit(0 if success else 1)