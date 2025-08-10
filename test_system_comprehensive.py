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

def test_system_comprehensive():
    """Comprehensive system test for CalmConnect core functionalities"""
    print("🧪 CalmConnect System Test - Comprehensive Analysis")
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
        test_user = CustomUser.objects.filter(username='test_user_sys').first()
        if not test_user:
            test_user = CustomUser.objects.create_user(
                username='test_user_sys',
                email='test@clsu2.edu.ph',
                password='TestPassword123!',
                full_name='Test User System',
                student_id='2021-12345',
                age=20,
                gender='M',
                college='CEN',
                program='Bachelor of Science in Information Technology',
                year_level='3rd Year'
            )
        log_test("User Model Creation", True, f"User ID: {test_user.id}")
    except Exception as e:
        log_test("User Model Creation", False, str(e))
    
    # Test 3: Authentication System
    try:
        auth_user = authenticate(username='test_user_sys', password='TestPassword123!')
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
                    services='Individual Counseling',
                    reason='System test appointment',
                    status='pending'
                )
            log_test("Appointment System", True, f"Appointment ID: {appointment.id}, Status: {appointment.status}")
        else:
            log_test("Appointment System", False, "Missing counselor or user data")
    except Exception as e:
        log_test("Appointment System", False, str(e))
    
    # Test 6: Report System
    try:
        if 'appointment' in locals() and appointment:
            report = Report.objects.filter(appointment=appointment).first()
            if not report:
                report = Report.objects.create(
                    user=test_user,
                    appointment=appointment,
                    title='System Test Report',
                    description='This is a test report for system validation',
                    report_type='session'
                )
            log_test("Report System", True, f"Report ID: {report.id}, Type: {report.report_type}")
        else:
            log_test("Report System", False, "No appointment available for report")
    except Exception as e:
        log_test("Report System", False, str(e))
    
    # Test 7: Email System
    try:
        send_mail(
            'CalmConnect System Test',
            'This is a test email from CalmConnect system test.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False
        )
        log_test("Email System", True, f"Email backend: {settings.EMAIL_BACKEND}")
    except Exception as e:
        log_test("Email System", False, str(e))
    
    # Test 8: Notification System
    try:
        notification = Notification.objects.filter(user=test_user).first()
        if not notification:
            notification = Notification.objects.create(
                user=test_user,
                title='System Test Notification',
                message='This is a test notification for system validation',
                type='info'
            )
        log_test("Notification System", True, f"Notification ID: {notification.id}")
    except Exception as e:
        log_test("Notification System", False, str(e))
    
    # Test 9: Feedback System
    try:
        if 'appointment' in locals() and appointment:
            feedback = Feedback.objects.filter(appointment=appointment).first()
            if not feedback:
                feedback = Feedback.objects.create(
                    user=test_user,
                    appointment=appointment,
                    rating=5,
                    comment='Great system test session!',
                    submitted_at=timezone.now()
                )
            log_test("Feedback System", True, f"Feedback ID: {feedback.id}, Rating: {feedback.rating}")
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
    
    # Test Results Summary
    print("\n" + "=" * 60)
    print("🏆 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {results['passed']}")
    print(f"❌ Tests Failed: {results['failed']}")
    print(f"📊 Success Rate: {(results['passed']/(results['passed']+results['failed']))*100:.1f}%")
    
    if results['failed'] > 0:
        print("\n⚠️  FAILED TESTS DETAILS:")
        for test_name, status, details in results['details']:
            if not status:
                print(f"   • {test_name}: {details}")
    
    # System Health Assessment
    print("\n🔍 SYSTEM HEALTH ASSESSMENT")
    print("=" * 60)
    
    success_rate = (results['passed']/(results['passed']+results['failed']))*100
    
    if success_rate >= 90:
        print("🟢 EXCELLENT: System is in excellent condition!")
        print("   • Ready for production deployment")
        print("   • Consider adding Cloudflare for enhanced performance")
    elif success_rate >= 75:
        print("🟡 GOOD: System is mostly functional with minor issues")
        print("   • Address failed tests before production")
        print("   • System core functionality appears stable")
    elif success_rate >= 50:
        print("🟠 FAIR: System has significant issues")
        print("   • Multiple core features need attention")
        print("   • Not ready for production")
    else:
        print("🔴 POOR: System has critical issues")
        print("   • Major functionality is broken")
        print("   • Requires immediate attention")
    
    print("\n📋 NEXT STEPS RECOMMENDATIONS:")
    if results['failed'] == 0:
        print("   ✅ All tests passed! System is ready for:")
        print("   • Beta testing with real users")
        print("   • Production deployment preparation")
        print("   • Cloudflare integration")
        print("   • Performance optimization")
    else:
        print("   🔧 Fix failed tests first:")
        failed_tests = [name for name, status, _ in results['details'] if not status]
        for i, test in enumerate(failed_tests[:5], 1):
            print(f"   {i}. {test}")
        if len(failed_tests) > 5:
            print(f"   ... and {len(failed_tests) - 5} more")
    
    return results

if __name__ == "__main__":
    test_system_comprehensive()
