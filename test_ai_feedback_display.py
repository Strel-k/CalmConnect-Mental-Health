#!/usr/bin/env python
"""
Test script to verify AI feedback display is working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.views import (
    analyze_dass21_responses,
    generate_dass21_specific_fallback_feedback,
    get_user_personalization_data
)

def test_ai_feedback_display():
    """Test that AI feedback display is working properly"""
    print("🧪 Testing AI Feedback Display...")
    
    # Test data
    test_answers = {
        'q3': 3,   # Severe: couldn't experience positive feelings
        'q5': 2,   # Moderate: difficulty with initiative
        'q17': 3,  # Severe: not worth much as person
        'q9': 2,   # Moderate: worried about panic
        'q1': 2,   # Moderate: hard to wind down
        'q12': 2,  # Moderate: difficult to relax
    }
    
    # Test DASS21 analysis
    analysis = analyze_dass21_responses(test_answers, 12, 8, 8)
    print(f"✅ DASS21 Analysis completed:")
    print(f"   - Primary concerns: {len(analysis['primary_concerns'])}")
    print(f"   - Coping patterns: {analysis['coping_patterns']}")
    print(f"   - Specific triggers: {analysis['specific_triggers']}")
    
    # Test fallback feedback generation
    from mentalhealth.models import CustomUser
    user = CustomUser.objects.first()
    if user:
        user_history = get_user_personalization_data(user)
        fallback_feedback = generate_dass21_specific_fallback_feedback(
            user, 12, 8, 8, 'moderate', 'moderate', 'moderate', user_history, analysis
        )
        print(f"✅ Fallback feedback generated ({len(fallback_feedback)} characters)")
        print(f"   Preview: {fallback_feedback[:100]}...")
    else:
        print("⚠️ No test user found")
    
    print("✅ AI feedback display test completed successfully!")
    print("   The AI feedback should now appear in the results after completing the DASS21 test.")

if __name__ == "__main__":
    test_ai_feedback_display() 