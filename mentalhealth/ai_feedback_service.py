"""
AI Feedback Service for CalmConnect
Provides personalized AI-generated feedback for DASS21 assessments
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import openai
from django.conf import settings

from .models import CustomUser, DASSResult, RelaxationLog, Appointment, Feedback

logger = logging.getLogger(__name__)


@dataclass
class DASSAnalysis:
    """Structured analysis of DASS21 responses"""
    depression_symptoms: List[Dict[str, Any]]
    anxiety_symptoms: List[Dict[str, Any]]
    stress_symptoms: List[Dict[str, Any]]
    primary_concerns: List[Dict[str, Any]]
    coping_patterns: List[str]
    specific_triggers: List[str]
    risk_level: str
    recommended_actions: List[str]


@dataclass
class UserContext:
    """Comprehensive user context for personalization"""
    test_count: int
    trend_analysis: Optional[Dict[str, str]]
    academic_context: Optional[Dict[str, Any]]
    exercise_preferences: Optional[Dict[str, Any]]
    recent_results: List[DASSResult]
    appointment_history: List[Appointment]
    feedback_history: List[Feedback]


class AIFeedbackService:
    """Service class for AI-powered feedback generation"""

    def __init__(self):
        self.openai_available = bool(getattr(settings, 'OPENAI_API_KEY', None))
        if self.openai_available:
            openai.api_key = settings.OPENAI_API_KEY

    def generate_feedback(self, user: CustomUser, dass_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to generate personalized AI feedback with structured sections

        Args:
            user: The user requesting feedback
            dass_data: Dictionary containing DASS21 scores and answers

        Returns:
            Dictionary with structured feedback sections, tips box, and metadata
        """
        try:
            # Validate input data
            self._validate_dass_data(dass_data)

            # Gather comprehensive user context
            user_context = self._gather_user_context(user)

            # Analyze DASS21 responses
            dass_analysis = self._analyze_dass21_responses(
                dass_data['answers'],
                dass_data['depression'],
                dass_data['anxiety'],
                dass_data['stress']
            )

            # Generate structured feedback with separate sections
            structured_feedback = self._generate_structured_feedback(
                user, dass_data, user_context, dass_analysis
            )

            # Generate mental health tips in a separate box/section
            tips_box = self._generate_tips_box(
                user, dass_data, user_context, dass_analysis
            )

            return {
                'success': True,
                'structured_feedback': structured_feedback,
                'tips_box': tips_box,
                'source': structured_feedback.get('source', 'fallback'),
                'personalization_level': 'high',
                'dass_analysis': self._serialize_dass_analysis(dass_analysis),
                'context_used': self._get_context_summary(user_context),
                'risk_assessment': dass_analysis.risk_level,
                'recommended_actions': dass_analysis.recommended_actions,
                # Legacy compatibility
                'feedback': structured_feedback.get('full_feedback', ''),
                'tips': tips_box.get('tips_content', '')
            }

        except Exception as e:
            logger.error(f"AI feedback generation error for user {user.id}: {str(e)}")
            return self._generate_fallback_response(user, dass_data, str(e))

    def _validate_dass_data(self, dass_data: Dict[str, Any]) -> None:
        """Validate DASS21 input data"""
        required_fields = ['depression', 'anxiety', 'stress', 'answers']
        for field in required_fields:
            if field not in dass_data:
                raise ValueError(f"Missing required field: {field}")

        scores = [dass_data['depression'], dass_data['anxiety'], dass_data['stress']]
        if not all(isinstance(score, int) and 0 <= score <= 63 for score in scores):
            raise ValueError("Invalid DASS21 scores. Must be integers between 0-63")

    def _gather_user_context(self, user: CustomUser) -> UserContext:
        """Gather comprehensive user context for personalization"""
        # Get DASS results history
        dass_results = DASSResult.objects.filter(user=user).order_by('-date_taken')[:5]

        # Analyze trends
        trend_analysis = None
        if len(dass_results) >= 2:
            trend_analysis = self._analyze_dass_trends(dass_results)

        # Get academic context
        academic_context = self._get_academic_context(user)

        # Get exercise preferences
        relaxation_logs = RelaxationLog.objects.filter(user=user).order_by('-timestamp')[:20]
        exercise_preferences = self._analyze_exercise_preferences(relaxation_logs)

        # Get appointment and feedback history
        appointments = Appointment.objects.filter(user=user).order_by('-date')[:5]
        feedbacks = Feedback.objects.filter(user=user).order_by('-submitted_at')[:3]

        return UserContext(
            test_count=len(dass_results),
            trend_analysis=trend_analysis,
            academic_context=academic_context,
            exercise_preferences=exercise_preferences,
            recent_results=list(dass_results),
            appointment_history=list(appointments),
            feedback_history=list(feedbacks)
        )

    def _analyze_dass21_responses(self, answers: Dict[str, Any], depression: int,
                                anxiety: int, stress: int) -> DASSAnalysis:
        """Analyze DASS21 responses for targeted feedback"""
        analysis = DASSAnalysis(
            depression_symptoms=[],
            anxiety_symptoms=[],
            stress_symptoms=[],
            primary_concerns=[],
            coping_patterns=[],
            specific_triggers=[],
            risk_level='low',
            recommended_actions=[]
        )

        # DASS21 question mappings
        question_mappings = {
            'depression': {
                'q3': 'I couldn\'t seem to experience any positive feeling at all',
                'q5': 'I found it difficult to work up the initiative to do things',
                'q10': 'I felt that I had nothing to look forward to',
                'q13': 'I felt down-hearted and blue',
                'q16': 'I was unable to become enthusiastic about anything',
                'q17': 'I felt I wasn\'t worth much as a person',
                'q21': 'I felt that life was meaningless'
            },
            'anxiety': {
                'q2': 'I was aware of dryness of my mouth',
                'q4': 'I experienced breathing difficulty',
                'q7': 'I experienced trembling',
                'q9': 'I was worried about situations in which I might panic',
                'q15': 'I felt I was close to panic',
                'q19': 'I was aware of the action of my heart',
                'q20': 'I felt scared without any good reason'
            },
            'stress': {
                'q1': 'I found it hard to wind down',
                'q6': 'I tended to over-react to situations',
                'q8': 'I felt that I was using a lot of nervous energy',
                'q11': 'I found myself getting agitated',
                'q12': 'I found it difficult to relax',
                'q14': 'I was intolerant of anything that kept me from getting on with what I was doing',
                'q18': 'I felt that I was rather touchy'
            }
        }

        # Analyze each dimension
        for dimension, questions in question_mappings.items():
            for q_id, question in questions.items():
                if q_id in answers:
                    score = answers[q_id]
                    if score >= 2:  # Moderate to severe response
                        symptom_data = {
                            'question': question,
                            'score': score,
                            'severity': 'moderate' if score == 2 else 'severe'
                        }

                        if dimension == 'depression':
                            analysis.depression_symptoms.append(symptom_data)
                        elif dimension == 'anxiety':
                            analysis.anxiety_symptoms.append(symptom_data)
                        elif dimension == 'stress':
                            analysis.stress_symptoms.append(symptom_data)

        # Identify primary concerns
        all_symptoms = (analysis.depression_symptoms +
                       analysis.anxiety_symptoms +
                       analysis.stress_symptoms)

        if all_symptoms:
            all_symptoms.sort(key=lambda x: (x['severity'] == 'severe', x['score']), reverse=True)
            analysis.primary_concerns = all_symptoms[:3]

        # Analyze coping patterns
        coping_indicators = {
            'q1': 'difficulty relaxing',
            'q12': 'relaxation challenges',
            'q6': 'emotional reactivity',
            'q18': 'sensitivity to criticism'
        }

        for q_id, pattern in coping_indicators.items():
            if q_id in answers and answers[q_id] >= 2:
                analysis.coping_patterns.append(pattern)

        # Identify specific triggers
        trigger_indicators = {
            'q9': 'social situations',
            'q15': 'panic attacks',
            'q5': 'motivation challenges',
            'q17': 'self-esteem issues'
        }

        for q_id, trigger in trigger_indicators.items():
            if q_id in answers and answers[q_id] >= 2:
                analysis.specific_triggers.append(trigger)

        # Determine risk level
        max_score = max(depression, anxiety, stress)
        if max_score >= 21:  # Severe range
            analysis.risk_level = 'high'
        elif max_score >= 14:  # Moderate range
            analysis.risk_level = 'moderate'
        else:
            analysis.risk_level = 'low'

        # Generate recommended actions based on risk level
        analysis.recommended_actions = self._generate_recommended_actions(
            analysis.risk_level, analysis.primary_concerns, analysis.coping_patterns
        )

        return analysis

    def _generate_recommended_actions(self, risk_level: str,
                                    primary_concerns: List[Dict[str, Any]],
                                    coping_patterns: List[str]) -> List[str]:
        """Generate recommended actions based on analysis"""
        actions = []

        if risk_level == 'high':
            actions.extend([
                "Consider scheduling an appointment with a counselor",
                "Reach out to a trusted friend or family member",
                "Practice grounding techniques when feeling overwhelmed"
            ])
        elif risk_level == 'moderate':
            actions.extend([
                "Try relaxation exercises daily",
                "Maintain regular sleep and eating patterns",
                "Consider talking to a counselor for additional support"
            ])
        else:
            actions.extend([
                "Continue practicing good self-care habits",
                "Stay connected with your support network",
                "Consider preventive mental health strategies"
            ])

        # Add specific actions based on concerns
        for concern in primary_concerns[:2]:  # Top 2 concerns
            if 'positive feeling' in concern['question'].lower():
                actions.append("Try activities that usually bring you joy, even for short periods")
            elif 'initiative' in concern['question'].lower():
                actions.append("Break tasks into small, manageable steps")
            elif 'panic' in concern['question'].lower():
                actions.append("Practice deep breathing exercises when feeling anxious")

        return actions[:5]  # Limit to 5 actions

    def _analyze_dass_trends(self, results: List[DASSResult]) -> Dict[str, str]:
        """Analyze trends in DASS scores"""
        if len(results) < 2:
            return None

        trends = {}
        for dimension in ['depression', 'anxiety', 'stress']:
            scores = [getattr(result, f'{dimension}_score') for result in results]
            if len(scores) >= 2:
                change = scores[0] - scores[-1]  # Most recent - oldest
                if change > 3:
                    trends[dimension] = 'improving'
                elif change < -3:
                    trends[dimension] = 'worsening'
                else:
                    trends[dimension] = 'stable'

        return trends

    def _get_academic_context(self, user: CustomUser) -> Dict[str, Any]:
        """Get academic context for personalization"""
        context = {}

        # College-specific stressors
        college_stressors = {
            'CASS': 'arts and humanities coursework, creative projects, and social sciences research',
            'CEN': 'engineering projects, technical coursework, and problem-solving challenges',
            'CBA': 'business case studies, financial analysis, and professional development',
            'COF': 'fieldwork, laboratory work, and environmental studies',
            'CAG': 'agricultural research, fieldwork, and sustainability projects',
            'CHSI': 'home economics projects, industry applications, and practical skills',
            'CED': 'teaching practicums, educational research, and classroom management',
            'COS': 'scientific research, laboratory work, and mathematical analysis',
            'CVSM': 'veterinary clinical work, animal care, and medical studies'
        }

        if hasattr(user, 'college') and user.college:
            context['college_stressors'] = college_stressors.get(user.college, 'academic coursework')

        # Year-level specific challenges
        year_challenges = {
            '1': 'adjusting to university life, building study habits, and making new friends',
            '2': 'increasing academic workload, choosing specializations, and career exploration',
            '3': 'advanced coursework, research projects, and internship preparation',
            '4': 'thesis work, career preparation, and transition to professional life'
        }

        if hasattr(user, 'year_level') and user.year_level:
            context['year_challenges'] = year_challenges.get(user.year_level, 'academic development')

        # Age-specific considerations
        if hasattr(user, 'age') and user.age:
            if user.age < 20:
                context['age_context'] = 'young adult transitioning to independence'
            elif user.age < 25:
                context['age_context'] = 'emerging adult navigating career and personal development'
            else:
                context['age_context'] = 'adult learner balancing multiple responsibilities'

        return context

    def _analyze_exercise_preferences(self, relaxation_logs: List[RelaxationLog]) -> Optional[Dict[str, Any]]:
        """Analyze user's relaxation exercise preferences"""
        if not relaxation_logs:
            return None

        exercise_counts = {}
        for log in relaxation_logs:
            exercise_type = log.exercise_type
            exercise_counts[exercise_type] = exercise_counts.get(exercise_type, 0) + 1

        if exercise_counts:
            preferred_exercise = max(exercise_counts, key=exercise_counts.get)
            return {
                'preferred_exercise': preferred_exercise,
                'total_sessions': len(relaxation_logs),
                'exercise_counts': exercise_counts
            }

        return None

    def _generate_structured_feedback(self, user: CustomUser, dass_data: Dict[str, Any],
                                    user_context: UserContext, dass_analysis: DASSAnalysis) -> Dict[str, Any]:
        """Generate structured feedback with separate sections for key concerns and main feedback"""
        if not self.openai_available:
            return {
                'acknowledgment': self._generate_acknowledgment_section(user, dass_data, dass_analysis),
                'key_concerns': self._generate_key_concerns_section(dass_analysis),
                'main_feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'actionable_steps': self._generate_actionable_steps_section(dass_analysis),
                'full_feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'source': 'fallback'
            }

        try:
            # Generate acknowledgment section
            acknowledgment = self._generate_acknowledgment_section(user, dass_data, dass_analysis)

            # Generate key concerns section
            key_concerns = self._generate_key_concerns_section(dass_analysis)

            # Generate main feedback
            main_feedback_result = self._generate_personalized_feedback(user, dass_data, user_context, dass_analysis)

            # Generate actionable steps
            actionable_steps = self._generate_actionable_steps_section(dass_analysis)

            # Combine into full feedback
            full_feedback = f"{acknowledgment}\n\n{key_concerns}\n\n{main_feedback_result['feedback']}\n\n{actionable_steps}"

            return {
                'acknowledgment': acknowledgment,
                'key_concerns': key_concerns,
                'main_feedback': main_feedback_result['feedback'],
                'actionable_steps': actionable_steps,
                'full_feedback': full_feedback,
                'source': main_feedback_result['source']
            }

        except Exception as e:
            logger.error(f"Structured feedback generation failed for user {user.id}: {str(e)}")
            return {
                'acknowledgment': self._generate_acknowledgment_section(user, dass_data, dass_analysis),
                'key_concerns': self._generate_key_concerns_section(dass_analysis),
                'main_feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'actionable_steps': self._generate_actionable_steps_section(dass_analysis),
                'full_feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'source': 'fallback'
            }

    def _generate_acknowledgment_section(self, user: CustomUser, dass_data: Dict[str, Any],
                                       dass_analysis: DASSAnalysis) -> str:
        """Generate acknowledgment section for key concerns"""
        acknowledgment_parts = []

        # Acknowledge the assessment completion
        acknowledgment_parts.append("Thank you for completing the DASS21 assessment. I understand this takes courage and self-awareness.")

        # Acknowledge their specific scores
        depression_severity = dass_data.get('depression_severity', 'normal')
        anxiety_severity = dass_data.get('anxiety_severity', 'normal')
        stress_severity = dass_data.get('stress_severity', 'normal')

        scores_summary = []
        if depression_severity != 'normal':
            scores_summary.append(f"depression in the {depression_severity} range")
        if anxiety_severity != 'normal':
            scores_summary.append(f"anxiety in the {anxiety_severity} range")
        if stress_severity != 'normal':
            scores_summary.append(f"stress in the {stress_severity} range")

        if scores_summary:
            acknowledgment_parts.append(f"Your results indicate {', '.join(scores_summary)}.")

        return " ".join(acknowledgment_parts)

    def _generate_key_concerns_section(self, dass_analysis: DASSAnalysis) -> str:
        """Generate key concerns section"""
        if not dass_analysis.primary_concerns:
            return "Based on your responses, you're managing well overall with no significant concerns identified."

        concerns_text = ["Based on your responses, here are the key areas that stood out:"]

        for i, concern in enumerate(dass_analysis.primary_concerns[:3], 1):
            severity_desc = "significantly" if concern['severity'] == 'severe' else "moderately"
            concerns_text.append(f"{i}. {concern['question']} ({severity_desc})")

        if dass_analysis.coping_patterns:
            concerns_text.append(f"\nCoping patterns identified: {', '.join(dass_analysis.coping_patterns)}.")

        if dass_analysis.specific_triggers:
            concerns_text.append(f"Potential triggers: {', '.join(dass_analysis.specific_triggers)}.")

        return "\n".join(concerns_text)

    def _generate_actionable_steps_section(self, dass_analysis: DASSAnalysis) -> str:
        """Generate actionable steps section"""
        steps = ["Here are some immediate steps you can take today:"]

        # Add risk-level specific actions
        if dass_analysis.risk_level == 'high':
            steps.extend([
                "• Contact your university counseling center for professional support",
                "• Reach out to a trusted friend or family member to talk about how you're feeling",
                "• Practice grounding techniques: name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste"
            ])
        elif dass_analysis.risk_level == 'moderate':
            steps.extend([
                "• Schedule a relaxation session using your preferred exercise technique",
                "• Break your next academic task into 3 smaller, manageable steps",
                "• Set aside 10 minutes for a short walk or deep breathing exercise"
            ])
        else:
            steps.extend([
                "• Continue your current self-care practices that are working well",
                "• Try one new relaxation technique this week",
                "• Maintain regular social connections with friends or study groups"
            ])

        # Add concern-specific actions
        for concern in dass_analysis.primary_concerns[:2]:
            if 'positive feeling' in concern['question'].lower():
                steps.append("• Start with 5 minutes of an activity you usually enjoy")
            elif 'initiative' in concern['question'].lower():
                steps.append("• Choose the smallest possible first step for your next task")
            elif 'panic' in concern['question'].lower():
                steps.append("• Practice the 4-7-8 breathing technique when feeling anxious")
            elif 'relax' in concern['question'].lower():
                steps.append("• Try progressive muscle relaxation for 5 minutes")

        return "\n".join(steps)

    def _generate_tips_box(self, user: CustomUser, dass_data: Dict[str, Any],
                          user_context: UserContext, dass_analysis: DASSAnalysis) -> Dict[str, Any]:
        """Generate tips in a separate box/section after key concerns"""
        # Check if tips should be generated
        moderate_normal_severities = ['normal', 'mild', 'moderate']
        has_moderate_normal = (
            dass_data.get('depression_severity') in moderate_normal_severities or
            dass_data.get('anxiety_severity') in moderate_normal_severities or
            dass_data.get('stress_severity') in moderate_normal_severities
        )

        if not has_moderate_normal:
            return {
                'tips_content': None,
                'tips_title': None,
                'source': 'not_generated',
                'reason': 'high_severity_scores'
            }

        if not self.openai_available:
            return {
                'tips_content': self._generate_fallback_tips(user, dass_data, user_context, dass_analysis),
                'tips_title': '💡 Additional Tips for Wellness',
                'source': 'fallback',
                'generated_for': 'moderate_normal'
            }

        try:
            prompt = self._build_tips_prompt(user, dass_data, user_context, dass_analysis)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive mental health assistant specializing in university student wellness. Provide practical, evidence-based tips for maintaining mental health and preventing escalation of symptoms."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7,
            )

            tips = response.choices[0].message['content'].strip()
            return {
                'tips_content': tips,
                'tips_title': '💡 Additional Tips for Wellness',
                'source': 'openai',
                'generated_for': 'moderate_normal'
            }

        except Exception as e:
            logger.error(f"Tips box generation failed for user {user.id}: {str(e)}")
            return {
                'tips_content': self._generate_fallback_tips(user, dass_data, user_context, dass_analysis),
                'tips_title': '💡 Additional Tips for Wellness',
                'source': 'fallback',
                'generated_for': 'moderate_normal'
            }

    def _generate_personalized_feedback(self, user: CustomUser, dass_data: Dict[str, Any],
                                      user_context: UserContext, dass_analysis: DASSAnalysis) -> Dict[str, Any]:
        """Generate personalized AI feedback"""
        if not self.openai_available:
            return {
                'feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'source': 'fallback'
            }

        try:
            prompt = self._build_enhanced_prompt(user, dass_data, user_context, dass_analysis)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7,
            )

            feedback = response.choices[0].message['content'].strip()
            logger.info(f"Personalized AI feedback generated for user {user.id}")

            return {
                'feedback': feedback,
                'source': 'openai'
            }

        except Exception as e:
            logger.error(f"OpenAI feedback generation failed for user {user.id}: {str(e)}")
            return {
                'feedback': self._generate_fallback_feedback(user, dass_data, user_context, dass_analysis),
                'source': 'fallback'
            }

    def _build_enhanced_prompt(self, user: CustomUser, dass_data: Dict[str, Any],
                              user_context: UserContext, dass_analysis: DASSAnalysis) -> str:
        """Build enhanced personalized prompt for AI feedback"""
        prompt_parts = []

        # Basic scores
        prompt_parts.append(f"A university student has completed the DASS21 test with scores: "
                          f"Depression: {dass_data['depression']} ({dass_data.get('depression_severity', 'unknown')}), "
                          f"Anxiety: {dass_data['anxiety']} ({dass_data.get('anxiety_severity', 'unknown')}), "
                          f"Stress: {dass_data['stress']} ({dass_data.get('stress_severity', 'unknown')}).")

        # Specific concerns
        if dass_analysis.primary_concerns:
            prompt_parts.append("Key concerns from their responses:")
            for i, concern in enumerate(dass_analysis.primary_concerns[:3], 1):
                prompt_parts.append(f"{i}. {concern['question']} (severity: {concern['severity']})")

        # Coping patterns and triggers
        if dass_analysis.coping_patterns:
            prompt_parts.append(f"Coping challenges: {', '.join(dass_analysis.coping_patterns)}.")

        if dass_analysis.specific_triggers:
            prompt_parts.append(f"Specific triggers: {', '.join(dass_analysis.specific_triggers)}.")

        # Personalization context
        context_parts = []

        # Academic context
        if user_context.academic_context:
            context = user_context.academic_context
            if 'college_stressors' in context:
                context_parts.append(f"Student is in {user.get_college_display()} facing {context['college_stressors']}.")
            if 'year_challenges' in context:
                context_parts.append(f"As a {user.get_year_level_display()} student, they're dealing with {context['year_challenges']}.")

        # Test history and trends
        if user_context.test_count > 1:
            context_parts.append(f"This is their {user_context.test_count}th DASS21 assessment.")
            if user_context.trend_analysis:
                trends = user_context.trend_analysis
                trend_desc = []
                for dimension, trend in trends.items():
                    if trend == 'improving':
                        trend_desc.append(f"{dimension} scores are improving")
                    elif trend == 'worsening':
                        trend_desc.append(f"{dimension} scores are worsening")
                if trend_desc:
                    context_parts.append(f"Trend analysis shows: {', '.join(trend_desc)}.")

        # Exercise preferences
        if user_context.exercise_preferences:
            pref = user_context.exercise_preferences
            context_parts.append(f"They've completed {pref['total_sessions']} relaxation sessions, preferring {pref['preferred_exercise']}.")

        # Appointment history
        if user_context.appointment_history:
            recent_appts = [appt for appt in user_context.appointment_history if appt.status == 'completed']
            if recent_appts:
                context_parts.append(f"They've completed {len(recent_appts)} counseling sessions recently.")

        if context_parts:
            prompt_parts.append("Personal context: " + " ".join(context_parts))

        # Gender context
        if hasattr(user, 'gender') and user.gender and user.gender != 'Prefer not to say':
            prompt_parts.append(f"The student identifies as {user.gender.lower()}.")

        # Risk level and recommended actions
        prompt_parts.append(f"Risk assessment: {dass_analysis.risk_level} risk level.")
        if dass_analysis.recommended_actions:
            prompt_parts.append("Recommended actions: " + "; ".join(dass_analysis.recommended_actions[:3]))

        # Final instructions
        prompt_parts.append("""
Provide a personalized, empathetic feedback message (4-6 sentences) that:
1. Acknowledges their specific DASS21 responses and concerns
2. References their academic/personal context and history
3. Addresses their specific coping challenges and triggers
4. Provides specific, actionable advice based on their risk level
5. Suggests relevant resources or coping strategies
6. Maintains a supportive, encouraging tone
7. Includes concrete next steps they can take today

Highlight actionable advice in <b>bold</b> HTML tags.
Structure the response with: acknowledgment, context-specific advice, actionable steps, encouragement.
Do not mention AI or that this is automated.
Make the feedback feel like it's coming from someone who understands their specific symptoms and challenges.
""")

        return " ".join(prompt_parts)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI feedback generation"""
        return """You are a supportive, personalized mental health assistant for university students.
You have extensive knowledge of mental health, DASS21 assessment, and university student challenges.
Provide empathetic, actionable advice tailored to the student's specific DASS21 responses, academic context, and mental health journey.
Always maintain a warm, encouraging tone and provide concrete, actionable steps based on their specific symptoms.
Focus on validation, practical strategies, and appropriate professional referrals when needed."""

    def _generate_fallback_feedback(self, user: CustomUser, dass_data: Dict[str, Any],
                                  user_context: UserContext, dass_analysis: DASSAnalysis) -> str:
        """Generate fallback feedback when OpenAI is unavailable"""
        feedback_parts = []

        # Address specific concerns
        if dass_analysis.primary_concerns:
            primary_concern = dass_analysis.primary_concerns[0]
            if 'positive feeling' in primary_concern['question'].lower():
                feedback_parts.append("I notice you're having difficulty experiencing positive feelings. <b>Try starting with small activities you once enjoyed, even if just for 5 minutes each day.</b>")
            elif 'initiative' in primary_concern['question'].lower():
                feedback_parts.append("You mentioned struggling with motivation and initiative. <b>Break tasks into tiny steps and celebrate each small completion.</b>")
            elif 'panic' in primary_concern['question'].lower():
                feedback_parts.append("I see you're experiencing panic-related concerns. <b>Practice the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.</b>")
            elif 'worth' in primary_concern['question'].lower():
                feedback_parts.append("You're feeling down about your self-worth. <b>Remember that your value isn't determined by your current struggles.</b>")
            elif 'relax' in primary_concern['question'].lower():
                feedback_parts.append("You're finding it hard to relax. <b>Try progressive muscle relaxation: tense and release each muscle group for 5 seconds.</b>")

        # Address coping patterns
        if 'difficulty relaxing' in dass_analysis.coping_patterns:
            feedback_parts.append("<b>For relaxation challenges, try setting aside 10 minutes daily for deep breathing or guided meditation.</b>")
        if 'emotional reactivity' in dass_analysis.coping_patterns:
            feedback_parts.append("<b>When feeling overwhelmed, try the 'STOP' technique: Stop, Take a breath, Observe your thoughts, Proceed mindfully.</b>")

        # Academic context
        if user_context.academic_context:
            context = user_context.academic_context
            if 'college_stressors' in context:
                feedback_parts.append(f"As a {user.get_college_display()} student, you're navigating {context['college_stressors']}.")
            if 'year_challenges' in context:
                feedback_parts.append(f"Being a {user.get_year_level_display()} student brings {context['year_challenges']}.")

        # Trend-based feedback
        if user_context.trend_analysis:
            trends = user_context.trend_analysis
            improving = [dim for dim, trend in trends.items() if trend == 'improving']
            if improving:
                feedback_parts.append(f"It's encouraging to see improvement in your {', '.join(improving)} scores. <b>Continue the strategies that have been working for you.</b>")

        # Score-based feedback
        depression_severity = dass_data.get('depression_severity', 'normal')
        anxiety_severity = dass_data.get('anxiety_severity', 'normal')
        stress_severity = dass_data.get('stress_severity', 'normal')

        if depression_severity in ['moderate', 'severe', 'extremely-severe']:
            feedback_parts.append("Your depression scores suggest significant emotional challenges. <b>Consider reaching out to a counselor or mental health professional for support.</b> <b>Try to maintain a regular sleep schedule and engage in activities you once enjoyed, even if it's just for a few minutes each day.</b>")
        elif depression_severity == 'mild':
            feedback_parts.append("You're showing some signs of depression. <b>Try engaging in activities you usually enjoy and maintain regular social connections.</b> <b>Consider setting small, achievable goals for each day to help build momentum.</b>")

        if anxiety_severity in ['moderate', 'severe', 'extremely-severe']:
            feedback_parts.append("Your anxiety levels appear elevated. <b>Practice deep breathing exercises and consider talking to a counselor about your concerns.</b> <b>Try the 4-7-8 breathing technique: inhale for 4 counts, hold for 7, exhale for 8.</b>")
        elif anxiety_severity == 'mild':
            feedback_parts.append("You're experiencing some anxiety. <b>Try mindfulness techniques and regular exercise to help manage stress.</b> <b>Consider taking short breaks during study sessions to prevent overwhelm.</b>")

        if stress_severity in ['moderate', 'severe', 'extremely-severe']:
            feedback_parts.append("Your stress levels are quite high. <b>Prioritize self-care activities and consider seeking professional support to develop coping strategies.</b> <b>Try breaking large tasks into smaller, manageable steps and celebrate each completion.</b>")
        elif stress_severity == 'mild':
            feedback_parts.append("You're experiencing some stress. <b>Try time management techniques and regular breaks to maintain balance.</b> <b>Consider using a planner to organize your academic and personal responsibilities.</b>")

        # Exercise recommendations
        if user_context.exercise_preferences:
            pref = user_context.exercise_preferences
            if pref['preferred_exercise'] == 'PMR':
                feedback_parts.append("<b>Consider using Progressive Muscle Relaxation, which you've found helpful before.</b> <b>Try a 10-minute PMR session before studying or before bed.</b>")
            elif pref['preferred_exercise'] == 'EFT':
                feedback_parts.append("<b>Try Emotional Freedom Technique tapping, which has worked well for you in the past.</b> <b>Use EFT when you feel overwhelmed or before important academic tasks.</b>")
            elif pref['preferred_exercise'] == 'Breathing':
                feedback_parts.append("<b>Your breathing exercises have been effective.</b> <b>Try box breathing: 4 counts in, 4 hold, 4 out, 4 hold, repeat for 5 minutes.</b>")

        # College-specific advice
        if user_context.academic_context:
            context = user_context.academic_context
            if 'college_stressors' in context:
                if 'engineering' in context['college_stressors'].lower():
                    feedback_parts.append("<b>For technical coursework stress, try the Pomodoro Technique: 25 minutes of focused work followed by a 5-minute break.</b>")
                elif 'business' in context['college_stressors'].lower():
                    feedback_parts.append("<b>For case study stress, try discussing complex topics with classmates to gain different perspectives.</b>")
                elif 'arts' in context['college_stressors'].lower():
                    feedback_parts.append("<b>For creative projects, try free-writing or sketching to unlock creative blocks.</b>")

        # Year-level specific advice
        if user_context.academic_context:
            context = user_context.academic_context
            if 'year_challenges' in context:
                if '1st' in context['year_challenges']:
                    feedback_parts.append("<b>As a first-year student, focus on building good study habits and finding your support network.</b>")
                elif '4th' in context['year_challenges']:
                    feedback_parts.append("<b>As a graduating student, remember to celebrate your achievements while managing thesis stress.</b>")

        # General encouragement
        if not feedback_parts:
            feedback_parts.append("Your scores are within normal ranges. <b>Continue practicing good mental health habits and reach out for support if needed.</b> <b>Consider maintaining a gratitude journal to track positive moments.</b>")

        return " ".join(feedback_parts)



    def _build_tips_prompt(self, user: CustomUser, dass_data: Dict[str, Any],
                          user_context: UserContext, dass_analysis: DASSAnalysis) -> str:
        """Build prompt for mental health tips generation"""
        prompt_parts = []

        prompt_parts.append(f"Generate 5-7 practical, actionable mental health tips for a university student with DASS21 scores: "
                          f"Depression: {dass_data['depression']} ({dass_data.get('depression_severity', 'unknown')}), "
                          f"Anxiety: {dass_data['anxiety']} ({dass_data.get('anxiety_severity', 'unknown')}), "
                          f"Stress: {dass_data['stress']} ({dass_data.get('stress_severity', 'unknown')}).")

        # Add specific concerns
        if dass_analysis.primary_concerns:
            prompt_parts.append("Key concerns from their responses:")
            for concern in dass_analysis.primary_concerns[:3]:
                prompt_parts.append(f"- {concern['question']}")

        # Add personalization
        if user_context.academic_context:
            context = user_context.academic_context
            if 'college_stressors' in context:
                prompt_parts.append(f"Academic context: Student is in {user.get_college_display()} facing {context['college_stressors']}.")
            if 'year_challenges' in context:
                prompt_parts.append(f"As a {user.get_year_level_display()} student, they're dealing with {context['year_challenges']}.")

        # Add exercise preferences
        if user_context.exercise_preferences:
            pref = user_context.exercise_preferences
            prompt_parts.append(f"They've completed {pref['total_sessions']} relaxation sessions, preferring {pref['preferred_exercise']}.")

        prompt_parts.append("""
Generate tips that are:
1. Specific to their DASS21 scores and concerns
2. Tailored to university student life
3. Practical and immediately actionable
4. Focused on prevention and maintenance for moderate/normal mental health
5. Include a mix of academic, social, and self-care strategies
6. Number them 1-7 and keep each tip concise (1-2 sentences)
7. Use encouraging, supportive language
8. Avoid medical advice or diagnosis
Format as a bulleted list with <b>bold</b> key actions.
""")

        return " ".join(prompt_parts)

    def _generate_fallback_tips(self, user: CustomUser, dass_data: Dict[str, Any],
                               user_context: UserContext, dass_analysis: DASSAnalysis) -> str:
        """Generate fallback tips when OpenAI is unavailable"""
        tips = []

        depression_severity = dass_data.get('depression_severity', 'normal')
        anxiety_severity = dass_data.get('anxiety_severity', 'normal')
        stress_severity = dass_data.get('stress_severity', 'normal')

        # Depression tips
        if depression_severity in ['mild', 'moderate', 'normal']:
            tips.extend([
                "1. <b>Maintain a consistent sleep schedule</b> of 7-9 hours per night to support emotional regulation.",
                "2. <b>Practice daily gratitude</b> by noting 3 things you're thankful for each evening.",
                "3. <b>Stay connected with friends</b> through regular social activities, even small ones like coffee chats."
            ])

        # Anxiety tips
        if anxiety_severity in ['mild', 'moderate', 'normal']:
            tips.extend([
                "4. <b>Use the 4-7-8 breathing technique</b>: inhale for 4 counts, hold for 7, exhale for 8 when feeling anxious.",
                "5. <b>Break tasks into smaller steps</b> to reduce overwhelm and build momentum.",
                "6. <b>Practice progressive muscle relaxation</b> for 10 minutes daily to release physical tension."
            ])

        # Stress tips
        if stress_severity in ['mild', 'moderate', 'normal']:
            tips.extend([
                "7. <b>Try the Pomodoro Technique</b>: 25 minutes focused work followed by 5-minute breaks.",
                "8. <b>Incorporate short walks</b> between classes to clear your mind and reduce stress.",
                "9. <b>Set boundaries</b> around study time and leisure time to maintain work-life balance."
            ])

        # Academic-specific tips
        if user_context.academic_context:
            context = user_context.academic_context
            if 'college_stressors' in context:
                if 'engineering' in context['college_stressors'].lower():
                    tips.append("10. <b>For technical coursework</b>, schedule regular review sessions to prevent last-minute stress.")
                elif 'business' in context['college_stressors'].lower():
                    tips.append("10. <b>For case studies</b>, try discussing complex topics with classmates to gain different perspectives.")
                elif 'arts' in context['college_stressors'].lower():
                    tips.append("10. <b>For creative projects</b>, try free-writing or sketching to unlock creative blocks.")

        # Year-level specific advice
        if user_context.academic_context:
            context = user_context.academic_context
            if 'year_challenges' in context:
                if '1st' in context['year_challenges']:
                    tips.append("11. <b>As a first-year student</b>, focus on building good study habits and finding your support network.")
                elif '4th' in context['year_challenges']:
                    tips.append("11. <b>As a graduating student</b>, remember to celebrate your achievements while managing thesis stress.")

        return "\n".join(tips)

    def _serialize_dass_analysis(self, analysis: DASSAnalysis) -> Dict[str, Any]:
        """Serialize DASS analysis for JSON response"""
        return {
            'depression_symptoms': analysis.depression_symptoms,
            'anxiety_symptoms': analysis.anxiety_symptoms,
            'stress_symptoms': analysis.stress_symptoms,
            'primary_concerns': analysis.primary_concerns,
            'coping_patterns': analysis.coping_patterns,
            'specific_triggers': analysis.specific_triggers,
            'risk_level': analysis.risk_level,
            'recommended_actions': analysis.recommended_actions
        }

    def _get_context_summary(self, user_context: UserContext) -> Dict[str, Any]:
        """Get summary of context used for personalization"""
        return {
            'test_count': user_context.test_count,
            'has_trend_analysis': user_context.trend_analysis is not None,
            'has_academic_context': user_context.academic_context is not None,
            'has_exercise_preferences': user_context.exercise_preferences is not None,
            'appointment_count': len(user_context.appointment_history),
            'feedback_count': len(user_context.feedback_history)
        }

    def _generate_fallback_response(self, user: CustomUser, dass_data: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Generate fallback response when main generation fails"""
        logger.warning(f"Using fallback response for user {user.id}: {error}")

        # Create basic analysis for fallback
        basic_analysis = DASSAnalysis(
            depression_symptoms=[],
            anxiety_symptoms=[],
            stress_symptoms=[],
            primary_concerns=[],
            coping_patterns=[],
            specific_triggers=[],
            risk_level='low',
            recommended_actions=["Consider talking to a counselor", "Practice daily relaxation"]
        )

        basic_context = UserContext(
            test_count=1,
            trend_analysis=None,
            academic_context=None,
            exercise_preferences=None,
            recent_results=[],
            appointment_history=[],
            feedback_history=[]
        )

        return {
            'success': False,
            'feedback': self._generate_fallback_feedback(user, dass_data, basic_context, basic_analysis),
            'tips': None,
            'source': 'fallback',
            'personalization_level': 'basic',
            'dass_analysis': self._serialize_dass_analysis(basic_analysis),
            'context_used': self._get_context_summary(basic_context),
            'risk_assessment': basic_analysis.risk_level,
            'recommended_actions': basic_analysis.recommended_actions
        }
