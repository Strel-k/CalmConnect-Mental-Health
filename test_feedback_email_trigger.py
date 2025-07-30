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

def test_feedback_email_trigger():
    """Test feedback email triggering during report creation"""
    print("🧪 Testing feedback email trigger during report creation...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.post('/api/reports/')
    
    # Get a counselor and appointment
    counselor = Counselor.objects.first()
    appointment = Appointment.objects.filter(counselor=counselor, status='confirmed').first()
    
    if counselor and appointment:
        print(f"👨‍⚕️ Counselor: {counselor.name}")
        print(f"👤 User: {appointment.user.full_name}")
        print(f"📅 Appointment: {appointment.id} - {appointment.date} at {appointment.time}")
        print(f"📧 User email: {appointment.user.email}")
        
        # Test the feedback email function directly
        print("\n🔔 Testing feedback email function directly...")
        try:
            send_feedback_request_email(request, appointment)
            print("✅ Feedback email function executed successfully")
        except Exception as e:
            print(f"❌ Error in feedback email function: {e}")
        
        # Test report creation via API (simulating the actual process)
        print("\n📝 Testing report creation via API...")
        try:
            # Simulate the report API call
            data = {
                'title': f'Session with {appointment.user.full_name}',
                'description': 'Test session report',
                'report_type': 'session',
                'user_id': appointment.user.id
            }
            
            # This would normally be handled by the report_api view
            # For testing, we'll simulate the logic
            appointment.status = 'completed'
            appointment.save()
            print(f"✅ Appointment {appointment.id} marked as completed")
            
            # Create the report
            report = Report.objects.create(
                counselor=counselor,
                user=appointment.user,
                title=data['title'],
                description=data['description'],
                report_type=data['report_type'],
                status='completed'
            )
            print(f"✅ Report {report.id} created successfully")
            
            # Send feedback email
            print("🔔 Sending feedback email...")
            send_feedback_request_email(request, appointment)
            print("✅ Feedback email sent successfully")
            
        except Exception as e:
            print(f"❌ Error in report creation process: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No counselor or confirmed appointment found for testing")

if __name__ == "__main__":
    test_feedback_email_trigger() 