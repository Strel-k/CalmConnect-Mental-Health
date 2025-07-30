#!/usr/bin/env python
"""
Debug script to test AI feedback API and see what data is returned
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.views import (
    analyze_dass21_responses,
    generate_dass21_specific_fallback_feedback,
    get_user_personalization_data,
    ai_feedback
)
from django.test import RequestFactory
from django.contrib.auth import get_user_model
import json

def test_ai_feedback_api():
    """Test the AI feedback API to see what data is returned"""
    print("🔍 Testing AI Feedback API Response...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.post('/api/ai-feedback/')
    
    # Get a test user
    User = get_user_model()
    user = User.objects.first()
    if not user:
        print("❌ No test user found")
        return
    
    # Test data with moderate to severe responses
    test_data = {
        'depression': 12,
        'anxiety': 10,
        'stress': 8,
        'answers': {
            'q3': 3,   # Severe: couldn't experience positive feelings
            'q5': 2,   # Moderate: difficulty with initiative
            'q17': 3,  # Severe: not worth much as person
            'q9': 2,   # Moderate: worried about panic
            'q1': 2,   # Moderate: hard to wind down
            'q12': 2,  # Moderate: difficult to relax
        }
    }
    
    # Set request data
    request.data = test_data
    request.user = user
    
    print(f"✅ Testing with user: {user.username}")
    print(f"✅ Test data: {test_data}")
    
    # Test DASS21 analysis directly
    analysis = analyze_dass21_responses(
        test_data['answers'], 
        test_data['depression'],
        test_data['anxiety'], 
        test_data['stress']
    )
    
    print(f"\n🔍 DASS21 Analysis Results:")
    print(f"   Primary concerns: {len(analysis['primary_concerns'])}")
    for i, concern in enumerate(analysis['primary_concerns'], 1):
        print(f"   {i}. {concern['question']} ({concern['severity']})")
    
    print(f"   Coping patterns: {analysis['coping_patterns']}")
    print(f"   Specific triggers: {analysis['specific_triggers']}")
    
    # Test fallback feedback generation
    user_history = get_user_personalization_data(user)
    fallback_feedback = generate_dass21_specific_fallback_feedback(
        user,
        test_data['depression'],
        test_data['anxiety'],
        test_data['stress'],
        'moderate', 'moderate', 'moderate',
        user_history,
        analysis
    )
    
    print(f"\n🔍 Fallback Feedback Response Structure:")
    response_data = {
        'success': True,
        'feedback': fallback_feedback,
        'source': 'fallback',
        'personalization_level': 'high',
        'dass_analysis': analysis,
        'context_used': {
            'academic_context': bool(user_history['academic_context']),
            'test_history': user_history['test_count'],
            'exercise_preferences': bool(user_history['exercise_preferences']),
            'trend_analysis': bool(user_history['trend_analysis']),
            'dass_specific': True
        }
    }
    
    print(f"   Success: {response_data['success']}")
    print(f"   Source: {response_data['source']}")
    print(f"   Personalization level: {response_data['personalization_level']}")
    print(f"   DASS analysis present: {'dass_analysis' in response_data}")
    print(f"   Primary concerns count: {len(response_data['dass_analysis']['primary_concerns'])}")
    print(f"   Coping patterns count: {len(response_data['dass_analysis']['coping_patterns'])}")
    print(f"   Specific triggers count: {len(response_data['dass_analysis']['specific_triggers'])}")
    
    # Test the actual API endpoint
    try:
        response = ai_feedback(request)
        print(f"\n🔍 API Response Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"   Success: {response.data.get('success', 'N/A')}")
            print(f"   Source: {response.data.get('source', 'N/A')}")
            print(f"   DASS analysis present: {'dass_analysis' in response.data}")
            if 'dass_analysis' in response.data:
                dass_data = response.data['dass_analysis']
                print(f"   Primary concerns: {len(dass_data.get('primary_concerns', []))}")
                print(f"   Coping patterns: {len(dass_data.get('coping_patterns', []))}")
                print(f"   Specific triggers: {len(dass_data.get('specific_triggers', []))}")
                
                # Show the actual concerns
                if dass_data.get('primary_concerns'):
                    print(f"\n🔴 PRIMARY CONCERNS FROM API:")
                    for i, concern in enumerate(dass_data['primary_concerns'][:3], 1):
                        print(f"   {i}. {concern['question']} ({concern['severity']})")
                
                if dass_data.get('coping_patterns'):
                    print(f"\n🟡 COPING PATTERNS FROM API:")
                    for pattern in dass_data['coping_patterns']:
                        print(f"   • {pattern}")
                
                if dass_data.get('specific_triggers'):
                    print(f"\n🔵 SPECIFIC TRIGGERS FROM API:")
                    for trigger in dass_data['specific_triggers']:
                        print(f"   • {trigger}")
            else:
                print("   ❌ No dass_analysis in response")
        else:
            print("   ❌ No data in response")
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
    
    print(f"\n✅ Debug test completed!")

if __name__ == "__main__":
    test_ai_feedback_api() 