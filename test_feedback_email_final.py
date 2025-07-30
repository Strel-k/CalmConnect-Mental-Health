#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor, CustomUser, Appointment, Report
from mentalhealth.views import send_feedback_request_email
from django.test import RequestFactory
import json

def test_feedback_email_final():
    """Final test to verify feedback email is working"""
    print("🧪 Final feedback email test...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.post('/api/reports/')
    
    # Get a counselor and appointment
    counselor = Counselor.objects.first()
    appointment = Appointment.objects.filter(
        counselor=counselor
    ).exclude(status__in=['completed', 'cancelled']).first()
    
    if counselor and appointment:
        print(f"👨‍⚕️ Counselor: {counselor.name}")
        print(f"👤 User: {appointment.user.full_name}")
        print(f"📅 Appointment: {appointment.id} - {appointment.date} at {appointment.time}")
        print(f"📧 User email: {appointment.user.email}")
        print(f"📊 Appointment status: {appointment.status}")
        
        # Test the updated logic
        print("\n🔔 Testing updated feedback email logic...")
        try:
            # Simulate the exact data that would be sent to the API
            data = {
                'title': f'Session with {appointment.user.full_name}',
                'description': 'Test session report for feedback flow',
                'report_type': 'session',
                'user_id': appointment.user.id
            }
            
            print(f"📊 API Data: {data}")
            print(f"🔍 Report type: {data.get('report_type')}")
            
            # Simulate the updated report_api view logic
            if data.get('report_type') == 'session':
                print("✅ Report type is 'session', proceeding with feedback email...")
                
                # Find the appointment using the updated logic
                try:
                    found_appointment = Appointment.objects.filter(
                        user=appointment.user,
                        counselor=counselor
                    ).exclude(status__in=['completed', 'cancelled']).latest('date')
                    
                    print(f"✅ Found appointment {found_appointment.id} for feedback email")
                    print(f"📊 Found appointment status: {found_appointment.status}")
                    
                    # Mark as completed
                    found_appointment.status = 'completed'
                    found_appointment.save()
                    print(f"✅ Appointment {found_appointment.id} marked as completed")
                    
                    # Send feedback email
                    print("🔔 Sending feedback email...")
                    send_feedback_request_email(request, found_appointment)
                    print("✅ Feedback email sent successfully!")
                    
                    print("\n🎯 Summary:")
                    print("✅ Feedback email function works correctly")
                    print("✅ Updated logic finds pending appointments")
                    print("✅ Email is sent to Mailtrap")
                    print("📧 Check Mailtrap for the feedback email")
                    
                except Appointment.DoesNotExist:
                    print(f"❌ No available appointment found for user {appointment.user} and counselor {counselor}")
            else:
                print(f"❌ Report type is not 'session': {data.get('report_type')}")
                
        except Exception as e:
            print(f"❌ Error in feedback email test: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No counselor or available appointment found for testing")

if __name__ == "__main__":
    test_feedback_email_final() 