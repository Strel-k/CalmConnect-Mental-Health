#!/usr/bin/env python
"""
Demonstration of Key Concerns Identified by DASS21-Specific Feedback System
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.views import analyze_dass21_responses

def demonstrate_key_concerns():
    """Demonstrate the key concerns identified by the DASS21 analysis system"""
    print("🔍 DASS21 Key Concerns Identification System")
    print("=" * 60)
    
    # Test scenarios with different types of concerns
    test_scenarios = [
        {
            'name': 'Depression-Focused Concerns',
            'description': 'Student showing primarily depression symptoms',
            'answers': {
                'q3': 3,   # Severe: couldn't experience positive feelings
                'q5': 3,   # Severe: difficulty with initiative
                'q10': 2,  # Moderate: nothing to look forward to
                'q13': 2,  # Moderate: down-hearted
                'q16': 1,  # Mild: unable to become enthusiastic
                'q17': 3,  # Severe: not worth much as person
                'q21': 2,  # Moderate: life meaningless
                # Anxiety questions (mild responses)
                'q2': 1, 'q4': 1, 'q7': 1, 'q9': 1, 'q15': 1, 'q19': 1, 'q20': 1,
                # Stress questions (mild responses)
                'q1': 1, 'q6': 1, 'q8': 1, 'q11': 1, 'q12': 1, 'q14': 1, 'q18': 1
            }
        },
        {
            'name': 'Anxiety-Focused Concerns',
            'description': 'Student showing primarily anxiety symptoms',
            'answers': {
                'q2': 3,   # Severe: dryness of mouth
                'q4': 3,   # Severe: breathing difficulty
                'q7': 2,   # Moderate: trembling
                'q9': 3,   # Severe: worried about panic
                'q15': 3,  # Severe: close to panic
                'q19': 2,  # Moderate: heart awareness
                'q20': 2,  # Moderate: scared without reason
                # Depression questions (mild responses)
                'q3': 1, 'q5': 1, 'q10': 1, 'q13': 1, 'q16': 1, 'q17': 1, 'q21': 1,
                # Stress questions (mild responses)
                'q1': 1, 'q6': 1, 'q8': 1, 'q11': 1, 'q12': 1, 'q14': 1, 'q18': 1
            }
        },
        {
            'name': 'Stress-Focused Concerns',
            'description': 'Student showing primarily stress symptoms',
            'answers': {
                'q1': 3,   # Severe: hard to wind down
                'q6': 3,   # Severe: over-react to situations
                'q8': 2,   # Moderate: using nervous energy
                'q11': 3,  # Severe: getting agitated
                'q12': 3,  # Severe: difficult to relax
                'q14': 2,  # Moderate: intolerant of interruptions
                'q18': 2,  # Moderate: rather touchy
                # Depression questions (mild responses)
                'q3': 1, 'q5': 1, 'q10': 1, 'q13': 1, 'q16': 1, 'q17': 1, 'q21': 1,
                # Anxiety questions (mild responses)
                'q2': 1, 'q4': 1, 'q7': 1, 'q9': 1, 'q15': 1, 'q19': 1, 'q20': 1
            }
        },
        {
            'name': 'Mixed Moderate Concerns',
            'description': 'Student showing moderate symptoms across all dimensions',
            'answers': {
                'q3': 2,  # Moderate: couldn't experience positive feelings
                'q5': 2,  # Moderate: difficulty with initiative
                'q10': 2, # Moderate: nothing to look forward to
                'q13': 2, # Moderate: down-hearted
                'q16': 1, # Mild: unable to become enthusiastic
                'q17': 2, # Moderate: not worth much as person
                'q21': 1, # Mild: life meaningless
                'q2': 2,  # Moderate: dryness of mouth
                'q4': 2,  # Moderate: breathing difficulty
                'q7': 2,  # Moderate: trembling
                'q9': 2,  # Moderate: worried about panic
                'q15': 1, # Mild: close to panic
                'q19': 2, # Moderate: heart awareness
                'q20': 2, # Moderate: scared without reason
                'q1': 2,  # Moderate: hard to wind down
                'q6': 2,  # Moderate: over-react to situations
                'q8': 2,  # Moderate: using nervous energy
                'q11': 2, # Moderate: getting agitated
                'q12': 2, # Moderate: difficult to relax
                'q14': 2, # Moderate: intolerant of interruptions
                'q18': 2, # Moderate: rather touchy
            }
        },
        {
            'name': 'Self-Esteem and Motivation Issues',
            'description': 'Student struggling with self-worth and motivation',
            'answers': {
                'q17': 3, # Severe: not worth much as person
                'q5': 3,  # Severe: difficulty with initiative
                'q3': 2,  # Moderate: couldn't experience positive feelings
                'q10': 2, # Moderate: nothing to look forward to
                'q16': 2, # Moderate: unable to become enthusiastic
                'q21': 2, # Moderate: life meaningless
                # Other questions (mild responses)
                'q1': 1, 'q2': 1, 'q4': 1, 'q6': 1, 'q7': 1, 'q8': 1, 'q9': 1,
                'q11': 1, 'q12': 1, 'q13': 1, 'q14': 1, 'q15': 1, 'q18': 1, 'q19': 1, 'q20': 1
            }
        },
        {
            'name': 'Panic and Social Anxiety',
            'description': 'Student experiencing panic attacks and social anxiety',
            'answers': {
                'q9': 3,  # Severe: worried about panic situations
                'q15': 3, # Severe: close to panic
                'q4': 3,  # Severe: breathing difficulty
                'q20': 3, # Severe: scared without reason
                'q2': 2,  # Moderate: dryness of mouth
                'q7': 2,  # Moderate: trembling
                'q19': 2, # Moderate: heart awareness
                # Other questions (mild responses)
                'q1': 1, 'q3': 1, 'q5': 1, 'q6': 1, 'q8': 1, 'q10': 1, 'q11': 1,
                'q12': 1, 'q13': 1, 'q14': 1, 'q16': 1, 'q17': 1, 'q18': 1, 'q21': 1
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print("-" * 50)
        
        # Analyze the responses
        analysis = analyze_dass21_responses(
            scenario['answers'], 
            depression=12, anxiety=10, stress=8  # Example scores
        )
        
        # Display primary concerns (top 3)
        print("🔴 PRIMARY CONCERNS IDENTIFIED:")
        if analysis['primary_concerns']:
            for j, concern in enumerate(analysis['primary_concerns'][:3], 1):
                severity_emoji = "🔴" if concern['severity'] == 'severe' else "🟡"
                print(f"   {j}. {severity_emoji} {concern['question']}")
                print(f"      Severity: {concern['severity'].upper()} (Score: {concern['score']})")
        else:
            print("   No significant concerns identified")
        
        # Display coping patterns
        print("\n🟡 COPING PATTERNS IDENTIFIED:")
        if analysis['coping_patterns']:
            for pattern in analysis['coping_patterns']:
                print(f"   • {pattern.replace('_', ' ').title()}")
        else:
            print("   No specific coping patterns identified")
        
        # Display specific triggers
        print("\n🔵 SPECIFIC TRIGGERS IDENTIFIED:")
        if analysis['specific_triggers']:
            for trigger in analysis['specific_triggers']:
                print(f"   • {trigger.replace('_', ' ').title()}")
        else:
            print("   No specific triggers identified")
        
        # Display symptom counts
        print(f"\n📊 SYMPTOM SUMMARY:")
        print(f"   • Depression symptoms: {len(analysis['depression_symptoms'])}")
        print(f"   • Anxiety symptoms: {len(analysis['anxiety_symptoms'])}")
        print(f"   • Stress symptoms: {len(analysis['stress_symptoms'])}")
        
        print("\n" + "=" * 60)
    
    print("\n🎯 KEY CONCERNS CATEGORIES:")
    print("The system identifies these types of concerns:")
    print("🔴 SEVERE CONCERNS (Score 3):")
    print("   • Self-worth issues (q17)")
    print("   • Panic attacks (q15)")
    print("   • Breathing difficulties (q4)")
    print("   • Motivation struggles (q5)")
    print("   • Positive feelings absence (q3)")
    print("   • Relaxation challenges (q1, q12)")
    print("   • Emotional reactivity (q6)")
    
    print("\n🟡 MODERATE CONCERNS (Score 2):")
    print("   • Mild versions of the above symptoms")
    print("   • Sensitivity to criticism (q18)")
    print("   • Social anxiety (q9)")
    print("   • Agitation (q11)")
    
    print("\n🟢 COPING PATTERNS IDENTIFIED:")
    print("   • Difficulty relaxing")
    print("   • Relaxation challenges")
    print("   • Emotional reactivity")
    print("   • Sensitivity to criticism")
    
    print("\n🔵 SPECIFIC TRIGGERS IDENTIFIED:")
    print("   • Social situations")
    print("   • Panic attacks")
    print("   • Motivation challenges")
    print("   • Self-esteem issues")

if __name__ == "__main__":
    demonstrate_key_concerns() 