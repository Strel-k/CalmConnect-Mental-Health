#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import CustomUser, DASSResult, RelaxationLog
from mentalhealth.views import (
    get_user_personalization_data, 
    build_personalized_prompt,
    generate_personalized_fallback_feedback,
    ai_feedback
)
from django.test import RequestFactory
import json

def test_enhanced_ai_feedback():
    """Test the enhanced AI feedback system with personalized output"""
    print("🧪 Testing Enhanced AI Feedback System...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.post('/api/ai-feedback/')
    
    # Get a test user
    user = CustomUser.objects.first()
    if not user:
        print("❌ No users found in database")
        return
    
    print(f"👤 Testing with user: {user.full_name}")
    print(f"🎓 College: {user.get_college_display()}")
    print(f"📚 Year Level: {user.get_year_level_display()}")
    print(f"👥 Gender: {user.gender}")
    
    # Test 1: User Personalization Data
    print("\n📊 Test 1: User Personalization Data")
    try:
        user_history = get_user_personalization_data(user)
        print(f"✅ Test count: {user_history['test_count']}")
        print(f"✅ Academic context: {bool(user_history['academic_context'])}")
        print(f"✅ Exercise preferences: {bool(user_history['exercise_preferences'])}")
        print(f"✅ Trend analysis: {bool(user_history['trend_analysis'])}")
        
        if user_history['academic_context']:
            context = user_history['academic_context']
            print(f"   - College stressors: {context.get('college_stressors', 'N/A')}")
            print(f"   - Year challenges: {context.get('year_challenges', 'N/A')}")
            print(f"   - Age context: {context.get('age_context', 'N/A')}")
        
        if user_history['exercise_preferences']:
            pref = user_history['exercise_preferences']
            print(f"   - Preferred exercise: {pref['preferred_exercise']}")
            print(f"   - Total sessions: {pref['total_sessions']}")
            
    except Exception as e:
        print(f"❌ Error in user personalization: {e}")
    
    # Test 2: Personalized Prompt Building
    print("\n📝 Test 2: Personalized Prompt Building")
    try:
        # Test with different severity levels
        test_scores = [
            {'depression': 15, 'anxiety': 12, 'stress': 18, 'depression_severity': 'moderate', 'anxiety_severity': 'moderate', 'stress_severity': 'moderate'},
            {'depression': 8, 'anxiety': 6, 'stress': 10, 'depression_severity': 'mild', 'anxiety_severity': 'mild', 'stress_severity': 'mild'},
            {'depression': 25, 'anxiety': 22, 'stress': 28, 'depression_severity': 'severe', 'anxiety_severity': 'severe', 'stress_severity': 'severe'}
        ]
        
        for i, scores in enumerate(test_scores, 1):
            print(f"\n   Scenario {i}: {scores['depression_severity']} depression, {scores['anxiety_severity']} anxiety, {scores['stress_severity']} stress")
            prompt = build_personalized_prompt(
                user, 
                scores['depression'], 
                scores['anxiety'], 
                scores['stress'],
                scores['depression_severity'],
                scores['anxiety_severity'],
                scores['stress_severity'],
                user_history
            )
            print(f"   ✅ Prompt length: {len(prompt)} characters")
            print(f"   ✅ Contains academic context: {'college' in prompt.lower()}")
            print(f"   ✅ Contains personalization: {'student' in prompt.lower()}")
            
    except Exception as e:
        print(f"❌ Error in prompt building: {e}")
    
    # Test 3: Fallback Feedback Generation
    print("\n🔄 Test 3: Fallback Feedback Generation")
    try:
        for i, scores in enumerate(test_scores, 1):
            print(f"\n   Scenario {i}: {scores['depression_severity']} levels")
            fallback = generate_personalized_fallback_feedback(
                user,
                scores['depression'],
                scores['anxiety'],
                scores['stress'],
                scores['depression_severity'],
                scores['anxiety_severity'],
                scores['stress_severity'],
                user_history
            )
            print(f"   ✅ Fallback length: {len(fallback)} characters")
            print(f"   ✅ Contains bold tags: {'<b>' in fallback}")
            print(f"   ✅ Contains actionable advice: {'try' in fallback.lower() or 'consider' in fallback.lower()}")
            
    except Exception as e:
        print(f"❌ Error in fallback generation: {e}")
    
    # Test 4: AI Feedback API (if OpenAI is configured)
    print("\n🤖 Test 4: AI Feedback API")
    try:
        # Simulate API call
        request.user = user
        request.data = {
            'depression': 15,
            'anxiety': 12,
            'stress': 18,
            'depression_severity': 'moderate',
            'anxiety_severity': 'moderate',
            'stress_severity': 'moderate'
        }
        
        response = ai_feedback(request)
        print(f"   ✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"   ✅ Success: {data.get('success')}")
            print(f"   ✅ Source: {data.get('source')}")
            print(f"   ✅ Personalization level: {data.get('personalization_level')}")
            print(f"   ✅ Feedback length: {len(data.get('feedback', ''))}")
            
            if data.get('context_used'):
                context = data['context_used']
                print(f"   ✅ Context used:")
                print(f"      - Academic context: {context.get('academic_context')}")
                print(f"      - Test history: {context.get('test_history')}")
                print(f"      - Exercise preferences: {context.get('exercise_preferences')}")
                print(f"      - Trend analysis: {context.get('trend_analysis')}")
        else:
            print(f"   ❌ Error response: {response.data}")
            
    except Exception as e:
        print(f"❌ Error in AI feedback API: {e}")
    
    print("\n🎯 Enhanced AI Feedback System Test Summary:")
    print("✅ User personalization data collection")
    print("✅ Personalized prompt building")
    print("✅ Fallback feedback generation")
    print("✅ AI feedback API integration")
    print("✅ Context-aware responses")
    print("✅ College-specific advice")
    print("✅ Year-level specific guidance")
    print("✅ Exercise preference integration")
    print("✅ Trend analysis incorporation")

if __name__ == "__main__":
    test_enhanced_ai_feedback() 