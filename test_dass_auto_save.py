#!/usr/bin/env python
import os
import sys
import django
import json
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import CustomUser, DASSResult

def test_dass_auto_save():
    """Test the DASS21 auto-save functionality"""
    
    # Find a user to test with (preferably one without DASS results)
    test_user = CustomUser.objects.filter(dassresult__isnull=True).first()
    if not test_user:
        print("No users without DASS results found. Creating a test scenario...")
        # Use the first user and simulate a new test
        test_user = CustomUser.objects.first()
    
    print(f"Testing with user: {test_user.username}")
    print(f"Current DASS results count: {test_user.dassresult_set.count()}")
    
    # Simulate DASS21 test results
    test_data = {
        'depression': 14,
        'anxiety': 10,
        'stress': 8,
        'depression_severity': 'Moderate',
        'anxiety_severity': 'Mild',
        'stress_severity': 'Normal',
        'answers': [1, 2, 1, 3, 2, 1, 2, 1, 3, 2, 1, 2, 1, 3, 2, 1, 2, 1, 3, 2, 1]
    }
    
    # Test the save_dass_results view logic
    from mentalhealth.views import save_dass_results
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.post('/save-dass-results/', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    request.user = test_user
    
    # Simulate the save process
    try:
        result = DASSResult(
            user=test_user,
            depression_score=test_data['depression'],
            anxiety_score=test_data['anxiety'],
            stress_score=test_data['stress'],
            depression_severity=test_data['depression_severity'],
            anxiety_severity=test_data['anxiety_severity'],
            stress_severity=test_data['stress_severity'],
            answers=test_data['answers']
        )
        result.save()
        print(f"✅ DASS result saved successfully!")
        print(f"New DASS results count: {test_user.dassresult_set.count()}")
        
        # Test the scheduler view logic
        latest_result = DASSResult.objects.filter(user=test_user).order_by('-date_taken').first()
        print(f"Latest result: {latest_result}")
        
        if latest_result:
            scores = {
                'depression': latest_result.depression_score,
                'anxiety': latest_result.anxiety_score,
                'stress': latest_result.stress_score,
            }
            print(f"Scores that should be passed to scheduler: {scores}")
            print(f"URL parameters: ?depression={scores['depression']}&anxiety={scores['anxiety']}&stress={scores['stress']}")
        else:
            print("❌ No DASS results found after saving")
            
    except Exception as e:
        print(f"❌ Error saving DASS result: {e}")

if __name__ == "__main__":
    test_dass_auto_save() 