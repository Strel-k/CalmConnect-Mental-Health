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
from django.utils import timezone

# Setup Django with fallback for missing DATABASE_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Set a dummy DATABASE_URL for testing if not present
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'

try:
    django.setup()
except ValueError as e:
    if "DATABASE_URL environment variable must be set" in str(e):
        print("⚠️  DATABASE_URL not set, using dummy database for email testing...")
        # Force Django to use a dummy database configuration
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            EMAIL_HOST=os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
            EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER', ''),
            EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD', ''),
            EMAIL_PORT=int(os.environ.get('EMAIL_PORT', '587')),
            EMAIL_USE_TLS=os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true',
            EMAIL_USE_SSL=os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true',
            DEFAULT_FROM_EMAIL=os.environ.get('DEFAULT_FROM_EMAIL', 'test@example.com'),
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
            ],
            SECRET_KEY='test-key-for-email-testing',
            USE_TZ=True,
        )
        django.setup()
    else:
        raise

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
        print("📤 Testing email delivery...")

        # Test email addresses
        test_recipients = [
            settings.DEFAULT_FROM_EMAIL,  # Send to yourself
            "test@example.com",  # Dummy address for logging
        ]

        test_subject = f"CalmConnect Email Test - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        test_message = f"""
        Hello!

        This is a test email from CalmConnect.

        Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

        Configuration Details:
        - SMTP Host: {settings.EMAIL_HOST}
        - SMTP Port: {settings.EMAIL_PORT}
        - From Email: {settings.DEFAULT_FROM_EMAIL}
        - TLS: {settings.EMAIL_USE_TLS}
        - SSL: {settings.EMAIL_USE_SSL}

        If you received this email, your SMTP configuration is working correctly!

        Best regards,
        CalmConnect Team
        """

        print(f"📧 Sending test email to: {settings.DEFAULT_FROM_EMAIL}")
        print(f"📧 Subject: {test_subject}")

        # Send test email
        result = send_mail(
            subject=test_subject,
            message=test_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False
        )

        if result == 1:
            print("✅ Test email sent successfully!")
            print(f"   📧 To: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   📧 From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   📧 Subject: {test_subject}")
            print()
            print("🔍 Verification Steps:")
            print("   1. Check your email inbox (including spam/junk folder)")
            print("   2. Look for the subject line above")
            print("   3. If not received in 5-10 minutes, check your SMTP settings")
            print()
            print("💡 Can't check email now? The email was sent successfully.")
            print("   Your SMTP credentials are working correctly!")
            print()
            print("📄 Email Content Preview:")
            print("-" * 40)
            print(test_message.strip())
            print("-" * 40)

            return True
        else:
            print("❌ Email sending failed - Django returned 0 (no emails sent)")
            return False

    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print()
        print("🔧 Troubleshooting Tips:")
        print("   1. Check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print("   2. For Gmail: Use App Passwords, not your regular password")
        print("   3. Verify EMAIL_PORT and EMAIL_USE_TLS settings")
        print("   4. Check if your SMTP provider requires special configuration")
        print("   5. Try sending to a different email address")
        print("   6. Check if your SMTP provider has sending limits")
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