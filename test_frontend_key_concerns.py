#!/usr/bin/env python
"""
Test to verify frontend Key Concerns display logic
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.views import analyze_dass21_responses

def test_frontend_key_concerns():
    """Test the frontend Key Concerns display logic"""
    print("🔍 Testing Frontend Key Concerns Display Logic...")
    
    # Test with sample data that should show concerns
    test_answers = {
        'q3': 3,   # Severe: couldn't experience positive feelings
        'q5': 2,   # Moderate: difficulty with initiative
        'q17': 3,  # Severe: not worth much as person
        'q9': 2,   # Moderate: worried about panic
        'q1': 2,   # Moderate: hard to wind down
        'q12': 2,  # Moderate: difficult to relax
    }
    
    # Analyze the responses
    analysis = analyze_dass21_responses(test_answers, 12, 10, 8)
    
    # Simulate the frontend data structure
    feedback_data = {
        'feedback': "I notice you're having difficulty experiencing positive feelings. <b>Try starting with small activities you once enjoyed, even if just for 5 minutes each day.</b>",
        'source': 'fallback',
        'personalization_level': 'high',
        'dass_analysis': analysis
    }
    
    print(f"✅ Feedback Data Structure:")
    print(f"   Success: {feedback_data.get('success', 'N/A')}")
    print(f"   Source: {feedback_data['source']}")
    print(f"   Personalization level: {feedback_data['personalization_level']}")
    print(f"   DASS analysis present: {'dass_analysis' in feedback_data}")
    
    if 'dass_analysis' in feedback_data:
        dass_data = feedback_data['dass_analysis']
        print(f"\n🔍 DASS Analysis Data:")
        print(f"   Primary concerns count: {len(dass_data.get('primary_concerns', []))}")
        print(f"   Coping patterns count: {len(dass_data.get('coping_patterns', []))}")
        print(f"   Specific triggers count: {len(dass_data.get('specific_triggers', []))}")
        
        # Test the frontend conditional logic
        primary_concerns_condition = (
            dass_data.get('primary_concerns') and 
            len(dass_data['primary_concerns']) > 0
        )
        
        coping_patterns_condition = (
            dass_data.get('coping_patterns') and 
            len(dass_data['coping_patterns']) > 0
        )
        
        specific_triggers_condition = (
            dass_data.get('specific_triggers') and 
            len(dass_data['specific_triggers']) > 0
        )
        
        print(f"\n🔍 Frontend Display Conditions:")
        print(f"   Primary concerns should display: {primary_concerns_condition}")
        print(f"   Coping patterns should display: {coping_patterns_condition}")
        print(f"   Specific triggers should display: {specific_triggers_condition}")
        
        if primary_concerns_condition:
            print(f"\n🔴 PRIMARY CONCERNS (Will display in frontend):")
            for i, concern in enumerate(dass_data['primary_concerns'][:3], 1):
                print(f"   {i}. {concern['question']} ({concern['severity']})")
        else:
            print(f"\n❌ No primary concerns to display")
        
        if coping_patterns_condition:
            print(f"\n🟡 COPING PATTERNS (Will display in frontend):")
            for pattern in dass_data['coping_patterns']:
                print(f"   • {pattern}")
        else:
            print(f"\n❌ No coping patterns to display")
        
        if specific_triggers_condition:
            print(f"\n🔵 SPECIFIC TRIGGERS (Will display in frontend):")
            for trigger in dass_data['specific_triggers']:
                print(f"   • {trigger}")
        else:
            print(f"\n❌ No specific triggers to display")
    
    print(f"\n✅ Frontend Display Test Results:")
    if primary_concerns_condition:
        print("   ✅ Key Concerns section WILL display")
        print("   ✅ Will show specific DASS21 responses")
    else:
        print("   ❌ Key Concerns section will NOT display")
        print("   ⚠️ This might be why the section appears empty")
    
    if coping_patterns_condition:
        print("   ✅ Coping Patterns section WILL display")
    else:
        print("   ❌ Coping Patterns section will NOT display")
    
    if specific_triggers_condition:
        print("   ✅ Specific Triggers section WILL display")
    else:
        print("   ❌ Specific Triggers section will NOT display")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if not primary_concerns_condition:
        print("   • The issue might be that no DASS21 answers are being collected")
        print("   • Check if all 21 DASS21 questions are being answered")
        print("   • Verify that the answers are being sent to the API")
    else:
        print("   • The data structure is correct")
        print("   • The frontend should display the Key Concerns")
        print("   • Check browser console for any JavaScript errors")

if __name__ == "__main__":
    test_frontend_key_concerns() 