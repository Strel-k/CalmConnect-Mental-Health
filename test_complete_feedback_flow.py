#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor, CustomUser, Appointment, Report
from mentalhealth.views import send_feedback_request_email
from django.test import RequestFactory
from django.urls import reverse
import json

def test_complete_feedback_flow():
    """Test the complete feedback flow from report creation to email sending"""
    print("🧪 Testing complete feedback flow...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.post('/api/reports/')
    
    # Get a counselor and appointment
    counselor = Counselor.objects.first()
    appointment = Appointment.objects.filter(counselor=counselor, status='pending').first()
    
    if counselor and appointment:
        print(f"👨‍⚕️ Counselor: {counselor.name}")
        print(f"👤 User: {appointment.user.full_name}")
        print(f"📅 Appointment: {appointment.id} - {appointment.date} at {appointment.time}")
        print(f"📧 User email: {appointment.user.email}")
        print(f"📊 Appointment status: {appointment.status}")
        
        # Test 1: Direct feedback email function
        print("\n🔔 Test 1: Direct feedback email function")
        try:
            send_feedback_request_email(request, appointment)
            print("✅ Direct feedback email sent successfully")
        except Exception as e:
            print(f"❌ Error in direct feedback email: {e}")
        
        # Test 2: Simulate report creation via API
        print("\n📝 Test 2: Simulate report creation via API")
        try:
            # Simulate the exact data that would be sent to the API
            data = {
                'title': f'Session with {appointment.user.full_name}',
                'description': 'Test session report for feedback flow',
                'report_type': 'session',  # This is crucial for feedback email
                'user_id': appointment.user.id
            }
            
            print(f"📊 API Data: {data}")
            print(f"🔍 Report type: {data.get('report_type')}")
            
            # Simulate the report_api view logic
            if data.get('report_type') == 'session':
                print("✅ Report type is 'session', proceeding with feedback email...")
                
                # Find the appointment
                try:
                    found_appointment = Appointment.objects.filter(
                        user=appointment.user,
                        counselor=counselor,
                        status='confirmed'
                    ).latest('date')
                    
                    print(f"✅ Found appointment {found_appointment.id} for feedback email")
                    print(f"📊 Found appointment status: {found_appointment.status}")
                    
                    # Mark as completed
                    found_appointment.status = 'completed'
                    found_appointment.save()
                    print(f"✅ Appointment {found_appointment.id} marked as completed")
                    
                    # Send feedback email
                    print("🔔 Sending feedback email...")
                    send_feedback_request_email(request, found_appointment)
                    print("✅ Feedback email sent successfully via API simulation")
                    
                except Appointment.DoesNotExist:
                    print(f"❌ No confirmed appointment found for user {appointment.user} and counselor {counselor}")
            else:
                print(f"❌ Report type is not 'session': {data.get('report_type')}")
                
        except Exception as e:
            print(f"❌ Error in API simulation: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Check if feedback email template exists
        print("\n📧 Test 3: Check feedback email template")
        try:
            from django.template.loader import render_to_string
            html_content = render_to_string('mentalhealth/feedback-request.html', {
                'user': appointment.user,
                'appointment': appointment,
                'feedback_url': f"http://localhost:8000/feedback/{appointment.id}/",
            })
            print(f"✅ Feedback email template rendered successfully ({len(html_content)} characters)")
        except Exception as e:
            print(f"❌ Error rendering feedback email template: {e}")
        
        # Test 4: Check email settings
        print("\n⚙️ Test 4: Check email settings")
        from django.conf import settings
        print(f"📧 Email backend: {settings.EMAIL_BACKEND}")
        print(f"📧 Email host: {settings.EMAIL_HOST}")
        print(f"📧 Email port: {settings.EMAIL_PORT}")
        print(f"📧 Default from email: {settings.DEFAULT_FROM_EMAIL}")
        
        print("\n🎯 Summary:")
        print("✅ If all tests passed, the feedback email should be sent to Mailtrap")
        print("📧 Check your Mailtrap inbox at: https://mailtrap.io/")
        print("📧 Look for emails from: noreply@calmconnect.com")
        print("📧 Subject: 'How was your CalmConnect session?'")
        
    else:
        print("❌ No counselor or confirmed appointment found for testing")

if __name__ == "__main__":
    test_complete_feedback_flow() 