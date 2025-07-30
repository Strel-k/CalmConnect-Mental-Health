#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor, CustomUser, Appointment, Feedback
from django.template.loader import render_to_string
from django.test import RequestFactory

def test_feedback_template():
    """Test feedback template rendering with centered counselor info"""
    print("🧪 Testing feedback template with centered counselor info...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Get a counselor and appointment
    counselor = Counselor.objects.first()
    appointment = Appointment.objects.filter(counselor=counselor).first()
    
    if counselor and appointment:
        print(f"👨‍⚕️ Testing with counselor: {counselor.name}")
        print(f"📅 Appointment: {appointment.date} at {appointment.time}")
        
        # Test template rendering
        context = {
            'counselor': counselor,
            'appointment_date': appointment.date.strftime('%B %d, %Y'),
            'appointment_time': appointment.time.strftime('%I:%M %p'),
            'appointment_type': 'Individual Counseling',
            'duration': 60,
            'appointment_id': appointment.id,
        }
        
        try:
            # Render the template
            html_content = render_to_string('mentalhealth/feedback.html', context)
            
            # Check if the centered elements are present
            if 'counselor-avatar' in html_content:
                print("✅ Counselor avatar found in template")
            if 'appointment-details' in html_content:
                print("✅ Appointment details section found")
            if counselor.name in html_content:
                print("✅ Counselor name found in template")
            
            print("✅ Feedback template rendered successfully!")
            print(f"📄 Template size: {len(html_content)} characters")
            
            # Check for centering CSS
            if 'flex-direction: column' in html_content:
                print("✅ Centering CSS found (flex-direction: column)")
            if 'text-align: center' in html_content:
                print("✅ Text centering CSS found")
            if 'align-items: center' in html_content:
                print("✅ Center alignment CSS found")
                
        except Exception as e:
            print(f"❌ Error rendering template: {e}")
    else:
        print("❌ No counselor or appointment found for testing")

if __name__ == "__main__":
    test_feedback_template() 