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

def test_auto_save():
    """Test the DASS21 auto-save functionality"""
    
    # Find a user to test with
    test_user = CustomUser.objects.filter(username='justine').first()
    if not test_user:
        print("User 'justine' not found. Creating a test scenario...")
        # Use the first user
        test_user = CustomUser.objects.first()
    
    print(f"Testing with user: {test_user.username}")
    print(f"Current DASS results count: {test_user.dassresult_set.count()}")
    
    # Simulate DASS21 test data
    test_data = {
        'depression': 12,
        'anxiety': 8,
        'stress': 16,
        'depression_severity': 'Mild',
        'anxiety_severity': 'Mild',
        'stress_severity': 'Mild',
        'answers': [1, 2, 1, 0, 2, 1, 0, 1, 2, 1, 0, 2, 1, 0, 1, 2, 1, 0, 2, 1, 0]
    }
    
    # Create a DASS result manually to simulate auto-save
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
        
        print(f"✅ Successfully created DASS result for {test_user.username}")
        print(f"New DASS results count: {test_user.dassresult_set.count()}")
        
        # Check the latest result
        latest_result = test_user.dassresult_set.order_by('-date_taken').first()
        print(f"Latest result: {latest_result}")
        print(f"Depression: {latest_result.depression_score}")
        print(f"Anxiety: {latest_result.anxiety_score}")
        print(f"Stress: {latest_result.stress_score}")
        
    except Exception as e:
        print(f"❌ Error creating DASS result: {e}")

if __name__ == "__main__":
    test_auto_save() 