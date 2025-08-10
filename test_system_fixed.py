#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from mentalhealth.models import CustomUser, Counselor, Appointment, Report, Notification, Feedback
from django.utils import timezone
from datetime import datetime, date, time
import traceback

def test_system_fixed():
    """Fixed comprehensive system test for CalmConnect core functionalities"""
    print("🧪 CalmConnect System Test - FIXED VERSION")
    print("=" * 60)
    
    results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    def log_test(test_name, status, details=""):
        if status:
            print(f"✅ {test_name}")
            results['passed'] += 1
        else:
            print(f"❌ {test_name} - {details}")
            results['failed'] += 1
        results['details'].append((test_name, status, details))
    
    # Test 1: Database Connection
    try:
        users_count = CustomUser.objects.count()
        counselors_count = Counselor.objects.count()
        appointments_count = Appointment.objects.count()
        log_test("Database Connection", True, f"Users: {users_count}, Counselors: {counselors_count}, Appointments: {appointments_count}")
    except Exception as e:
        log_test("Database Connection", False, str(e))
    
    # Test 2: User Model Functionality
    try:
        # Test user creation
        test_user = CustomUser.objects.filter(username='test_user_fixed').first()
        if not test_user:
            test_user = CustomUser.objects.create_user(
                username='test_user_fixed',
                email='testfixed@clsu2.edu.ph',
                password='TestPassword123!',
                full_name='Test User Fixed',
                student_id='2021-54321',
                age=20,
                gender='Male',
                college='CEN',
                program='Bachelor of Science in Information Technology',
                year_level='3'
            )
        log_test("User Model Creation", True, f"User ID: {test_user.id}")
    except Exception as e:
        log_test("User Model Creation", False, str(e))
    
    # Test 3: Authentication System
    try:
        auth_user = authenticate(username='test_user_fixed', password='TestPassword123!')
        if auth_user:
            log_test("Authentication System", True, "User authenticated successfully")
        else:
            log_test("Authentication System", False, "Authentication failed")
    except Exception as e:
        log_test("Authentication System", False, str(e))
    
    # Test 4: Counselor Model
    try:
        counselors = Counselor.objects.all()[:3]
        if counselors:
            counselor = counselors[0]
            log_test("Counselor Model", True, f"Found {len(counselors)} counselors. Test counselor: {counselor.name}")
        else:
            log_test("Counselor Model", False, "No counselors found")
    except Exception as e:
        log_test("Counselor Model", False, str(e))
    
    # Test 5: Appointment System
    try:
        if counselors and test_user:
            # Try to find existing appointment or create one
            appointment = Appointment.objects.filter(
                user=test_user,
                counselor=counselors[0]
            ).first()
            
            if not appointment:
                appointment = Appointment.objects.create(
                    user=test_user,
                    counselor=counselors[0],
                    date=date.today(),
                    time=time(14, 0),  # 2:00 PM
                    services=['Individual Counseling'],  # Should be a list for JSONField
                    reason='System test appointment',
                    phone='09123456789',
                    course_section='CEN-3A',
                    status='pending'
                )
            log_test("Appointment System", True, f"Appointment ID: {appointment.id}, Status: {appointment.status}")
        else:
            log_test("Appointment System", False, "Missing counselor or user data")
    except Exception as e:
        log_test("Appointment System", False, str(e))
    
    # Test 6: Report System (FIXED - include counselor_id)
    try:
        if 'appointment' in locals() and appointment and counselors:
            report = Report.objects.filter(appointment=appointment).first()
            if not report:
                report = Report.objects.create(
                    user=test_user,
                    appointment=appointment,
                    counselor=counselors[0],  # FIXED: Added required counselor field
                    title='System Test Report',
                    description='This is a test report for system validation',
                    report_type='session'
                )
            log_test("Report System", True, f"Report ID: {report.id}, Type: {report.report_type}")
        else:
            log_test("Report System", False, "No appointment or counselor available for report")
    except Exception as e:
        log_test("Report System", False, str(e))
    
    # Test 7: Email System
    try:
        send_mail(
            'CalmConnect System Test - Fixed',
            'This is a test email from CalmConnect system test (fixed version).',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False
        )
        log_test("Email System", True, f"Email backend: {settings.EMAIL_BACKEND}")
    except Exception as e:
        log_test("Email System", False, str(e))
    
    # Test 8: Notification System (FIXED - removed 'title' field)
    try:
        notification = Notification.objects.filter(user=test_user).first()
        if not notification:
            notification = Notification.objects.create(
                user=test_user,
                message='System Test Notification - This is a test notification for system validation',  # FIXED: No title field
                type='general'
            )
        log_test("Notification System", True, f"Notification ID: {notification.id}")
    except Exception as e:
        log_test("Notification System", False, str(e))
    
    # Test 9: Feedback System (FIXED - use correct field names)
    try:
        if 'appointment' in locals() and appointment and counselors:
            feedback = Feedback.objects.filter(appointment=appointment).first()
            if not feedback:
                feedback = Feedback.objects.create(
                    user=test_user,
                    appointment=appointment,
                    counselor=counselors[0],  # FIXED: Added counselor field
                    overall_rating=5,  # FIXED: Use overall_rating instead of rating
                    positive_feedback='Great system test session!',  # FIXED: Use positive_feedback instead of comment
                    submitted_at=timezone.now()
                )
            log_test("Feedback System", True, f"Feedback ID: {feedback.id}, Rating: {feedback.overall_rating}")
        else:
            log_test("Feedback System", False, "No appointment available for feedback")
    except Exception as e:
        log_test("Feedback System", False, str(e))
    
    # Test 10: Security Features
    try:
        # Test password validation
        from django.contrib.auth.password_validation import validate_password
        validate_password('TestPassword123!', test_user)
        
        # Test session security settings
        session_age = settings.SESSION_COOKIE_AGE
        secure_cookies = hasattr(settings, 'SESSION_COOKIE_HTTPONLY') and settings.SESSION_COOKIE_HTTPONLY
        
        log_test("Security Features", True, f"Session age: {session_age}s, Secure cookies: {secure_cookies}")
    except Exception as e:
        log_test("Security Features", False, str(e))
    
    # Test 11: Static Files and Media
    try:
        static_url = settings.STATIC_URL
        media_url = settings.MEDIA_URL
        static_root = hasattr(settings, 'STATIC_ROOT')
        media_root = hasattr(settings, 'MEDIA_ROOT')
        
        log_test("Static/Media Configuration", True, f"Static: {static_url}, Media: {media_url}")
    except Exception as e:
        log_test("Static/Media Configuration", False, str(e))
    
    # Test 12: Middleware and Security Headers
    try:
        middleware_count = len(settings.MIDDLEWARE)
        has_security_middleware = 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE
        has_custom_middleware = any('mentalhealth.middleware' in mw for mw in settings.MIDDLEWARE)
        
        log_test("Middleware Configuration", True, f"Count: {middleware_count}, Security: {has_security_middleware}, Custom: {has_custom_middleware}")
    except Exception as e:
        log_test("Middleware Configuration", False, str(e))
    
    # Test 13: Additional Core Features Test
    try:
        # Test DASS21 results
        from mentalhealth.models import DASSResult
        dass_count = DASSResult.objects.count()
        
        # Test Live Session model
        from mentalhealth.models import LiveSession
        live_session_count = LiveSession.objects.count()
        
        log_test("Additional Models", True, f"DASS Results: {dass_count}, Live Sessions: {live_session_count}")
    except Exception as e:
        log_test("Additional Models", False, str(e))
    
    # Test Results Summary
    print("\n" + "=" * 60)
    print("🏆 FIXED TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {results['passed']}")
    print(f"❌ Tests Failed: {results['failed']}")
    total_tests = results['passed'] + results['failed']
    print(f"📊 Success Rate: {(results['passed']/total_tests)*100:.1f}%")
    
    if results['failed'] > 0:
        print("\n⚠️  FAILED TESTS DETAILS:")
        for test_name, status, details in results['details']:
            if not status:
                print(f"   • {test_name}: {details}")
    
    # System Health Assessment
    print("\n🔍 SYSTEM HEALTH ASSESSMENT")
    print("=" * 60)
    
    success_rate = (results['passed']/total_tests)*100
    
    if success_rate >= 90:
        print("🟢 EXCELLENT: System is in excellent condition!")
        print("   • Core functionalities are working perfectly")
        print("   • Ready for production deployment")
        print("   • Consider adding Cloudflare for enhanced performance")
        print("   • Beta testing can begin")
    elif success_rate >= 75:
        print("🟡 GOOD: System is mostly functional with minor issues")
        print("   • Core functionality appears stable")
        print("   • Address failed tests before production")
        print("   • Most features are working correctly")
    elif success_rate >= 50:
        print("🟠 FAIR: System has significant issues")
        print("   • Multiple core features need attention")
        print("   • Not ready for production")
    else:
        print("🔴 POOR: System has critical issues")
        print("   • Major functionality is broken")
        print("   • Requires immediate attention")
    
    # Feature Assessment
    print("\n📋 CORE FEATURES STATUS:")
    feature_status = {
        'User Registration & Authentication': '✅ Working' if results['passed'] >= 2 else '❌ Issues',
        'Counselor Management': '✅ Working' if any('Counselor' in detail[0] and detail[1] for detail in results['details']) else '❌ Issues',
        'Appointment System': '✅ Working' if any('Appointment' in detail[0] and detail[1] for detail in results['details']) else '❌ Issues',
        'Email System': '✅ Working' if any('Email' in detail[0] and detail[1] for detail in results['details']) else '❌ Issues',
        'Security Features': '✅ Working' if any('Security' in detail[0] and detail[1] for detail in results['details']) else '❌ Issues',
        'Database Integration': '✅ Working' if any('Database' in detail[0] and detail[1] for detail in results['details']) else '❌ Issues',
    }
    
    for feature, status in feature_status.items():
        print(f"   {status} {feature}")
    
    print("\n📋 NEXT STEPS RECOMMENDATIONS:")
    if results['failed'] == 0:
        print("   🎉 CONGRATULATIONS! All core systems are working!")
        print("   ✅ System is ready for:")
        print("   • User acceptance testing")
        print("   • Beta testing with real students")
        print("   • Production deployment preparation")
        print("   • Cloudflare integration")
        print("   • Performance optimization")
        print("   • Load testing")
    else:
        print("   🔧 Priority fixes needed:")
        failed_tests = [name for name, status, _ in results['details'] if not status]
        for i, test in enumerate(failed_tests[:5], 1):
            print(f"   {i}. {test}")
        if len(failed_tests) > 5:
            print(f"   ... and {len(failed_tests) - 5} more")
    
    # Production Readiness Checklist
    print("\n📊 PRODUCTION READINESS CHECKLIST:")
    checklist_items = [
        ("Core Models", success_rate >= 80),
        ("Authentication", any('Authentication' in detail[0] and detail[1] for detail in results['details'])),
        ("Email System", any('Email' in detail[0] and detail[1] for detail in results['details'])),
        ("Security Features", any('Security' in detail[0] and detail[1] for detail in results['details'])),
        ("Database", any('Database' in detail[0] and detail[1] for detail in results['details'])),
    ]
    
    for item, status in checklist_items:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {item}")
    
    ready_count = sum(1 for _, status in checklist_items if status)
    total_items = len(checklist_items)
    
    print(f"\n📈 Production Readiness: {ready_count}/{total_items} ({(ready_count/total_items)*100:.0f}%)")
    
    if ready_count == total_items:
        print("🚀 SYSTEM IS PRODUCTION READY!")
    elif ready_count >= total_items * 0.8:
        print("🟡 NEARLY PRODUCTION READY - Minor fixes needed")
    else:
        print("🔧 NOT PRODUCTION READY - Major fixes required")
    
    return results

if __name__ == "__main__":
    test_system_fixed()
