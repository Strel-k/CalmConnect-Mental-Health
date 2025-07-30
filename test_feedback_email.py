#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Appointment, CustomUser, Counselor
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def test_feedback_email():
    """Test feedback email functionality"""
    print("🧪 Testing feedback email functionality...")
    
    # Check if we have any data
    print(f"👥 Users in database: {CustomUser.objects.count()}")
    print(f"👨‍⚕️ Counselors in database: {Counselor.objects.count()}")
    print(f"📅 Appointments in database: {Appointment.objects.count()}")
    
    # Find an existing appointment to test with
    try:
        appointment = Appointment.objects.filter(status='confirmed').first()
        if appointment:
            print(f"📅 Found appointment: {appointment.id} for {appointment.user.full_name}")
            print(f"📧 User email: {appointment.user.email}")
            print(f"👨‍⚕️ Counselor: {appointment.counselor.name}")
            
            # Test the email template rendering
            print("🔔 Testing email template rendering...")
            
            html_message = render_to_string('mentalhealth/feedback-request.html', {
                'user': appointment.user,
                'appointment': appointment,
                'feedback_url': f"http://localhost:8000/feedback/{appointment.id}/",
            })
            
            print("✅ Email template rendered successfully!")
            print(f"📧 HTML message length: {len(html_message)} characters")
            
            # Test sending the email
            print("📤 Testing email sending...")
            send_mail(
                'Test: How was your CalmConnect session?',
                'This is a test email for feedback functionality.',
                settings.DEFAULT_FROM_EMAIL,
                [appointment.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            print("✅ Email sent successfully!")
            print("📧 Check your email inbox or Mailtrap for the test email")
            
        else:
            print("❌ No confirmed appointments found for testing")
            
    except Exception as e:
        print(f"❌ Error during feedback email test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feedback_email() 