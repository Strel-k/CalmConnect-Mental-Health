#!/usr/bin/env python
import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from mentalhealth.views import followup_details

User = get_user_model()

def test_counselor_followup_details():
    """Test the followup_details view function for counselors"""

    # Get Justine's user
    justine = User.objects.get(id=66)
    print(f"Testing with counselor: {justine.full_name} (ID: {justine.id})")

    # Create a request factory
    factory = RequestFactory()

    # Create a GET request to the followup_details view
    request = factory.get('/followup/1/details/')
    request.user = justine

    # Call the view function directly
    try:
        response = followup_details(request, request_id=1)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                print(f"API Response success: {data.get('success')}")

                if data.get('success'):
                    print("Response contains:")
                    print(f"  - followup_request: {'Yes' if 'followup_request' in data else 'No'}")
                    print(f"  - appointment: {'Yes' if 'appointment' in data else 'No'}")
                    print(f"  - counselor: {'Yes' if 'counselor' in data else 'No'}")
                    print(f"  - student: {'Yes' if 'student' in data else 'No'}")

                    if 'appointment' in data:
                        appt = data['appointment']
                        print(f"Appointment data: Date={appt.get('date')}, Time={appt.get('time')}, Session Type={appt.get('session_type')}")

                    if 'counselor' in data:
                        counselor = data['counselor']
                        print(f"Counselor data: Name={counselor.get('name')}, Unit={counselor.get('unit')}")

                    if 'student' in data:
                        student = data['student']
                        print(f"Student data: Name={student.get('full_name')}, ID={student.get('student_id')}")
                else:
                    print(f"API Error: {data.get('error', 'Unknown error')}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.content.decode()[:500]}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.content.decode()[:500]}")

    except Exception as e:
        print(f"Exception calling view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_counselor_followup_details()
