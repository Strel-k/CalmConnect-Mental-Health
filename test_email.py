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

def inspect_email_credentials():
    """Inspect and validate current email credentials"""
    print("🔍 Inspecting Email Credentials...")
    print("=" * 50)

    # Display current email settings
    print("📧 Current Email Configuration:")
    print(f"   HOST: {settings.EMAIL_HOST}")
    print(f"   PORT: {settings.EMAIL_PORT}")
    print(f"   USER: {settings.EMAIL_HOST_USER}")
    print(f"   PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   SSL: {settings.EMAIL_USE_SSL}")
    print(f"   FROM: {settings.DEFAULT_FROM_EMAIL}")
    print()

    # Validate configuration
    issues = []

    # Check for Mailtrap (development)
    if 'mailtrap' in settings.EMAIL_HOST.lower():
        issues.append("⚠️  USING MAILTRAP - This is for testing only, emails won't reach real addresses!")

    # Check required fields
    if not settings.EMAIL_HOST:
        issues.append("❌ EMAIL_HOST is not set")
    if not settings.EMAIL_HOST_USER:
        issues.append("❌ EMAIL_HOST_USER is not set")
    if not settings.EMAIL_HOST_PASSWORD:
        issues.append("❌ EMAIL_HOST_PASSWORD is not set")
    if not settings.DEFAULT_FROM_EMAIL:
        issues.append("❌ DEFAULT_FROM_EMAIL is not set")

    # Check Gmail-specific issues
    if 'gmail' in settings.EMAIL_HOST.lower():
        if settings.EMAIL_PORT != 587:
            issues.append("⚠️  Gmail typically uses port 587, but you have " + str(settings.EMAIL_PORT))
        if not settings.EMAIL_USE_TLS:
            issues.append("⚠️  Gmail requires TLS=True")
        if settings.EMAIL_USE_SSL:
            issues.append("⚠️  Gmail should use TLS, not SSL")

        # Check if password looks like an app password
        if settings.EMAIL_HOST_PASSWORD and len(settings.EMAIL_HOST_PASSWORD) != 16:
            issues.append("⚠️  Gmail App Passwords are 16 characters. Make sure you're using an App Password, not your regular password.")

    # Check Outlook-specific issues
    if 'outlook' in settings.EMAIL_HOST.lower() or 'hotmail' in settings.EMAIL_HOST.lower():
        if settings.EMAIL_PORT != 587:
            issues.append("⚠️  Outlook typically uses port 587, but you have " + str(settings.EMAIL_PORT))

    # Check SendGrid-specific issues
    if 'sendgrid' in settings.EMAIL_HOST.lower():
        if settings.EMAIL_HOST_USER != 'apikey':
            issues.append("⚠️  SendGrid SMTP user should be 'apikey'")

    if issues:
        print("🚨 Configuration Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print()
    else:
        print("✅ Basic configuration looks good!")
        print()

    return len(issues) == 0

def test_email_configuration():
    """Test email configuration and send a test email"""
    print("🧪 Testing Email Configuration...")
    print("=" * 50)

    # First inspect credentials
    config_ok = inspect_email_credentials()

    if not config_ok:
        print("❌ Configuration issues found. Please fix them before testing.")
        return False

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

def check_railway_env_vars():
    """Check Railway environment variables"""
    print("🚂 Checking Railway Environment Variables...")
    print("=" * 50)

    env_vars = [
        'EMAIL_HOST',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_USE_SSL',
        'DEFAULT_FROM_EMAIL',
        'DATABASE_URL'
    ]

    print("📋 Environment Variables Status:")
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'EMAIL_HOST_PASSWORD':
            # Mask password
            display_value = '*' * len(value) if value != 'NOT SET' else value
        else:
            display_value = value

        status = "✅" if value != 'NOT SET' else "❌"
        print(f"   {status} {var}: {display_value}")

    print()

    # Check if Railway-specific vars are set
    railway_vars = ['RAILWAY_PROJECT_ID', 'RAILWAY_ENVIRONMENT', 'RAILWAY_STATIC_URL']
    railway_present = any(os.environ.get(var) for var in railway_vars)

    if railway_present:
        print("✅ Running on Railway")
    else:
        print("⚠️  Not running on Railway (local development?)")

    print()

if __name__ == '__main__':
    print("🚀 CalmConnect Email Configuration Inspector")
    print("=" * 50)

    # Check environment first
    check_railway_env_vars()

    # Then test configuration
    success = test_email_configuration()

    if 'gmail' in settings.EMAIL_HOST.lower() and not success:
        test_gmail_app_password()

    print()
    print("✨ Inspection completed!")
    sys.exit(0 if success else 1)