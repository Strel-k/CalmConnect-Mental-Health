#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor, CustomUser, Appointment, Feedback
from django.db.models import Avg

def test_counselor_ratings():
    """Test counselor rating calculations"""
    print("🧪 Testing counselor rating calculations...")
    
    # Get a counselor
    counselor = Counselor.objects.first()
    if not counselor:
        print("❌ No counselors found in database")
        return
    
    print(f"👨‍⚕️ Testing ratings for counselor: {counselor.name}")
    
    # Calculate feedback statistics
    feedbacks = Feedback.objects.filter(counselor=counselor, skipped=False)
    total_feedbacks = feedbacks.count()
    
    print(f"📊 Total feedbacks: {total_feedbacks}")
    
    if total_feedbacks > 0:
        # Calculate average ratings
        avg_overall = feedbacks.aggregate(avg=Avg('overall_rating'))['avg'] or 0
        avg_professionalism = feedbacks.aggregate(avg=Avg('professionalism_rating'))['avg'] or 0
        avg_helpfulness = feedbacks.aggregate(avg=Avg('helpfulness_rating'))['avg'] or 0
        avg_recommend = feedbacks.aggregate(avg=Avg('recommend_rating'))['avg'] or 0
        
        # Calculate overall average rating
        overall_avg = 0
        if total_feedbacks > 0:
            total_rating = avg_overall + avg_professionalism + avg_helpfulness + avg_recommend
            overall_avg = round(total_rating / 4, 1)
        
        print(f"⭐ Overall Average: {overall_avg}")
        print(f"📈 Individual Ratings:")
        print(f"   - Overall: {avg_overall:.1f}")
        print(f"   - Professionalism: {avg_professionalism:.1f}")
        print(f"   - Helpfulness: {avg_helpfulness:.1f}")
        print(f"   - Recommendation: {avg_recommend:.1f}")
        
        # Show some sample feedback
        print(f"\n📝 Sample feedback entries:")
        for i, feedback in enumerate(feedbacks[:3]):
            print(f"   {i+1}. Overall: {feedback.overall_rating}, "
                  f"Professionalism: {feedback.professionalism_rating}, "
                  f"Helpfulness: {feedback.helpfulness_rating}, "
                  f"Recommend: {feedback.recommend_rating}")
            if feedback.positive_feedback:
                print(f"      Positive: {feedback.positive_feedback[:50]}...")
    else:
        print("📝 No feedback found for this counselor")
        
                # Create some test feedback
        print("🔧 Creating test feedback...")
        user = CustomUser.objects.first()
        if user:
            # Find an appointment for this counselor
            appointment = Appointment.objects.filter(counselor=counselor).first()
            if appointment:
                # Create test feedback
                feedback = Feedback.objects.create(
                    counselor=counselor,
                    user=user,
                    appointment=appointment,
                    overall_rating=4.5,
                    professionalism_rating=4.0,
                    helpfulness_rating=4.5,
                    recommend_rating=5.0,
                    positive_feedback="Great session, very helpful!",
                    improvement_feedback="Could be a bit more punctual",
                    additional_comments="Overall excellent experience",
                    skipped=False
                )
                print(f"✅ Created test feedback with ID: {feedback.id}")
            else:
                print("❌ No appointments found for this counselor")
                return
            
            # Recalculate ratings
            feedbacks = Feedback.objects.filter(counselor=counselor, skipped=False)
            total_feedbacks = feedbacks.count()
            avg_overall = feedbacks.aggregate(avg=Avg('overall_rating'))['avg'] or 0
            avg_professionalism = feedbacks.aggregate(avg=Avg('professionalism_rating'))['avg'] or 0
            avg_helpfulness = feedbacks.aggregate(avg=Avg('helpfulness_rating'))['avg'] or 0
            avg_recommend = feedbacks.aggregate(avg=Avg('recommend_rating'))['avg'] or 0
            
            total_rating = avg_overall + avg_professionalism + avg_helpfulness + avg_recommend
            overall_avg = round(total_rating / 4, 1)
            
            print(f"📊 Updated ratings:")
            print(f"   - Total feedbacks: {total_feedbacks}")
            print(f"   - Overall average: {overall_avg}")
            print(f"   - Individual averages: {avg_overall:.1f}, {avg_professionalism:.1f}, {avg_helpfulness:.1f}, {avg_recommend:.1f}")
        else:
            print("❌ No users found to create test feedback")

if __name__ == "__main__":
    test_counselor_ratings() 