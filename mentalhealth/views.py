# @PydevCodeAnalysisIgnore
# Standard library imports
import json
import logging
from datetime import datetime, timedelta

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Avg, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.views.decorators.http import (require_GET, require_POST,
                                          require_http_methods)

# Third-party imports
import openai

# Django REST Framework imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Local imports
from .decorators import (
    api_staff_required,
    verified_required
)
from django.views.decorators.csrf import csrf_exempt
from .forms import (
    AppointmentForm,
    CounselorProfileForm,
    CustomLoginForm,
    CustomUserRegistrationForm,
    ReportForm
)
from .models import (
    Appointment, Counselor, CustomUser, DASSResult, Feedback, LiveSession,
    Notification, RelaxationLog, Report, SessionMessage, SessionParticipant
)
from .notification_service import notification_service
from .serializers import AppointmentSerializer

# Import ratelimit with fallback
try:
    from ratelimit.decorators import ratelimit
    RATELIMIT_AVAILABLE = True
except ImportError:
    # Fallback decorator if ratelimit is not available
    def ratelimit(key=None, rate=None, block=True):
        def decorator(view_func):
            return view_func
        return decorator
    RATELIMIT_AVAILABLE = False

logger = logging.getLogger(__name__)


@login_required
def dass21_test(request):
    return render(request, 'index.html', {
        'username': request.user.username,
    })


@verified_required
@login_required
def index(request):
    # Get the most recent DASS result for this user
    latest_result = DASSResult.objects.filter(user=request.user).order_by(
        '-date_taken').first()

    scores = {
        'depression': latest_result.depression_score if latest_result else 0,
        'anxiety': latest_result.anxiety_score if latest_result else 0,
        'stress': latest_result.stress_score if latest_result else 0,
    }

    context = {
        'user': request.user,
        'username': request.user.username,
        'college_display': request.user.get_college_display(),
        'year_display': request.user.get_year_level_display(),
        'profile_picture': (
            request.user.profile_picture.url
            if request.user.profile_picture else None
        ),
        'scores': scores,
    }

    return render(request, 'index.html', context)


@login_required
def save_dass_results(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Create and save new result
            result = DASSResult(
                user=request.user,
                depression_score=data['depression'],
                anxiety_score=data['anxiety'],
                stress_score=data['stress'],
                depression_severity=data['depression_severity'],
                anxiety_severity=data['anxiety_severity'],
                stress_severity=data['stress_severity'],
                answers=data['answers']
            )
            result.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Results saved successfully'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


def welcome_api(request):
    """
    API endpoint that logs requests and returns a welcome message with metadata
    """
    logger.info(f"Request received: {request.method} {request.path}")

    return JsonResponse({
        'message': 'Welcome to the CalmConnect API Service!',
        'method': request.method,
        'path': request.path,
        'timestamp': timezone.now().isoformat(),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'remote_addr': request.META.get('REMOTE_ADDR', '')
    })


def health_check(request):
    """
    API endpoint that logs requests and returns a health check status with metadata
    """
    logger.info(f"Health check request: {request.method} {request.path}")

    return JsonResponse({
        'status': 'healthy',
        'message': 'CalmConnect API Service is running smoothly!',
        'method': request.method,
        'path': request.path,
        'timestamp': timezone.now().isoformat(),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'remote_addr': request.META.get('REMOTE_ADDR', ''),
        'version': '1.0.0'
    })


@login_required
def user_profile(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                user = request.user
                # Only allow updating these specific fields
                user.full_name = request.POST.get('full_name', user.full_name)
                user.college = request.POST.get('college', user.college)
                user.program = request.POST.get('program', user.program)
                user.year_level = request.POST.get(
                    'year_level', user.year_level)
                user.age = request.POST.get('age', user.age)
                user.gender = request.POST.get('gender', user.gender)
                user.save()

                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        elif 'profile_picture' in request.FILES:
            try:
                user = request.user
                # Handle profile picture upload
                profile_picture = request.FILES['profile_picture']

                # Validate file type
                allowed_types = [
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/gif']
                if profile_picture.content_type not in allowed_types:
                    return JsonResponse({
                        'success': False,
                        'error': ('Invalid file type. Please upload a JPEG, PNG, or GIF '
                                  'image.')
                    })

                # Validate file size (max 5MB)
                if profile_picture.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'error': 'File size too large. Please upload an image smaller than 5MB.'
                    })

                # Save the new profile picture
                user.profile_picture = profile_picture
                user.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully!',
                    'image_url': user.profile_picture.url
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

    user = request.user

    # Paginate test results
    test_results = user.dassresult_set.all().order_by('-date_taken')
    test_paginator = Paginator(test_results, 5)  # Show 5 results per page
    test_page_number = request.GET.get('test_page')
    test_page_obj = test_paginator.get_page(test_page_number)

    # Paginate appointments
    appointments = Appointment.objects.filter(
        user=user).order_by('-date', '-time')
    appt_paginator = Paginator(appointments, 5)  # Show 5 appointments per page
    appt_page_number = request.GET.get('appt_page')
    appt_page_obj = appt_paginator.get_page(appt_page_number)

    # Enhanced context
    context = {
        'full_name': request.user.get_full_name(),
        'college_display': request.user.get_college_display(),
        'test_page_obj': test_page_obj,
        'appt_page_obj': appt_page_obj,
    }

    # Messages for empty sections
    if test_page_obj.paginator.count == 0:
        messages.info(
            request,
            'No DASS21 test results yet. Take the test to start tracking your progress.')
    if appt_page_obj.paginator.count == 0:
        messages.info(
            request,
            'No appointments scheduled. Book a session to get started.')

    return render(request, 'user-profile.html', context)


def home(request):
    return render(request, 'mentalhealth/login.html')


def register(request):
    if request.method == 'POST':
        # Add detailed debugging
        print(f"POST data received: {request.POST}")
        form = CustomUserRegistrationForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            try:
                print("Form is valid, creating user...")
                user = form.save(commit=False)
                user.is_active = False
                if not user.verification_token:
                    user.verification_token = get_random_string(64)
                print(f"Saving user with email: {user.email}")
                user.save()
                print("User saved successfully")

                verification_link = request.build_absolute_uri(
                    reverse('verify_email',
                            kwargs={'token': user.verification_token})
                )
                print(f"Verification link: {verification_link}")

                # Send verification email
                try:
                    html_message = render_to_string(
                        'mentalhealth/verification-email.html', {
                            'user': user, 'verification_link': verification_link})

                    plain_message = (
                        f"Verify Your Email for CalmConnect\n\n"
                        f"Hello {user.full_name},\n\n"
                        f"Please click this link to verify your email: {verification_link}\n\n"
                        f"Thank you!")

                    print(f"Sending email to: {user.email}")
                    send_mail(
                        'Verify Your Email for CalmConnect',
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=True,
                        # Changed to True to prevent email errors from breaking
                        # registration
                    )
                    print("Email sent successfully")
                except Exception as email_error:
                    print(f"Email sending failed: {email_error}")
                    # Continue without email for now - user can still verify
                    # manually
                    pass

                # For development, if email fails, make user active anyway
                if not settings.DEBUG:
                    # In production, require email verification
                    if request.headers.get(
                            'X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'email': user.email,
                            'redirect_url': reverse('verify_prompt')
                        })
                    return redirect('verify_prompt')
                else:
                    # In development, make user active even if email fails
                    user.is_active = True
                    user.email_verified = True
                    user.save()
                    print("User activated for development")

                    if request.headers.get(
                            'X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'email': user.email,
                            'redirect_url': reverse('index')
                        })
                    return redirect('index')

            except Exception as e:
                print(f"Exception in registration: {e}")
                import traceback
                traceback.print_exc()

                # If user was created but email failed, handle gracefully
                if 'user' in locals() and user and user.pk:
                    print("User was created but email verification failed")
                    if settings.DEBUG:
                        # In development, activate user anyway
                        user.is_active = True
                        user.email_verified = True
                        user.save()
                        print("User activated for development despite email failure")

                        if request.headers.get(
                                'X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'email': user.email,
                                'redirect_url': reverse('index'),
                                'message': (
                                    'Registration successful! '
                                    'Email verification skipped in development.'
                                )
                            })
                        return redirect('index')

                error_msg = str(e)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=400)
                messages.error(request, error_msg)
        else:
            # Add debugging for form errors
            print(f"Form errors: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data()
                }, status=400)
            messages.error(request, "Please correct the errors below.")

    # GET request or form invalid with non-AJAX submission
    form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})


# Add these new views
def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)

        if user.email_verified:
            messages.info(request, "Email already verified.")
            return redirect('login')

        user.email_verified = True
        user.is_active = True  # Allow login after verification
        user.verification_token = None
        user.save()

        # Auto-login after verification
        login(request, user)
        messages.success(request, "Email successfully verified!")
        return redirect('index')  # Changed from login to index

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('register')


def resend_verification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            user = CustomUser.objects.get(email=email)

            if user.email_verified:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is already verified'
                }, status=400)

            token = user.generate_verification_token()
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': token})
            )

            # Render HTML email
            html_message = render_to_string(
                'mentalhealth/verification-email.html', {
                    'user': user, 'verification_link': verification_link})

            # Plain text version
            plain_message = (
                f"Verify Your Email for CalmConnect\n\n"
                f"Hello {user.full_name},\n\n"
                f"We've received a request to resend your verification email. \n"
                f"Please verify your email address by visiting this link:\n\n"
                f"{verification_link}\n\n"
                f"If you didn't request this, you can safely ignore this email.\n\n"
                f"Thank you for using CalmConnect!\n"
                f"The CalmConnect Team")

            send_mail(
                'Verify your email for CalmConnect',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return JsonResponse({
                'success': True,
                'message': 'Verification email resent successfully'
            })

        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User with this email does not exist'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)


def verify_prompt(request):
    if request.user.is_authenticated and request.user.email_verified:
        return redirect('index')

    if request.user.is_authenticated:
        # User is logged in but not verified
        return render(request, 'mentalhealth/verify-prompt.html', {
            'email': request.user.email,
            'username': request.user.username
        })

    # User not logged in at all
    return redirect('login')


def validate_fields(request):
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')
        errors = []

        if field == 'username':
            if CustomUser.objects.filter(username=value).exists():
                errors.append('Username already taken')

        return JsonResponse({
            'valid': len(errors) == 0,
            'errors': errors
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def login_view(request):
    # Initialize error_message at the start
    error_message = None

    if request.user.is_authenticated:
        # Check for counselor profile first
        if hasattr(request.user, 'counselor_profile'):
            # Check if the counselor profile is active
            if not request.user.counselor_profile.is_active:
                messages.error(
                    request, 'Your account has been archived. Please contact the administrator.')
                logout(request)
                return redirect('login')
            return redirect('counselor_dashboard')
        elif request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        elif request.user.email_verified:
            return redirect('index')
        return redirect('verify_prompt')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Add login debug logging
            username = request.POST.get('username', '')
            logger.info(
                f"Login attempt for {username}, user_exists: True, "
                f"is_active: {user.is_active}"
            )

            # Check if user is a counselor BEFORE logging in
            if hasattr(user, 'counselor_profile'):
                # Check if the counselor profile is active
                if not user.counselor_profile.is_active:
                    error_message = (
                        'Your account has been archived. '
                        'Please contact the administrator.'
                    )
                    return render(request, 'login.html', {
                        'form': CustomLoginForm(),
                        'error_message': error_message
                    })

            # If we get here, the user can log in
            login(request, user)

            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)

            # Check if user is a counselor
            if hasattr(user, 'counselor_profile'):
                # Check if this is a new counselor with default password
                # This should be handled by a more secure method in production
                if hasattr(
                        user,
                        'force_password_change') and user.force_password_change:
                    request.session['force_password_change'] = True
                    return redirect('password_change')
                return redirect('counselor_dashboard')
            elif user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            elif user.email_verified:
                return redirect('index')
            return redirect('verify_prompt')
        else:
            # Provide more specific error messages
            username = request.POST.get('username', '')
            # Check if username exists
            user_exists = False
            if '@' in username:
                user_exists = CustomUser.objects.filter(
                    email=username).exists()
            else:
                user_exists = CustomUser.objects.filter(
                    username=username).exists()
            if not user_exists:
                error_message = (
                    'Username or email not found. Please check your credentials.'
                )
            else:
                # Check if user account is active
                if '@' in username:
                    try:
                        user = CustomUser.objects.get(email=username)
                    except CustomUser.DoesNotExist:
                        user = None
                else:
                    try:
                        user = CustomUser.objects.get(username=username)
                    except CustomUser.DoesNotExist:
                        user = None

                if user and not user.is_active:
                    error_message = (
                        'Your account has been deactivated. '
                        'Please contact the administrator.'
                    )
                else:
                    # User exists but password is wrong
                    error_message = 'Incorrect password. Please try again.'

    return render(request, 'login.html', {
        'form': CustomLoginForm(),
        'error_message': error_message
    })


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@require_http_methods(["POST"])
def get_programs_ajax(request):
    """AJAX view to get programs based on selected college"""
    try:
        data = json.loads(request.body)
        college = data.get('college')

        # Define college-program mapping (same as in your JS)
        college_programs = {
            'CASS': [
                'Bachelor of Arts in English',
                'Bachelor of Arts in Literature',
                'Bachelor of Arts in Social Sciences',
                'Bachelor of Arts in Development Communication',
                'Bachelor of Arts in Psychology'
            ],
            'CEN': [
                'Bachelor of Science in Civil Engineering',
                'Bachelor of Science in Information Technology',
                'Bachelor of Science in Agricultural Biosystems Engineering',
            ],
            'CBA': [
                'Bachelor of Science in Accountancy',
                'Bachelor of Science in Business Administration',
                'Bachelor of Science in Entrepreneurship',
                'Bachelor of Science in Management Accounting'
            ],
            'COF': [
                'Bachelor of Science in Fisheries'
            ],
            'CAG': [
                'Bachelor of Science in Agriculture',
                'Bachelor of Science in Agribusiness',
                'Bachelor of Science in Animal Science',
                'Bachelor of Science in Crop Science'
            ],
            'CHSI': [
                'Bachelor of Science in Food Technology',
                'Bachelor of Science in Fashion and Textile Technology',
                'Bachelor of Science in Hospitality Management',
                'Bachelor of Science in Tourism Management'
            ],
            'CED': [
                'Bachelor of Elementary Education',
                'Bachelor of Secondary Education',
                'Bachelor of Cultural and Arts Education',
                'Bachelor of Early Childhood Education',
            ],
            'COS': [
                'Bachelor of Science in Biology',
                'Bachelor of Science in Chemistry',
                'Bachelor of Science in Environmental Science',
                'Bachelor of Science in Mathematics',
                'Bachelor of Science in Statistics',
                'Bachelor of Science in Meteorology'
            ],
            'CVSM': [
                'Doctor of Veterinary Medicine'
            ]
        }

        programs = college_programs.get(college, [])
        return JsonResponse({
            'success': True,
            'programs': programs
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
def validate_field_ajax(request):
    """AJAX view to validate individual form fields"""
    try:
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        errors = []

        if field == 'username':
            if CustomUser.objects.filter(username=value).exists():
                errors.append('This username is already taken')

        # Return the validation results
        return JsonResponse({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@verified_required
@login_required
def scheduler(request):
    # Get the most recent DASS result for this user
    latest_result = DASSResult.objects.filter(
        user=request.user).order_by('-date_taken').first()

    counselors = Counselor.objects.filter(is_active=True)

    # Debug output
    print(f"Latest DASS result: {latest_result}")
    print(f"Counselors: {list(counselors.values_list('name', flat=True))}")

    context = {
        'counselors': counselors,
        'username': request.user.username,
        'dass_result': latest_result,
        'scores': {
            'depression': latest_result.depression_score if latest_result else 0,
            'anxiety': latest_result.anxiety_score if latest_result else 0,
            'stress': latest_result.stress_score if latest_result else 0,
        } if latest_result else None,
        'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None,
    }

    return render(request, 'scheduler.html', context)


@require_GET
@login_required
def get_counselor_slots(request, counselor_id):
    try:
        counselor = Counselor.objects.get(id=counselor_id)
        # Generate available slots for the next 2 weeks
        available_slots = []
        today = timezone.now().date()
        for day_offset in range(0, 7):  # Next 7 days (1 week)
            current_date = today + timedelta(days=day_offset)
            day_name = current_date.strftime('%A')
            if day_name in counselor.available_days:
                # Get individual day schedule or fall back to default
                day_schedule = counselor.day_schedules.get(day_name, {})
                from datetime import time as dt_time

                def parse_time(val):
                    if isinstance(val, str):
                        parts = val.split(":")
                        return dt_time(int(parts[0]), int(parts[1]))
                    return val
                start_time = parse_time(
                    day_schedule.get('start_time')) if day_schedule.get('start_time') else (
                    counselor.available_start_time if counselor.available_start_time else None)
                end_time = parse_time(
                    day_schedule.get('end_time')) if day_schedule.get('end_time') else (
                    counselor.available_end_time if counselor.available_end_time else None)
                if start_time and end_time:
                    time_str = start_time.strftime('%H:%M')
                    # Check if slot is already booked
                    is_booked = Appointment.objects.filter(
                        counselor=counselor,
                        date=current_date,
                        time=time_str,
                        status__in=['pending', 'confirmed']
                    ).exists()
                    if not is_booked:
                        available_slots.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'day': day_name,
                            'time': time_str,
                            'display': f"{day_name}, {time_str}"
                        })
        return JsonResponse({
            'success': True,
            'slots': available_slots
        })
    except Counselor.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Counselor not found'
        }, status=404)


def create_notification(
        user,
        message,
        notification_type='general',
        url='#',
        priority='normal'):
    """Create a notification for a user (legacy function - use notification_service directly)"""
    return notification_service.create_notification(
        user=user,
        message=message,
        notification_type=notification_type,
        priority=priority,
        action_url=url
    )


@require_POST
@login_required
def book_appointment(request):
    """Book an appointment"""
    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = [
            'counselor_id',
            'date',
            'time',
            'session_type',
            'services',
            'reason',
            'phone',
            'course_section']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)

        # Get counselor
        try:
            counselor = Counselor.objects.get(
                id=data['counselor_id'], is_active=True)
        except Counselor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Counselor not found or not available'
            }, status=404)

        # Parse date and time
        try:
            appointment_date = datetime.strptime(
                data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid date or time format'
            }, status=400)

        # Check if date is in the past
        if appointment_date < timezone.now().date():
            return JsonResponse({
                'success': False,
                'error': 'Cannot book appointments in the past'
            }, status=400)

        # Check if time slot is available
        existing_appointment = Appointment.objects.filter(
            counselor=counselor,
            date=appointment_date,
            time=appointment_time,
            status__in=['pending', 'confirmed']
        ).first()

        if existing_appointment:
            return JsonResponse({
                'success': False,
                'error': 'This time slot is already booked'
            }, status=400)

        # Create appointment
        appointment = Appointment.objects.create(
            user=request.user,
            counselor=counselor,
            date=appointment_date,
            time=appointment_time,
            session_type=data['session_type'],
            services=data['services'],
            reason=data['reason'],
            phone=data['phone'],
            course_section=data['course_section'],
            status='pending'
        )

        # Attach DASS result if provided
        if 'dass_result_id' in data and data['dass_result_id']:
            try:
                dass_result = DASSResult.objects.get(
                    id=data['dass_result_id'], user=request.user)
                appointment.dass_result = dass_result
                appointment.save()
            except DASSResult.DoesNotExist:
                pass  # Continue without DASS result

        # Create notifications using the new notification service
        from .notification_service import create_appointment_notification
        create_appointment_notification(appointment, 'created')

        # Handle session type specific actions
        if appointment.session_type == 'remote':
            # Create live session for remote appointments
            start_time = timezone.make_aware(
                datetime.combine(
                    appointment.date,
                    appointment.time))
            # Default 1-hour session
            end_time = start_time + timedelta(hours=1)

            # Create or get existing live session
            live_session, created = LiveSession.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'scheduled_start': start_time,
                    'scheduled_end': end_time,
                    'session_type': 'video',
                    'status': 'scheduled'
                }
            )

            # Generate room ID if not already set
            if not live_session.room_id:
                live_session.room_id = f'appointment_{appointment.id}'
                live_session.save()

            # Generate video call link for remote sessions
            video_call_url = request.build_absolute_uri(
                reverse('live_session_view', kwargs={'room_id': live_session.room_id})
            )
            appointment.video_call_url = video_call_url
            appointment.save()

            # Send remote session confirmation email
            send_remote_session_email(request, request.user, appointment)
        else:
            # Send standard confirmation email for face-to-face sessions
            send_confirmation_email(request, request.user, appointment)

        return JsonResponse({
            'success': True,
            'message': 'Appointment booked successfully!',
            'appointment_id': appointment.id,
            'session_type': appointment.session_type,
            'video_call_url': getattr(appointment, 'video_call_url', None)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while booking the appointment'
        }, status=500)


def send_remote_session_email(request, user, appointment):
    """Send remote session confirmation email with video call link"""
    # Generate cancellation token and deadline
    appointment.cancellation_token = get_random_string(64)
    appointment.cancellation_deadline = timezone.now() + timedelta(hours=24)
    appointment.save()

    # Build URLs
    cancellation_url = request.build_absolute_uri(
        reverse(
            'cancel_appointment', kwargs={
                'token': appointment.cancellation_token}))

    # Get or create live session for remote appointments
    if appointment.session_type == 'remote':
        try:
            live_session = LiveSession.objects.get(appointment=appointment)
            room_id = live_session.room_id
        except LiveSession.DoesNotExist:
            room_id = f'appointment_{appointment.id}'
    else:
        room_id = f'appointment_{appointment.id}'

    video_call_url = request.build_absolute_uri(
        reverse('live_session_view', kwargs={'room_id': room_id})
    )

    subject = 'Your CalmConnect Remote Session Confirmation'

    html_message = render_to_string('mentalhealth/remote-session-confirmation.html', {
        'user': user,
        'appointment': appointment,
        'cancellation_url': cancellation_url,
        'video_call_url': video_call_url,
        'deadline': appointment.cancellation_deadline.strftime("%B %d, %Y %I:%M %p")
    })

    plain_message = f"""
    Remote Session Confirmation

    Hello {user.full_name},

    Your remote counseling session has been successfully booked with CalmConnect.

    Appointment Details:
    - Counselor: {appointment.counselor}
    - Date: {appointment.date}
    - Time: {appointment.time}
    - Session Type: {appointment.get_session_type_display()}
    - Services: {', '.join(appointment.services)}

    Video Call Information:
    Your video call will be conducted through our secure platform.
    Video Call Link: {video_call_url}

    How to Join:
    1. Click the video call link above 5-10 minutes before your session
    2. Allow camera and microphone access when prompted
    3. Wait in the virtual waiting room until your counselor joins
    4. Your session will begin automatically when both parties are ready

    Technical Requirements:
    - Stable internet connection
    - Webcam and microphone
    - Modern web browser (Chrome, Firefox, Safari, Edge)
    - Private, quiet location for your session

    If you need to reschedule or cancel, please contact us at least 24 hours in advance.

    Thank you for using CalmConnect!

    The CalmConnect Team
    """

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        print(f"❌ Failed to send remote session email: {e}")


def send_confirmation_email(request, user, appointment):
    """Send appointment confirmation email (identical content) with working cancellation"""
    # Generate cancellation token and deadline
    appointment.cancellation_token = get_random_string(64)
    appointment.cancellation_deadline = timezone.now() + timedelta(hours=24)
    appointment.save()

    # Build cancellation URL using the passed request object
    cancellation_url = request.build_absolute_uri(
        reverse(
            'cancel_appointment', kwargs={
                'token': appointment.cancellation_token}))

    # Keep the EXACT same email content as before
    subject = 'Your CalmConnect Appointment Confirmation'

    html_message = render_to_string('mentalhealth/appointment-confirmation.html', {
        'user': user,
        'appointment': appointment,
        'cancellation_url': cancellation_url,  # Only added this new variable
        'deadline': appointment.cancellation_deadline.strftime("%B %d, %Y %I:%M %p")
    })

    # Preserve the original plain text message exactly
    plain_message = f"""
    Appointment Confirmation

    Hello {user.full_name},

    Your counseling appointment has been successfully booked with CalmConnect.

    Appointment Details:
    - Counselor: {appointment.counselor}
    - Date: {appointment.date}
    - Time: {appointment.time}
    - Session Type: {appointment.get_session_type_display()}
    - Services: {', '.join(appointment.services)}

    What to Expect:
    Please arrive 5-10 minutes before your scheduled time. Bring any relevant documents or materials.

    If you need to reschedule or cancel, please contact us at least 24 hours in advance.

    Thank you for using CalmConnect!

    The CalmConnect Team
    """

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        print(f"❌ Failed to send confirmation email: {e}")


@require_http_methods(["GET", "POST"])
def cancel_appointment(request, token):
    try:
        appointment = Appointment.objects.get(cancellation_token=token)

        # Check if cancellation is still allowed
        if timezone.now() > appointment.cancellation_deadline:
            return render(
                request,
                'mentalhealth/cancellation-expired.html',
                status=400)

        if request.method == 'POST':
            # Process cancellation form
            reason = request.POST.get('reason', 'No reason provided')
            appointment.status = 'cancelled'
            appointment.cancellation_reason = reason
            appointment.save()

            # Send confirmation email with HTML template
            reschedule_url = request.build_absolute_uri(reverse('scheduler'))

            html_message = render_to_string(
                'mentalhealth/appointment-cancellation.html',
                {
                    'user': appointment.user,
                    'appointment': appointment,
                    'reschedule_url': reschedule_url,
                })

            plain_message = f"""
            Appointment Cancellation Confirmed

            Hello {appointment.user.full_name},

            Your counseling appointment has been successfully cancelled.

            Cancelled Appointment Details:
            - Counselor: {appointment.counselor}
            - Date: {appointment.date}
            - Time: {appointment.time}
            - Services: {', '.join(appointment.services)}
            """

            if appointment.cancellation_reason:
                plain_message += f"- Cancellation Reason: {appointment.cancellation_reason}\n"

            plain_message += f"""

            Need to reschedule?
            You can easily book a new appointment at any time through our scheduling system.

            We're sorry to see you go. You can always schedule a new appointment anytime.

            Thank you for using CalmConnect!

            The CalmConnect Team
            """

            send_mail(
                'Appointment Cancellation Confirmed',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.user.email],
                html_message=html_message,
                fail_silently=False
            )

            return render(request, 'mentalhealth/cancellation-success.html')

        # GET request - show cancellation form
        return render(request, 'mentalhealth/cancellation-form.html', {
            'appointment': appointment,
            'token': token
        })

    except Appointment.DoesNotExist:
        return render(
            request,
            'mentalhealth/cancellation-expired.html',
            status=404)


def send_feedback_request_email(request, appointment):
    """Send feedback request email when appointment is completed"""
    print(
        f"🔔 Sending feedback request email to {appointment.user.email} for appointment {appointment.id}")

    # Generate feedback token
    # Store token in session or create a temporary model field
    # For now, we'll use the appointment ID in the URL
    feedback_url = request.build_absolute_uri(
        reverse('feedback_form', kwargs={'appointment_id': appointment.id})
    )

    subject = 'How was your CalmConnect session?'

    html_message = render_to_string('mentalhealth/feedback-request.html', {
        'user': appointment.user,
        'appointment': appointment,
        'feedback_url': feedback_url,
    })

    plain_message = f"""
    How was your CalmConnect session?

    Hello {appointment.user.full_name},

    Your counseling session has been completed. We hope it was helpful and would love to hear about your experience!

    Session Details:
    - Counselor: {appointment.counselor.name}
    - Date: {appointment.date}
    - Time: {appointment.time}
    - Services: {', '.join(appointment.services)}

    Share Your Feedback:
    Your feedback helps us improve our services and supports our counselors in providing the best care possible.
    It only takes a few minutes and your input is invaluable to us.

    Thank you for choosing CalmConnect for your mental health support!

    The CalmConnect Team
    """

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.user.email],
            html_message=html_message,
            fail_silently=False
        )
        print(
            f"✅ Feedback request email sent successfully to {appointment.user.email}")
    except Exception as e:
        print(f"❌ Failed to send feedback request email: {e}")


def force_logout(request):
    """Force logout and clear all session data."""
    logout(request)
    request.session.flush()  # Deletes the session cookie and all data
    return redirect('login')


@staff_member_required
def admin_dashboard(request):
    # Calculate statistics
    total_appointments = Appointment.objects.count()

    # Debug: Check what severity values exist in the database
    all_severities = DASSResult.objects.values_list(
        'depression_severity', 'anxiety_severity', 'stress_severity'
    ).distinct()
    print(f"All severity values in database: {list(all_severities)}")

    # Fix the high risk cases query to match the actual severity values being
    # stored
    high_risk_cases = DASSResult.objects.filter(
        Q(depression_severity__icontains='Severe') |
        Q(depression_severity__icontains='Extremely') |
        Q(anxiety_severity__icontains='Severe') |
        Q(anxiety_severity__icontains='Extremely') |
        Q(stress_severity__icontains='Severe') |
        Q(stress_severity__icontains='Extremely')
    ).distinct().count()

    print(f"High risk cases found: {high_risk_cases}")

    active_counselors = Counselor.objects.filter(is_active=True).count()

    # Get recent activities (last 7 days)
    recent_appointments = Appointment.objects.filter(
        created_at__gte=now() - timedelta(days=7)
    ).order_by('-created_at')[:4]

    # Prepare DASS21 chart data
    dass_data = {
        'depression': DASSResult.objects.aggregate(
            avg=Avg('depression_score'))['avg'], 'anxiety': DASSResult.objects.aggregate(
            avg=Avg('anxiety_score'))['avg'], 'stress': DASSResult.objects.aggregate(
                avg=Avg('stress_score'))['avg'], }

    return render(request, 'admin-panel.html', {
        'total_appointments': total_appointments,
        'high_risk_cases': high_risk_cases,
        'active_counselors': active_counselors,
        'recent_appointments': recent_appointments,
        'dass_data': dass_data,
    })


@staff_member_required
def admin_data(request):
    # Get all colleges with their average DASS scores and student counts
    colleges = CustomUser.COLLEGE_CHOICES
    college_data = []

    for code, name in colleges:
        # Get all users from this college
        users = CustomUser.objects.filter(college=code)
        student_count = users.count()

        # Get DASS results for these users
        results = DASSResult.objects.filter(user__college=code)

        if results.exists():
            # Calculate averages
            depression_avg = results.aggregate(Avg('depression_score'))[
                'depression_score__avg']
            anxiety_avg = results.aggregate(Avg('anxiety_score'))[
                'anxiety_score__avg']
            stress_avg = results.aggregate(Avg('stress_score'))[
                'stress_score__avg']
            overall_avg = (depression_avg + anxiety_avg + stress_avg) / 3

            # Determine severity level
            if overall_avg <= 10:
                severity = 'normal'
            elif overall_avg <= 20:
                severity = 'moderate'
            else:
                severity = 'severe'

            # Get last updated time
            last_updated = results.latest('date_taken').date_taken

            college_data.append({
                'code': code,
                'name': name,
                'student_count': student_count,
                'depression_avg': depression_avg,
                'anxiety_avg': anxiety_avg,
                'stress_avg': stress_avg,
                'overall_avg': overall_avg,
                'severity': severity,
                'last_updated': last_updated,
                # Helper function to assign colors
                'color_rgb': get_college_color(code)
            })

    return render(request, 'admin-data.html', {
        'colleges': college_data,
    })


def get_college_color(college_code):
    """Assign consistent colors to each college"""
    color_map = {
        'CASS': '255, 99, 132',
        'CEN': '54, 162, 235',
        'CBA': '255, 206, 86',
        'COF': '75, 192, 192',
        'CAG': '153, 102, 255',
        'CHSI': '255, 159, 64',
        'CED': '199, 199, 199',
        'COS': '83, 102, 255',
        'CVSM': '40, 167, 69'
    }
    return color_map.get(college_code, '75, 192, 192')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    # Add debugging
    print(f"Appointment list API called by user: {request.user.username}")
    print(f"User is staff: {request.user.is_staff}")
    print(
        f"User has counselor profile: {hasattr(request.user, 'counselor_profile')}")

    # Check if user is staff (admin) or has counselor profile
    if not (
        request.user.is_staff or hasattr(
            request.user,
            'counselor_profile')):
        print("Permission denied - user is not staff or counselor")
        return Response({'error': 'Permission denied'}, status=403)

    upcoming = request.GET.get('upcoming', 'false').lower() == 'true'
    queryset = Appointment.objects.all().select_related(
        'user', 'counselor', 'dass_result')

    if upcoming:
        queryset = queryset.filter(
            status__in=['pending', 'confirmed'],
            date__gte=timezone.now().date()
        ).order_by('date', 'time')

    print(f"Found {queryset.count()} appointments")
    serializer = AppointmentSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    # Check if user is staff (admin) or has counselor profile
    if not (
        request.user.is_staff or hasattr(
            request.user,
            'counselor_profile')):
        return Response({'error': 'Permission denied'}, status=403)

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=404)

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        # Ensure status is lowercase to match choices
        if 'status' in request.data and request.data['status']:
            request.data['status'] = request.data['status'].lower()

        serializer = AppointmentSerializer(
            appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        # Format validation errors
        errors = {}
        for field, error_list in serializer.errors.items():
            errors[field] = [str(error) for error in error_list]
        return Response({'error': 'Validation failed',
                        'details': errors}, status=400)


@staff_member_required
def admin_appointments(request):
    # Add debugging
    print(f"Admin appointments view called by user: {request.user.username}")
    print(f"User is staff: {request.user.is_staff}")
    print(f"User is superuser: {request.user.is_superuser}")

    # You can reuse the same context data as your other admin views
    return render(request, 'admin-appointments.html', {
        'total_appointments': Appointment.objects.count(),
        'high_risk_cases': DASSResult.objects.filter(
            Q(depression_severity__icontains='Severe') |
            Q(depression_severity__icontains='Extremely') |
            Q(anxiety_severity__icontains='Severe') |
            Q(anxiety_severity__icontains='Extremely') |
            Q(stress_severity__icontains='Severe') |
            Q(stress_severity__icontains='Extremely')
        ).distinct().count(),
        'active_counselors': Counselor.objects.filter(is_active=True).count()
    })


@staff_member_required
def admin_personnel(request):
    counselors = Counselor.objects.filter(is_active=True)
    return render(request, 'admin-personnel.html', {
        'counselors': counselors,
        'total_appointments': Appointment.objects.count(),
        'high_risk_cases': DASSResult.objects.filter(
            Q(depression_severity__icontains='Severe') |
            Q(depression_severity__icontains='Extremely') |
            Q(anxiety_severity__icontains='Severe') |
            Q(anxiety_severity__icontains='Extremely') |
            Q(stress_severity__icontains='Severe') |
            Q(stress_severity__icontains='Extremely')
        ).distinct().count(),
        'active_counselors': counselors.count()
    })


@csrf_exempt
@api_staff_required
def list_counselors(request):
    """API endpoint to list all counselors"""
    counselors = Counselor.objects.filter(is_active=True).order_by('name')
    counselors_data = []
    for counselor in counselors:
        image_url = counselor.image.url if counselor.image else None
        if image_url:
            image_url = request.build_absolute_uri(image_url)
        else:
            image_url = request.build_absolute_uri(
                settings.STATIC_URL + 'img/default.jpg')
        counselors_data.append({
            'id': counselor.id,
            'name': counselor.name,
            'email': counselor.email,
            'unit': counselor.unit,
            'rank': counselor.rank,
            'image_url': image_url
        })
    return JsonResponse({'success': True, 'counselors': counselors_data})


@csrf_exempt
@api_staff_required
@require_http_methods(["POST"])
def add_counselor(request):
    try:
        # Handle both form data and JSON requests
        if request.content_type == 'multipart/form-data':
            data = request.POST
            files = request.FILES
        else:
            try:
                data = json.loads(request.body)
                files = None
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data'
                }, status=400)

        # Validate required fields
        required_fields = ['name', 'email', 'unit', 'rank']
        missing_fields = [
            field for field in required_fields if not data.get(field)]

        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Check if email already exists
        if Counselor.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'error': 'A counselor with this email already exists'
            }, status=400)

        if CustomUser.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'error': 'A user with this email already exists'
            }, status=400)

        # Generate a secure random password and setup token
        setup_token = get_random_string(64)
        default_password = get_random_string(12)

        try:
            # First create the user account (inactive by default)
            username = data['email'].split('@')[0]
            user = CustomUser.objects.create_user(
                username=username,
                email=data['email'],
                password=default_password,
                full_name=data['name'],
                is_staff=True,  # Counselors are staff members
                is_superuser=False,  # But not superusers
                is_active=False,  # Inactive until they complete setup
                email_verified=False,
                verification_token=setup_token,
                student_id=f"staff-{get_random_string(8)}",
                age=0,
                gender='Prefer not to say',
                college='CBA',
                program='Staff',
                year_level='4'
            )

            # Then create the counselor
            counselor = Counselor.objects.create(
                name=data['name'],
                email=data['email'],
                unit=data['unit'],
                rank=data['rank'],
                is_active=True,
                user=user
            )

            # Handle image upload if present
            if files and 'photo' in files:
                counselor.image = files['photo']
                counselor.save()

            # Send setup email
            setup_url = request.build_absolute_uri(
                reverse('counselor_setup', kwargs={'token': setup_token})
            )

            html_message = render_to_string(
                'mentalhealth/counselor-setup-email.html',
                {
                    'user': user,
                    'setup_url': setup_url,
                    'temporary_password': default_password})

            plain_message = f"""
            Counselor Account Setup - CalmConnect

            Hello {user.full_name},

            An administrator has created a counselor account for you on CalmConnect.

            Your temporary credentials:
            Username: {user.username}
            Temporary Password: {default_password}

            Please complete your account setup by clicking this link:
            {setup_url}

            This link will expire in 48 hours. If you didn't request this account, please contact the administrator.

            The CalmConnect Team
            """

            send_mail(
                'Complete Your CalmConnect Counselor Account Setup',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            # Build image URL
            image_url = counselor.image.url if counselor.image else None
            if image_url:
                image_url = request.build_absolute_uri(image_url)
            else:
                image_url = request.build_absolute_uri(
                    settings.STATIC_URL + 'img/default.jpg')

            return JsonResponse({
                'success': True,
                'counselor': {
                    'id': counselor.id,
                    'name': counselor.name,
                    'email': counselor.email,
                    'unit': counselor.unit,
                    'rank': counselor.rank,
                    'image_url': image_url
                },
                'message': 'Counselor added successfully. Setup email sent.'
            })

        except IntegrityError as e:
            return JsonResponse({
                'success': False,
                'error': 'Database integrity error occurred'
            }, status=400)
        except Exception as e:
            # Clean up if anything fails
            if 'user' in locals():
                user.delete()
            if 'counselor' in locals() and counselor.id:
                counselor.delete()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@require_http_methods(["POST"])
def update_counselor(request, counselor_id):
    try:
        counselor = Counselor.objects.get(id=counselor_id)

        if request.content_type == 'multipart/form-data':
            data = request.POST
            files = request.FILES
        else:
            try:
                data = json.loads(request.body)
                files = None
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data'
                }, status=400)

        # Update fields
        counselor.name = data.get('name', counselor.name)
        counselor.email = data.get('email', counselor.email)
        counselor.unit = data.get('unit', counselor.unit)
        counselor.rank = data.get('rank', counselor.rank)

        # Handle image upload if present
        if files and 'photo' in files:
            # Delete old image if exists
            if counselor.image:
                default_storage.delete(counselor.image.path)
            counselor.image = files['photo']

        counselor.save()

        # Build image URL
        image_url = counselor.image.url if counselor.image else None
        if image_url:
            image_url = request.build_absolute_uri(image_url)
        else:
            image_url = request.build_absolute_uri(
                settings.STATIC_URL + 'img/default.jpg')

        return JsonResponse({
            'success': True,
            'counselor': {
                'id': counselor.id,
                'name': counselor.name,
                'email': counselor.email,
                'unit': counselor.unit,
                'rank': counselor.rank,
                'image_url': image_url
            },
            'message': 'Counselor updated successfully'
        })

    except Counselor.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Counselor not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@require_http_methods(["POST"])
def archive_counselor(request, counselor_id):
    try:
        counselor = Counselor.objects.get(id=counselor_id)
        counselor.is_active = False
        counselor.save()

        return JsonResponse({
            'success': True,
            'message': 'Counselor archived successfully'
        })
    except Counselor.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Counselor not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
def admin_archive(request):
    active_tab = request.GET.get('tab', 'appointments')

    # Paginate appointments
    archived_appointments = Appointment.objects.filter(
        Q(status='completed') | Q(status='cancelled')
    ).order_by('-date', '-time')
    appointments_paginator = Paginator(archived_appointments, 5)
    appointments_page_number = request.GET.get('appointments_page', 1)
    archived_appointments_page = appointments_paginator.get_page(
        appointments_page_number)

    # Paginate DASS results
    dass_results = DASSResult.objects.all().order_by('-date_taken')
    dass_paginator = Paginator(dass_results, 5)
    dass_page_number = request.GET.get('dass_page', 1)
    dass_results_page = dass_paginator.get_page(dass_page_number)

    # Paginate inactive counselors
    inactive_counselors = Counselor.objects.filter(
        is_active=False).order_by('name')
    counselors_paginator = Paginator(inactive_counselors, 5)
    counselors_page_number = request.GET.get('employees_page', 1)
    inactive_counselors_page = counselors_paginator.get_page(
        counselors_page_number)

    # Paginate archived reports
    archived_reports = Report.objects.filter(
        status__in=['archived', 'completed']).order_by('-created_at')
    reports_paginator = Paginator(archived_reports, 5)
    reports_page_number = request.GET.get('reports_page', 1)
    archived_reports_page = reports_paginator.get_page(reports_page_number)

    return render(request, 'admin-archive.html', {
        'archived_appointments_page': archived_appointments_page,
        'dass_results_page': dass_results_page,
        'inactive_counselors_page': inactive_counselors_page,
        'archived_reports_page': archived_reports_page,
        'active_tab': active_tab,
    })


def counselor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'counselor_profile'):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')

            if 'force_password_change' in request.session:
                del request.session['force_password_change']

            # Redirect based on user type
            if hasattr(request.user, 'counselor_profile'):
                return redirect('counselor_dashboard')
            elif request.user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('index')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'password_change.html', {
        'form': form,
        'force_change': request.session.get('force_password_change', False)
    })


def counselor_setup(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)

        # Check if token is expired (48 hours)
        if (timezone.now() - user.date_joined) > timedelta(hours=48):
            messages.error(
                request,
                "This setup link has expired. Please contact the administrator.")
            return redirect('login')

        if request.method == 'POST':
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                user.email_verified = True
                user.is_active = True
                user.verification_token = None
                user.save()

                update_session_auth_hash(request, user)
                messages.success(
                    request, 'Your account has been successfully set up!')

                # Log them in and redirect to counselor dashboard
                login(request, user)
                return redirect('counselor_dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = PasswordChangeForm(user)

        return render(request, 'mentalhealth/counselor-setup.html', {
            'form': form,
            'token': token,
            'user': user
        })

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid setup link.")
        return redirect('login')


@login_required
def counselor_dashboard(request):
    # Verify this is actually a counselor
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    counselor = request.user.counselor_profile
    today = timezone.now().date()

    # Get appointments for the current week (Monday to Sunday)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Get this week's appointments
    this_week_appointments = Appointment.objects.filter(
        counselor=counselor,
        date__range=[start_of_week, end_of_week],
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')

    # Get pending reports
    pending_reports = Report.objects.filter(
        counselor=counselor,
        status='pending'
    ).order_by('-created_at')[:5]

    # Get weekly session count
    weekly_sessions = Appointment.objects.filter(
        counselor=counselor,
        date__gte=start_of_week,
        status='completed'
    ).count()

    context = {
        'counselor': counselor,
        # Changed variable name but kept template compatibility
        'today_appointments': this_week_appointments,
        'pending_reports': pending_reports,
        'pending_reports_count': pending_reports.count(),
        'weekly_sessions_count': weekly_sessions,
        'week_start': start_of_week,
        'week_end': end_of_week,
    }

    return render(request, 'counselor-panel.html', context)


@login_required
def counselor_schedule(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    counselor = request.user.counselor_profile
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    print(f"Counselor schedule view called for: {counselor.name}")
    print(f"Week range: {start_of_week} to {end_of_week}")

    # Get appointments for the current week, ALL statuses for debugging
    appointments = Appointment.objects.filter(
        counselor=counselor,
        date__range=[start_of_week, end_of_week]
    ).order_by('date', 'time')

    print(f"Found {appointments.count()} appointments for this week")

    # Debug: Check all appointments for this counselor
    all_counselor_appointments = Appointment.objects.filter(
        counselor=counselor).order_by('date', 'time')
    print(
        f"Total appointments for counselor {counselor.name}: {all_counselor_appointments.count()}")
    for appt in all_counselor_appointments:
        print(
            f"  - {appt.user.full_name} on {appt.date} at {appt.time} (status: {appt.status})")

    for appt in appointments:
        print(
            f"  - {appt.user.full_name} on {appt.date} at {appt.time} (status: {appt.status})")

    # Prepare calendar events for FullCalendar
    calendar_events = []
    for appt in appointments:
        time_str = appt.time.strftime('%H:%M:%S') if appt.time else ''
        event = {
            'id': appt.id,
            'title': f"{appt.user.full_name} - {appt.reason} ({appt.status})",
            'start': f"{appt.date}T{time_str}",
            'extendedProps': {
                'studentId': appt.user.id,
                'studentName': appt.user.full_name,
                'college': getattr(appt.user, 'college', ''),
                'program': getattr(appt.user, 'program', ''),
                'sessionType': getattr(appt, 'session_type', ''),
                'status': appt.status,
                'notes': getattr(appt, 'notes', ''),
                'appointmentId': appt.id,
                'type': 'appointment',
            }
        }
        calendar_events.append(event)
        print(f"Created calendar event: {event['title']} on {event['start']}")

    print(f"Total calendar events: {len(calendar_events)}")

    import json
    return render(request, 'counselor-schedule.html', {
        'counselor': counselor,
        'appointments': appointments,
        'week_start': start_of_week,
        'week_end': end_of_week,
        'calendar_events': json.dumps(calendar_events),
    })


@login_required
def counselor_reports(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    counselor = request.user.counselor_profile

    # Get filter parameters
    report_type = request.GET.get('report_type', '')
    date_range = request.GET.get('date_range', '')
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Base queryset - exclude archived and completed reports from main view
    reports = Report.objects.filter(counselor=counselor)
    reports = reports.exclude(status__in=['archived', 'completed'])

    # Apply filters
    if report_type:
        reports = reports.filter(report_type=report_type)

    if status:
        reports = reports.filter(status=status)

    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply date range filter
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            reports = reports.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            reports = reports.filter(created_at__date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            reports = reports.filter(created_at__date__gte=month_ago)
        elif date_range == 'quarter':
            quarter_ago = today - timedelta(days=90)
            reports = reports.filter(created_at__date__gte=quarter_ago)

    # Order by created_at
    reports = reports.order_by('-created_at')

    # Calculate statistics
    total_reports = Report.objects.filter(counselor=counselor).count()
    filtered_reports_count = reports.count()
    pending_reports = reports.filter(status='pending').count()
    urgent_reports = reports.filter(report_type='urgent').count()

    # Get recent reports for display
    recent_reports = list(reports[:10])

    # Only show appointments that are:
    # - pending or confirmed
    session_report_exists = Report.objects.filter(
        appointment=OuterRef('pk'),
        report_type='session'
    )
    appointments = Appointment.objects.filter(
        counselor=counselor,
        status__in=['pending', 'confirmed']
    ).select_related('user').order_by('user__full_name')

    # Remove duplicates by user (keep only one appointment per user for
    # display)
    seen_users = set()
    unique_appointments = []
    for appointment in appointments:
        if appointment.user.id not in seen_users:
            unique_appointments.append(appointment)
            seen_users.add(appointment.user.id)

    students_with_appointments = unique_appointments

    context = {
        'counselor': counselor,
        'reports': recent_reports,
        'total_reports': total_reports,
        'filtered_reports_count': filtered_reports_count,
        'pending_reports': pending_reports,
        'urgent_reports': urgent_reports,
        'students_with_appointments': students_with_appointments,
        'filters': {
            'report_type': report_type,
            'date_range': date_range,
            'priority': priority,
            'status': status,
            'search': search_query,
        }
    }

    return render(
        request,
        'counselor-reports.html',
        context
    )


@login_required
def counselor_archive(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    counselor = request.user.counselor_profile
    # Completed sessions (appointments)
    completed_appointments = Appointment.objects.filter(
        counselor=counselor,
        status='completed'
    ).select_related('user').order_by('-date', '-time')

    # Archived reports
    archived_reports = Report.objects.filter(
        counselor=counselor,
        status='archived'
    ).select_related('user').order_by('-created_at')

    # Completed reports (for backward compatibility)
    completed_reports = Report.objects.filter(
        counselor=counselor,
        status='completed'
    ).select_related('user').order_by('-created_at')

    # Combine all archived and completed reports
    all_archived_reports = list(archived_reports) + list(completed_reports)

    context = {
        'counselor': counselor,
        'completed_appointments': completed_appointments,
        'archived_reports': all_archived_reports,
    }

    return render(request, 'counselor-archive.html', context)


@login_required
def counselor_profile(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    counselor = request.user.counselor_profile

    # Calculate feedback statistics
    feedbacks = Feedback.objects.filter(counselor=counselor, skipped=False)
    total_feedbacks = feedbacks.count()

    # Calculate average ratings
    avg_overall = feedbacks.aggregate(avg=Avg('overall_rating'))['avg'] or 0
    avg_professionalism = feedbacks.aggregate(
        avg=Avg('professionalism_rating'))['avg'] or 0
    avg_helpfulness = feedbacks.aggregate(
        avg=Avg('helpfulness_rating'))['avg'] or 0
    avg_recommend = feedbacks.aggregate(
        avg=Avg('recommend_rating'))['avg'] or 0

    # Calculate overall average rating
    overall_avg = 0
    if total_feedbacks > 0:
        total_rating = avg_overall + avg_professionalism + avg_helpfulness + avg_recommend
        overall_avg = round(total_rating / 4, 1)

    if request.method == 'POST':
        form = CounselorProfileForm(
            request.POST, request.FILES, instance=counselor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('counselor_profile')
    else:
        form = CounselorProfileForm(instance=counselor)

    return render(request, 'counselor-profile.html', {
        'counselor': counselor,
        'form': form,
        'total_feedbacks': total_feedbacks,
        'overall_avg_rating': overall_avg,
        'avg_overall': avg_overall,
        'avg_professionalism': avg_professionalism,
        'avg_helpfulness': avg_helpfulness,
        'avg_recommend': avg_recommend,
    })


@login_required
def create_appointment(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    if request.method == 'POST':
        form = AppointmentForm(request.user.counselor_profile, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.counselor = request.user.counselor_profile
            appointment.save()
            messages.success(request, 'Appointment created successfully!')
            return redirect('counselor_dashboard')
    else:
        form = AppointmentForm(request.user.counselor_profile)

    return render(request, 'create-appointment.html', {
        'form': form
    })


@login_required
def create_report(request):
    if not hasattr(request.user, 'counselor_profile'):
        return redirect('index')

    appointment_id = request.GET.get('appointment')
    initial = {}
    appointment = None
    if appointment_id:
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            # Pre-fill initial data for the report form
            initial = {
                'user': appointment.user.id,
                'appointment': appointment.id,
                'title': f'Session with {appointment.user.full_name} on {appointment.date}',
                'description': appointment.reason or '',
                'report_type': 'session',
            }
        except Appointment.DoesNotExist:
            appointment = None

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.counselor = request.user.counselor_profile

            # Always mark reports as completed when created
            report.status = 'completed'

            if appointment or form.cleaned_data.get('appointment'):
                # Use appointment from GET or from POST data
                if not appointment:
                    try:
                        appointment = Appointment.objects.get(
                            pk=form.cleaned_data['appointment'])
                    except Appointment.DoesNotExist:
                        appointment = None
                if appointment:
                    report.user = appointment.user
                    report.appointment = appointment
                    # Mark appointment as completed and save
                    appointment.status = 'completed'
                    appointment.save()

                    # Send feedback request email
                    print(
                        f"📧 Triggering feedback email for appointment {appointment.id}")
                    print(
                        f"🔍 Debug: appointment status = {appointment.status}")
                    print(
                        f"🔍 Debug: appointment user = {appointment.user.email}")
                    send_feedback_request_email(request, appointment)

            report.save()

            # Create notification for the student if report has a user
            if report.user:
                create_notification(
                    user=report.user,
                    message=f'Your session report with {request.user.counselor_profile.name} has been completed.',
                    notification_type='report',
                    url=reverse('user-profile'))

            messages.success(request, 'Report created successfully!')
            return redirect('counselor_reports')
    else:
        form = ReportForm(initial=initial)

    return render(request, 'create-report.html', {
        'form': form,
        'appointment': appointment
    })


@login_required
def report_detail(request, pk):
    try:
        report = Report.objects.get(pk=pk)
        if not hasattr(
                request.user,
                'counselor_profile') or report.counselor != request.user.counselor_profile:
            return redirect('index')

        return render(request, 'report-detail.html', {
            'report': report
        })
    except Report.DoesNotExist:
        return redirect('counselor_reports')


@login_required
@counselor_required
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def report_api(request, pk=None):
    """API endpoint for report CRUD operations"""
    counselor = request.user.counselor_profile

    if request.method == 'GET':
        if pk:
            try:
                report = Report.objects.get(pk=pk, counselor=counselor)
                return JsonResponse({
                    'success': True,
                    'report': {
                        'id': report.id,
                        'title': report.title,
                        'description': report.description,
                        'report_type': report.report_type,
                        'status': report.status,
                        'user_name': (report.user.full_name
                                    if report.user else None),
                        'created_at': report.created_at.strftime(
                            '%Y-%m-%d %H:%M'),
                        'updated_at': report.updated_at.strftime(
                            '%Y-%m-%d %H:%M')
                    }
                })
            except Report.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Report not found'
                }, status=404)
        else:
            # Get all reports for counselor (excluding archived and completed)
            reports = Report.objects.filter(counselor=counselor).exclude(
                status__in=['archived', 'completed']
            ).order_by('-created_at')
            reports_data = [{
                'id': report.id,
                'title': report.title,
                'description': report.description,
                'report_type': report.report_type,
                'status': report.status,
                'created_at': report.created_at.strftime('%Y-%m-%d'),
                'updated_at': report.updated_at.strftime('%Y-%m-%d %H:%M')
            } for report in reports]
            return JsonResponse({'success': True, 'reports': reports_data})

    elif request.method == 'POST':
        # Create new report
        try:
            data = json.loads(request.body)

            # Get the user if provided
            user = None
            if data.get('user_id'):
                try:
                    user = CustomUser.objects.get(id=data['user_id'])
                except CustomUser.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Student not found'
                    }, status=400)

            # Always set status to completed when creating reports
            status = 'completed'

            report = Report.objects.create(
                counselor=counselor,
                user=user,
                title=data.get('title', ''),
                description=data.get('description', ''),
                report_type=data.get('report_type', 'session'),
                status=status
            )

            # Create notification for the student if report has a user
            if user:
                create_notification(
                    user=user,
                    message=('Your session report with '
                             f'{counselor.name} has been completed.'),
                    notification_type='report',
                    url=reverse('user-profile')
                )

                # Send feedback request email if this is a session report
                print(f"🔍 Debug: report_type = {data.get('report_type')}")
                print(f"🔍 Debug: user = {user}")
                print(f"🔍 Debug: counselor = {counselor}")

                if data.get('report_type') == 'session':
                    print(
                        "✅ Report type is 'session', proceeding with feedback email...")
                    # Find the appointment for this user and counselor
                    # (not completed or cancelled)
                    try:
                        appointment = Appointment.objects.filter(
                            user=user, counselor=counselor).exclude(
                            status__in=[
                                'completed', 'cancelled']).latest('date')
                        print(
                            f"✅ Found appointment {appointment.id} for feedback email")
                        print(
                            f"📊 Found appointment status: {appointment.status}")

                        # Mark as completed
                        appointment.status = 'completed'
                        appointment.save()
                        print(
                            f"✅ Appointment {appointment.id} marked as completed")

                        # Send feedback email
                        print("🔔 Sending feedback email...")
                        send_feedback_request_email(request, appointment)
                        print("✅ Feedback email sent successfully via API simulation")

                    except Appointment.DoesNotExist:
                        print(
                            f"❌ No available appointment found for user {user} and counselor {counselor}")
                        pass  # No appointment found, skip feedback email
                else:
                    print(
                        f"❌ Report type is not 'session': {data.get('report_type')}")

            return JsonResponse({
                'success': True,
                'report': {
                    'id': report.id,
                    'title': report.title,
                    'description': report.description,
                    'report_type': report.report_type,
                    'status': report.status,
                    'user_name': user.full_name if user else None,
                    'created_at': report.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=400)

    elif request.method == 'PUT':
        # Update report
        try:
            report = Report.objects.get(pk=pk, counselor=counselor)
            data = json.loads(request.body)

            if 'title' in data:
                report.title = data['title']
            if 'description' in data:
                report.description = data['description']
            if 'report_type' in data:
                report.report_type = data['report_type']
            if 'status' in data:
                # If status is being set to 'completed', automatically archive
                # it
                if data['status'] == 'completed':
                    report.status = 'archived'
                else:
                    report.status = data['status']

            report.save()

            # Check if the report was automatically archived
            if data.get('status') == 'completed':
                return JsonResponse({
                    'success': True,
                    'message': ('Report completed and automatically archived! '
                                'Completed reports are moved to the archive.'),
                    'status': 'archived'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Report updated successfully'
                })
        except Report.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Report not found'
            }, status=404)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        # Delete report
        try:
            report = Report.objects.get(pk=pk, counselor=counselor)
            report.delete()
            return JsonResponse({
                'success': True,
                'message': 'Report deleted successfully'
            })
        except Report.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Report not found'
            }, status=404)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'error': str(e)}, status=400)


@login_required
def edit_report(request, pk):
    try:
        report = Report.objects.get(pk=pk)
        if not hasattr(
                request.user,
                'counselor_profile') or report.counselor != request.user.counselor_profile:
            return redirect('index')
        if request.method == 'POST':
            form = ReportForm(request.POST, instance=report)
            if form.is_valid():
                form.save()
                messages.success(request, 'Report updated successfully!')
                return redirect('counselor_reports')
        else:
            form = ReportForm(instance=report)
        return render(request, 'create-report.html', {
            'form': form,
            'report': report,
            'edit_mode': True
        })
    except Report.DoesNotExist:
        return redirect('counselor_reports')


def get_notifications(request):
    """Get notifications for the current user"""
    try:
        # Add debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(
            f"get_notifications called. User: {request.user}, Authenticated: {request.user.is_authenticated}")
        print(
            f"get_notifications called. User: {request.user}, Authenticated: {request.user.is_authenticated}")

        # Check if user is authenticated
        if not request.user.is_authenticated:
            print("User not authenticated")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'notifications': [],
                    'count': 0
                }, status=401)
            else:
                return redirect('login')

        # Get notifications from the database
        notifications = Notification.objects.filter(
            user=request.user,
            dismissed=False
        ).order_by('-created_at')[:10]  # Get last 10 notifications

        # Get unread count separately
        unread_count = Notification.objects.filter(
            user=request.user,
            dismissed=False,
            read=False
        ).count()

        # Convert to the format expected by the frontend
        notification_list = []
        for notif in notifications:
            notification_list.append({
                'id': notif.id,
                'type': notif.type,
                'message': notif.message,
                'url': notif.url or '#',
                'time': notif.created_at.strftime('%Y-%m-%d %H:%M'),
                'read': notif.read
            })

        print(f"Total notifications: {len(notification_list)}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # For AJAX requests, return JSON
            logger.debug(
                f"Returning JSON response with {len(notification_list)} notifications")
            print(
                f"Returning JSON response with {len(notification_list)} notifications")
            return JsonResponse({
                'success': True,
                'notifications': notification_list,
                'count': len(notification_list),
                'unread_count': unread_count
            })

        # For regular requests, render a template
        return render(request, 'mentalhealth/notifications.html', {
            'notifications': notification_list
        })
    except Exception as e:
        print(f"Error in get_notifications: {e}")
        import traceback
        traceback.print_exc()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'notifications': [],
                'count': 0
            }, status=500)
        else:
            messages.error(
                request, 'An error occurred while loading notifications')
            return redirect('index')


def login_required_json(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'success': False, 'error': 'Authentication required.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required_json
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def update_schedule(request):
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(
        f"update_schedule called. Authenticated: {request.user.is_authenticated}, User: {request.user}, Method: {request.method}")
    # Permission check: must be a counselor
    if not hasattr(request.user, 'counselor_profile'):
        logger.warning(f"User {request.user} does not have counselor_profile.")
        return JsonResponse(
            {'success': False, 'error': 'Permission denied: not a counselor.'}, status=403)
    counselor = request.user.counselor_profile

    def serialize_day_schedules(day_schedules):
        result = {}
        for day, sched in day_schedules.items():
            result[day] = {
                'start_time': sched.get('start_time') if sched.get('start_time') else None,
                'end_time': sched.get('end_time') if sched.get('end_time') else None}
        return result

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'days': counselor.available_days,
            'start_time': counselor.available_start_time.strftime('%H:%M') if counselor.available_start_time else None,
            'end_time': counselor.available_end_time.strftime('%H:%M') if counselor.available_end_time else None,
            'day_schedules': serialize_day_schedules(counselor.day_schedules)
        })

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}

    if request.method in ['POST', 'PUT']:
        days = data.get('days', [])
        day_schedules = data.get('day_schedules', {})
        if not days:
            return JsonResponse(
                {'success': False, 'error': 'At least one day must be selected'}, status=400)
        processed_schedules = {}
        try:
            for day in days:
                day_schedule = day_schedules.get(day, {})
                start_time = day_schedule.get('start_time')
                end_time = day_schedule.get('end_time')
                if not start_time or not end_time:
                    return JsonResponse(
                        {'success': False, 'error': f'Start and end times are required for {day}'}, status=400)
                if start_time >= end_time:
                    return JsonResponse(
                        {'success': False, 'error': f'End time must be after start time for {day}'}, status=400)
                # Store as strings, not time objects
                processed_schedules[day] = {
                    'start_time': start_time,
                    'end_time': end_time
                }
        except ValueError:
            return JsonResponse(
                {'success': False, 'error': 'Invalid time format. Use HH:MM format.'}, status=400)
        counselor.available_days = days
        counselor.day_schedules = processed_schedules
        counselor.save()
        return JsonResponse({
            'success': True,
            'message': 'Availability updated successfully',
            'days': counselor.available_days,
            'start_time': counselor.available_start_time.strftime('%H:%M') if counselor.available_start_time else None,
            'end_time': counselor.available_end_time.strftime('%H:%M') if counselor.available_end_time else None,
            'day_schedules': serialize_day_schedules(counselor.day_schedules)
        })
    elif request.method == 'DELETE':
        counselor.available_days = []
        counselor.available_start_time = None
        counselor.available_end_time = None
        counselor.save()
        return JsonResponse({'success': True,
                             'message': 'Availability cleared successfully'})


# --- Student-only decorator ---
def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        # You may need to adjust this logic based on your user model
        if not user.is_authenticated or getattr(
                user, 'is_counselor', False) or user.is_staff:
            return JsonResponse(
                {'success': False, 'error': 'Students only.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# Set up logger
logger = logging.getLogger('dass21_ai_feedback')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
# 5 requests per minute per user
@ratelimit(key='user', rate='5/m', block=True)
def ai_feedback(request):
    """
    Accepts DASS21 scores and returns personalized AI-generated feedback using
    OpenAI's API. Expects JSON: { 'depression': int, 'anxiety': int, 'stress': int, 'answers': dict, ... }
    Strictly sanitizes data and enforces student-only access.
    """
    user = request.user
    data = request.data
    depression = data.get('depression')
    anxiety = data.get('anxiety')
    stress = data.get('stress')
    depression_severity = data.get('depression_severity')
    anxiety_severity = data.get('anxiety_severity')
    stress_severity = data.get('stress_severity')
    answers = data.get('answers', {})  # Individual question responses

    # Validate input
    if not all(isinstance(x, int)
               for x in [depression, anxiety, stress] if x is not None):
        logger.warning(f"Invalid DASS21 input from user {user.id}")
        return Response(
            {'success': False, 'error': 'Invalid DASS21 scores.'}, status=400)
    if depression is None or anxiety is None or stress is None:
        logger.warning(f"Missing DASS21 input from user {user.id}")
        return Response(
            {'success': False, 'error': 'Missing DASS21 scores.'}, status=400)

    # Get comprehensive user history for personalization
    user_history = get_user_personalization_data(user)

    # Analyze specific DASS21 responses for targeted feedback
    dass_analysis = analyze_dass21_responses(
        answers, depression, anxiety, stress)

    # Compose a personalized prompt for OpenAI
    prompt = build_dass21_specific_prompt(
        user, depression, anxiety, stress,
        depression_severity, anxiety_severity, stress_severity,
        user_history, dass_analysis
    )

    # Generate mental health tips for moderate/normal scores
    tips_result = generate_mental_health_tips(
        user, depression, anxiety, stress,
        depression_severity, anxiety_severity, stress_severity,
        user_history, dass_analysis
    )

    try:
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        logger.info(
            f"OpenAI API key status: {'Configured' if openai.api_key else 'Not configured'}")
        if not openai.api_key:
            logger.warning(
                "OpenAI API key not configured. Using personalized fallback feedback.")
            # Provide personalized fallback feedback when OpenAI is not
            # configured
            fallback_feedback = generate_dass21_specific_fallback_feedback(
                user, depression, anxiety, stress,
                depression_severity, anxiety_severity, stress_severity,
                user_history, dass_analysis
            )
            # Include tips in fallback response if available
            fallback_tips = tips_result['tips'] if tips_result else None
            return Response({
                'success': True,
                'feedback': fallback_feedback,
                'tips': fallback_tips,
                'source': 'fallback',
                'personalization_level': 'high',
                'dass_analysis': dass_analysis
            })

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive, personalized mental health assistant for university students. Provide empathetic, actionable advice tailored to the student's specific DASS21 responses, academic context, and mental health journey. Always maintain a warm, encouraging tone and provide concrete, actionable steps based on their specific symptoms."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7,
        )
        feedback = response.choices[0].message['content'].strip()
        logger.info(f"Personalized AI feedback generated for user {user.id}")
        # Include tips in response if available
        tips_text = tips_result['tips'] if tips_result else None
        return Response({
            'success': True,
            'feedback': feedback,
            'tips': tips_text,
            'source': 'openai',
            'personalization_level': 'high',
            'dass_analysis': dass_analysis,
            'context_used': {
                'academic_context': bool(user_history['academic_context']),
                'test_history': user_history['test_count'],
                'exercise_preferences': bool(user_history['exercise_preferences']),
                'trend_analysis': bool(user_history['trend_analysis']),
                'dass_specific': True
            }
        })
    except Exception as e:
        logger.error(f"AI feedback error for user {user.id}: {str(e)}")
        # Provide personalized fallback feedback on any error
        fallback_feedback = generate_dass21_specific_fallback_feedback(
            user, depression, anxiety, stress,
            depression_severity, anxiety_severity, stress_severity,
            user_history, dass_analysis
        )
        # Include tips in fallback response if available
        fallback_tips = tips_result['tips'] if tips_result else None
        return Response({
            'success': True,
            'feedback': fallback_feedback,
            'tips': fallback_tips,
            'source': 'fallback',
            'personalization_level': 'high',
            'error': 'OpenAI service temporarily unavailable',
            'dass_analysis': dass_analysis
        })


def analyze_dass21_responses(answers, depression, anxiety, stress):
    """Analyze specific DASS21 responses for targeted feedback"""
    analysis = {
        'depression_symptoms': [],
        'anxiety_symptoms': [],
        'stress_symptoms': [],
        'primary_concerns': [],
        'coping_patterns': [],
        'specific_triggers': []
    }

    # DASS21 question mapping (7 questions per dimension)
    depression_questions = {
        'q3': 'I couldn\'t seem to experience any positive feeling at all',
        'q5': 'I found it difficult to work up the initiative to do things',
        'q10': 'I felt that I had nothing to look forward to',
        'q13': 'I felt down-hearted and blue',
        'q16': 'I was unable to become enthusiastic about anything',
        'q17': 'I felt I wasn\'t worth much as a person',
        'q21': 'I felt that life was meaningless'
    }

    anxiety_questions = {
        'q2': 'I was aware of dryness of my mouth',
        'q4': 'I experienced breathing difficulty (e.g., excessively rapid breathing, breathlessness in the absence of physical exertion)',
        'q7': 'I experienced trembling (e.g., in the hands)',
        'q9': 'I was worried about situations in which I might panic and make a fool of myself',
        'q15': 'I felt I was close to panic',
        'q19': 'I was aware of the action of my heart in the absence of physical exertion (e.g., sense of heart rate increase, heart missing a beat)',
        'q20': 'I felt scared without any good reason'}

    stress_questions = {
        'q1': 'I found it hard to wind down',
        'q6': 'I tended to over-react to situations',
        'q8': 'I felt that I was using a lot of nervous energy',
        'q11': 'I found myself getting agitated',
        'q12': 'I found it difficult to relax',
        'q14': 'I was intolerant of anything that kept me from getting on with what I was doing',
        'q18': 'I felt that I was rather touchy'}

    # Analyze depression responses
    for q_id, question in depression_questions.items():
        if q_id in answers:
            score = answers[q_id]
            if score >= 2:  # Moderate to severe response
                analysis['depression_symptoms'].append({
                    'question': question,
                    'score': score,
                    'severity': 'moderate' if score == 2 else 'severe'
                })

    # Analyze anxiety responses
    for q_id, question in anxiety_questions.items():
        if q_id in answers:
            score = answers[q_id]
            if score >= 2:  # Moderate to severe response
                analysis['anxiety_symptoms'].append({
                    'question': question,
                    'score': score,
                    'severity': 'moderate' if score == 2 else 'severe'
                })

    # Analyze stress responses
    for q_id, question in stress_questions.items():
        if q_id in answers:
            score = answers[q_id]
            if score >= 2:  # Moderate to severe response
                analysis['stress_symptoms'].append({
                    'question': question,
                    'score': score,
                    'severity': 'moderate' if score == 2 else 'severe'
                })

    # Identify primary concerns based on most severe responses
    all_symptoms = analysis['depression_symptoms'] + \
        analysis['anxiety_symptoms'] + analysis['stress_symptoms']
    if all_symptoms:
        # Sort by severity and score
        all_symptoms.sort(
            key=lambda x: (
                x['severity'] == 'severe',
                x['score']),
            reverse=True)
        analysis['primary_concerns'] = all_symptoms[:3]  # Top 3 concerns

    # Analyze coping patterns based on specific responses
    if 'q1' in answers and answers['q1'] >= 2:  # Hard to wind down
        analysis['coping_patterns'].append('difficulty relaxing')
    if 'q12' in answers and answers['q12'] >= 2:  # Difficult to relax
        analysis['coping_patterns'].append('relaxation challenges')
    if 'q6' in answers and answers['q6'] >= 2:  # Over-react to situations
        analysis['coping_patterns'].append('emotional reactivity')
    if 'q18' in answers and answers['q18'] >= 2:  # Rather touchy
        analysis['coping_patterns'].append('sensitivity to criticism')

    # Identify specific triggers
    # Worried about panic situations
    if 'q9' in answers and answers['q9'] >= 2:
        analysis['specific_triggers'].append('social situations')
    if 'q15' in answers and answers['q15'] >= 2:  # Close to panic
        analysis['specific_triggers'].append('panic attacks')
    if 'q5' in answers and answers['q5'] >= 2:  # Difficulty with initiative
        analysis['specific_triggers'].append('motivation challenges')
    if 'q17' in answers and answers['q17'] >= 2:  # Not worth much as a person
        analysis['specific_triggers'].append('self-esteem issues')

    return analysis


def get_user_personalization_data(user):
    """Gather comprehensive user data for personalization"""
    # Get all DASS results for trend analysis
    dass_results = DASSResult.objects.filter(user=user).order_by('-date_taken')

    # Get user's test history
    test_count = dass_results.count()
    if test_count > 1:
        # Get the most recent and previous results for trend analysis
        recent_results = list(dass_results[:3])  # Last 3 tests
        trend_analysis = analyze_dass_trends(recent_results)
    else:
        trend_analysis = None

    # Get academic context
    academic_context = get_academic_context(user)

    # Get relaxation exercise history
    relaxation_history = RelaxationLog.objects.filter(
        user=user).order_by('-timestamp')
    exercise_preferences = analyze_exercise_preferences(relaxation_history)

    return {
        'test_count': test_count,
        'trend_analysis': trend_analysis,
        'academic_context': academic_context,
        'exercise_preferences': exercise_preferences,
        'recent_results': list(dass_results[:3]) if test_count > 0 else []
    }


def analyze_dass_trends(results):
    """Analyze trends in DASS scores over time"""
    if len(results) < 2:
        return None

    trends = {}
    for dimension in ['depression', 'anxiety', 'stress']:
        scores = [getattr(result, f'{dimension}_score') for result in results]
        if len(scores) >= 2:
            change = scores[0] - scores[-1]  # Most recent - oldest
            if change > 2:
                trends[dimension] = 'improving'
            elif change < -2:
                trends[dimension] = 'worsening'
            else:
                trends[dimension] = 'stable'

    return trends


def get_academic_context(user):
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
        'CVSM': 'veterinary clinical work, animal care, and medical studies'}

    if hasattr(user, 'college') and user.college:
        context['college_stressors'] = college_stressors.get(
            user.college, 'academic coursework')

    # Year-level specific challenges
    year_challenges = {
        '1': 'adjusting to university life, building new social networks, and managing increased academic demands',
        '2': 'deepening subject knowledge, balancing extracurricular activities, and preparing for advanced coursework',
        '3': 'handling specialized projects, internships, and career exploration while maintaining academic performance',
        '4': 'completing capstone projects, thesis work, job applications, and transitioning to post-graduation life'}

    if hasattr(user, 'year_level') and user.year_level:
        context['year_challenges'] = year_challenges.get(
            user.year_level, 'academic responsibilities')

    # Age context
    if hasattr(user, 'age') and user.age:
        if 18 <= user.age <= 20:
            context['age_context'] = 'early college years, focusing on independence and identity formation'
        elif 21 <= user.age <= 23:
            context['age_context'] = 'mid-college years, balancing academics with career preparation and relationships'
        else:
            context['age_context'] = 'college experience with unique life circumstances'

    return context


def analyze_exercise_preferences(relaxation_history):
    """Analyze user's preferred relaxation exercises"""
    if not relaxation_history.exists():
        return None

    exercise_counts = {}
    for log in relaxation_history:
        exercise_type = log.exercise_type
        exercise_counts[exercise_type] = exercise_counts.get(
            exercise_type, 0) + 1

    if not exercise_counts:
        return None

    preferred_exercise = max(exercise_counts, key=exercise_counts.get)
    total_sessions = sum(exercise_counts.values())

    return {
        'preferred_exercise': preferred_exercise,
        'total_sessions': total_sessions,
        'exercise_counts': exercise_counts
    }


def build_dass21_specific_prompt(
        user,
        depression,
        anxiety,
        stress,
        depression_severity,
        anxiety_severity,
        stress_severity,
        user_history,
        dass_analysis):
    """Build a DASS21-specific personalized prompt for AI feedback"""

    # Base prompt with current scores
    prompt = f"A university student has completed the DASS21 test with these scores: "
    prompt += f"Depression: {depression} ({depression_severity}), "
    prompt += f"Anxiety: {anxiety} ({anxiety_severity}), "
    prompt += f"Stress: {stress} ({stress_severity}). "

    # Add specific DASS21 analysis
    if dass_analysis['primary_concerns']:
        prompt += f"\n\nSpecific concerns identified from their responses: "
        for i, concern in enumerate(dass_analysis['primary_concerns'][:3], 1):
            prompt += f"{i}. {concern['question']} (severity: {concern['severity']}) "

    if dass_analysis['coping_patterns']:
        prompt += f"\nCoping challenges: {', '.join(dass_analysis['coping_patterns'])}. "

    if dass_analysis['specific_triggers']:
        prompt += f"\nSpecific triggers: {', '.join(dass_analysis['specific_triggers'])}. "

    # Add personalization context
    personalization = []

    # Academic context
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'college_stressors' in context:
            personalization.append(
                f"The student is in {user.get_college_display()} and faces challenges with {context['college_stressors']}.")
        if 'year_challenges' in context:
            personalization.append(
                f"As a {user.get_year_level_display()} student, they're dealing with {context['year_challenges']}.")
        if 'age_context' in context:
            personalization.append(
                f"They are in the {context['age_context']} phase of life.")

    # Test history and trends
    if user_history['test_count'] > 1:
        personalization.append(
            f"This is their {user_history['test_count']}th DASS21 assessment.")
        if user_history['trend_analysis']:
            trends = user_history['trend_analysis']
            trend_desc = []
            for dimension, trend in trends.items():
                if trend == 'improving':
                    trend_desc.append(f"{dimension} scores are improving")
                elif trend == 'worsening':
                    trend_desc.append(f"{dimension} scores are worsening")
            if trend_desc:
                personalization.append(
                    f"Trend analysis shows: {', '.join(trend_desc)}.")

    # Exercise preferences
    if user_history['exercise_preferences']:
        pref = user_history['exercise_preferences']
        personalization.append(
            f"They have completed {pref['total_sessions']} relaxation sessions, with {pref['preferred_exercise']} being their preferred exercise.")

    # Add personalization to prompt
    if personalization:
        prompt += " ".join(personalization) + " "

    # Add gender context if available
    if hasattr(
            user,
            'gender') and user.gender and user.gender != 'Prefer not to say':
        prompt += f"The student identifies as {user.gender.lower()}. "

    # Enhanced final instructions with DASS21-specific guidance
    prompt += ("Provide a personalized, empathetic feedback message (4-5 sentences) that: "
               "1. Acknowledges their specific DASS21 responses and concerns "
               "2. References their academic and personal context "
               "3. Offers specific, actionable advice tailored to their identified symptoms "
               "4. Addresses their specific coping challenges and triggers "
               "5. Suggests relevant resources or coping strategies "
               "6. Maintains a supportive, encouraging tone "
               "7. Provides concrete next steps they can take today "
               "Highlight actionable advice in <b>bold</b> HTML tags. "
               "Include specific suggestions based on their DASS21 responses. "
               "Do not mention AI or that this is automated. "
               "Make the feedback feel like it's coming from someone who understands their specific symptoms and challenges. "
               "Structure the response with: 1) Acknowledgment of specific concerns, 2) Context-specific advice, 3) Actionable steps, 4) Encouragement.")

    return prompt


def generate_dass21_specific_fallback_feedback(
        user,
        depression,
        anxiety,
        stress,
        depression_severity,
        anxiety_severity,
        stress_severity,
        user_history,
        dass_analysis):
    """Generate DASS21-specific personalized fallback feedback when OpenAI is not available"""

    feedback_parts = []

    # Address specific DASS21 concerns first
    if dass_analysis['primary_concerns']:
        primary_concern = dass_analysis['primary_concerns'][0]
        if 'positive feeling' in primary_concern['question'].lower():
            feedback_parts.append(
                "I notice you're having difficulty experiencing positive feelings. <b>Try starting with small activities you once enjoyed, even if just for 5 minutes each day.</b>")
        elif 'initiative' in primary_concern['question'].lower():
            feedback_parts.append(
                "You mentioned struggling with motivation and initiative. <b>Break tasks into tiny steps and celebrate each small completion.</b>")
        elif 'panic' in primary_concern['question'].lower():
            feedback_parts.append(
                "I see you're experiencing panic-related concerns. <b>Practice the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.</b>")
        elif 'worth' in primary_concern['question'].lower():
            feedback_parts.append(
                "You're feeling down about your self-worth. <b>Remember that your value isn't determined by your current struggles.</b>")
        elif 'relax' in primary_concern['question'].lower():
            feedback_parts.append(
                "You're finding it hard to relax. <b>Try progressive muscle relaxation: tense and release each muscle group for 5 seconds.</b>")

    # Address coping patterns
    if 'difficulty relaxing' in dass_analysis['coping_patterns']:
        feedback_parts.append(
            "<b>For relaxation challenges, try setting aside 10 minutes daily for deep breathing or guided meditation.</b>")
    if 'emotional reactivity' in dass_analysis['coping_patterns']:
        feedback_parts.append(
            "<b>When feeling overwhelmed, try the 'STOP' technique: Stop, Take a breath, Observe your thoughts, Proceed mindfully.</b>")

    # Academic context introduction
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'college_stressors' in context:
            feedback_parts.append(
                f"As a {user.get_college_display()} student, you're navigating {context['college_stressors']}.")
        if 'year_challenges' in context:
            feedback_parts.append(
                f"Being a {user.get_year_level_display()} student brings {context['year_challenges']}.")

    # Trend-based feedback
    if user_history['trend_analysis']:
        trends = user_history['trend_analysis']
        improving = [dim for dim, trend in trends.items() if trend ==
                     'improving']
        if improving:
            feedback_parts.append(
                f"It's encouraging to see improvement in your {', '.join(improving)} scores. <b>Continue the strategies that have been working for you.</b>")

    # Current score feedback with DASS21-specific advice
    if depression_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append("Your depression scores suggest significant emotional challenges. <b>Consider reaching out to a counselor or mental health professional for support.</b> <b>Try to maintain a regular sleep schedule and engage in activities you once enjoyed, even if it's just for a few minutes each day.</b>")
    elif depression_severity == 'mild':
        feedback_parts.append(
            "You're showing some signs of depression. <b>Try engaging in activities you usually enjoy and maintain regular social connections.</b> <b>Consider setting small, achievable goals for each day to help build momentum.</b>")

    if anxiety_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append("Your anxiety levels appear elevated. <b>Practice deep breathing exercises and consider talking to a counselor about your concerns.</b> <b>Try the 4-7-8 breathing technique: inhale for 4 counts, hold for 7, exhale for 8.</b>")
    elif anxiety_severity == 'mild':
        feedback_parts.append(
            "You're experiencing some anxiety. <b>Try mindfulness techniques and regular exercise to help manage stress.</b> <b>Consider taking short breaks during study sessions to prevent overwhelm.</b>")

    if stress_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append("Your stress levels are quite high. <b>Prioritize self-care activities and consider seeking professional support to develop coping strategies.</b> <b>Try breaking large tasks into smaller, manageable steps and celebrate each completion.</b>")
    elif stress_severity == 'mild':
        feedback_parts.append(
            "You're experiencing some stress. <b>Try time management techniques and regular breaks to help maintain balance.</b> <b>Consider using a planner to organize your academic and personal responsibilities.</b>")

    # Exercise recommendations based on preferences
    if user_history['exercise_preferences']:
        pref = user_history['exercise_preferences']
        if pref['preferred_exercise'] == 'PMR':
            feedback_parts.append(
                "<b>Consider using Progressive Muscle Relaxation, which you've found helpful before.</b> <b>Try a 10-minute PMR session before studying or before bed.</b>")
        elif pref['preferred_exercise'] == 'EFT':
            feedback_parts.append(
                "<b>Try Emotional Freedom Technique tapping, which has worked well for you in the past.</b> <b>Use EFT when you feel overwhelmed or before important academic tasks.</b>")
        elif pref['preferred_exercise'] == 'Breathing':
            feedback_parts.append(
                "<b>Your breathing exercises have been effective.</b> <b>Try box breathing: 4 counts in, 4 hold, 4 out, 4 hold, repeat for 5 minutes.</b>")

    # College-specific advice
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'college_stressors' in context:
            if 'engineering' in context['college_stressors'].lower():
                feedback_parts.append(
                    "<b>For technical coursework stress, try the Pomodoro Technique: 25 minutes of focused work followed by a 5-minute break.</b>")
            elif 'business' in context['college_stressors'].lower():
                feedback_parts.append(
                    "<b>For case study stress, try discussing complex topics with classmates to gain different perspectives.</b>")
            elif 'arts' in context['college_stressors'].lower():
                feedback_parts.append(
                    "<b>For creative project stress, try free-writing or sketching to unlock creative blocks.</b>")

    # Year-level specific advice
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'year_challenges' in context:
            if '1st' in context['year_challenges']:
                feedback_parts.append(
                    "<b>As a first-year student, focus on building good study habits and finding your support network.</b>")
            elif '4th' in context['year_challenges']:
                feedback_parts.append(
                    "<b>As a graduating student, remember to celebrate your achievements while managing thesis stress.</b>")

    # General encouragement if no specific feedback
    if not feedback_parts:
        feedback_parts.append(
            "Your scores are within normal ranges. <b>Continue practicing good mental health habits and reach out for support if needed.</b> <b>Consider maintaining a gratitude journal to track positive moments.</b>")

    return " ".join(feedback_parts)


def generate_fallback_feedback(
        depression,
        anxiety,
        stress,
        depression_severity,
        anxiety_severity,
        stress_severity):
    """Generate basic feedback when OpenAI is not available"""
    feedback_parts = []

    # Depression feedback
    if depression_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append(
            "Your depression scores suggest you may be experiencing significant emotional challenges. <b>Consider reaching out to a mental health professional or counselor for support.</b>")
    elif depression_severity == 'mild':
        feedback_parts.append(
            "You're showing some signs of depression. <b>Try engaging in activities you usually enjoy and maintain regular social connections.</b>")

    # Anxiety feedback
    if anxiety_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append(
            "Your anxiety levels appear elevated. <b>Practice deep breathing exercises and consider talking to a counselor about your concerns.</b>")
    elif anxiety_severity == 'mild':
        feedback_parts.append(
            "You're experiencing some anxiety. <b>Try mindfulness techniques and regular exercise to help manage stress.</b>")

    # Stress feedback
    if stress_severity in ['moderate', 'severe', 'extremely-severe']:
        feedback_parts.append(
            "Your stress levels are quite high. <b>Prioritize self-care activities and consider seeking professional support to develop coping strategies.</b>")
    elif stress_severity == 'mild':
        feedback_parts.append(
            "You're experiencing some stress. <b>Try time management techniques and regular breaks to help maintain balance.</b>")

    # General encouragement
    if not feedback_parts:
        feedback_parts.append(
            "Your scores are within normal ranges. <b>Continue practicing good mental health habits and reach out for support if needed.</b>")

    return " ".join(feedback_parts)


@login_required
def clear_all_notifications(request):
    """Clear all notifications for the current user"""
    if request.method == 'POST':
        # Mark all notifications as dismissed
        Notification.objects.filter(
            user=request.user,
            dismissed=False
        ).update(dismissed=True)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'All notifications cleared'
            })
        else:
            messages.success(request, 'All notifications cleared')
            return redirect('notifications')

    return redirect('notifications')


@login_required
def clear_notification(request, notification_id):
    """Clear a specific notification for the current user"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=request.user,
                dismissed=False
            )
            notification.dismissed = True
            notification.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notification cleared'
                })
            else:
                messages.success(request, 'Notification cleared')
                return redirect('notifications')
        except Notification.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Notification not found'
                }, status=404)
            else:
                messages.error(request, 'Notification not found')
                return redirect('notifications')

    return redirect('notifications')


@login_required
def feedback_form(request, appointment_id):
    """Display feedback form for completed appointment"""
    try:
        appointment = Appointment.objects.get(
            pk=appointment_id,
            user=request.user,
            status='completed'
        )

        # Check if feedback already exists
        feedback_exists = Feedback.objects.filter(
            appointment=appointment,
            user=request.user
        ).exists()

        if feedback_exists:
            messages.info(
                request,
                'You have already provided feedback for this session.')
            return redirect('user-profile')

        return render(request, 'mentalhealth/feedback.html', {
            'appointment': appointment,
            'appointment_id': appointment.id,
            'counselor': appointment.counselor,
            'appointment_date': appointment.date,
            'appointment_time': appointment.time,
            'appointment_type': ', '.join(appointment.services),
            'duration': '60'  # Default duration, could be made configurable
        })

    except Appointment.DoesNotExist:
        messages.error(
            request,
            'Appointment not found or you do not have permission to provide feedback.')
        return redirect('user-profile')


@require_http_methods(["POST"])
@login_required
def submit_feedback(request):
    """Handle feedback submission"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')

        appointment = Appointment.objects.get(
            pk=appointment_id,
            user=request.user,
            status='completed'
        )

        # Check if feedback already exists
        if Feedback.objects.filter(
                appointment=appointment,
                user=request.user).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Feedback already submitted for this appointment.'
            })

        # Create feedback object
        feedback = Feedback.objects.create(
            appointment=appointment,
            user=request.user,
            counselor=appointment.counselor,
            overall_rating=data.get('overall_rating'),
            professionalism_rating=data.get('professionalism_rating'),
            helpfulness_rating=data.get('helpfulness_rating'),
            recommend_rating=data.get('recommend_rating'),
            positive_feedback=data.get('positive_feedback', ''),
            improvement_feedback=data.get('improvement_feedback', ''),
            additional_comments=data.get('additional_comments', ''),
            skipped=False
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Feedback submitted successfully!'
        })

    except Appointment.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Appointment not found.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


@require_http_methods(["POST"])
@login_required
def skip_feedback(request):
    """Handle feedback skip"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')

        appointment = Appointment.objects.get(
            pk=appointment_id,
            user=request.user,
            status='completed'
        )

        # Check if feedback already exists
        if Feedback.objects.filter(
                appointment=appointment,
                user=request.user).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Feedback already submitted for this appointment.'
            })

        # Create feedback object with skipped=True
        feedback = Feedback.objects.create(
            appointment=appointment,
            user=request.user,
            counselor=appointment.counselor,
            skipped=True
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Feedback skipped successfully!'
        })

    except Appointment.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Appointment not found.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


@login_required
def create_live_session(request, appointment_id):
    """Create a live session for an appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        # Check if user has permission to create session
        if not (request.user == appointment.user or
                (hasattr(request.user, 'counselor_profile') and
                 request.user.counselor_profile == appointment.counselor)):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Check if session already exists
        if hasattr(appointment, 'live_session'):
            return JsonResponse({
                'success': True,
                'session_id': appointment.live_session.room_id,
                'message': 'Session already exists'
            })

        # Create live session
        start_time = datetime.combine(appointment.date, appointment.time)
        end_time = start_time + timedelta(hours=1)  # Default 1-hour session

        live_session = LiveSession.objects.create(
            appointment=appointment,
            scheduled_start=start_time,
            scheduled_end=end_time,
            session_type='video'
        )

        # Generate room ID
        room_id = live_session.generate_room_id()

        return JsonResponse({
            'success': True,
            'session_id': room_id,
            'meeting_url': f'/live-session/{room_id}/'
        })

    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def join_live_session(request, room_id):
    """Join a live session"""
    try:
        live_session = LiveSession.objects.get(room_id=room_id)

        # Check if user has permission to join
        if not (request.user == live_session.appointment.user or
                (hasattr(request.user, 'counselor_profile') and
                 request.user.counselor_profile == live_session.appointment.counselor)):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Check if session is active
        if live_session.status not in ['scheduled', 'waiting', 'active']:
            return JsonResponse(
                {'error': 'Session is not available'}, status=400)

        # Update session status if needed
        if live_session.status == 'scheduled':
            live_session.status = 'waiting'
            live_session.save()

        # Create participant record
        participant, created = SessionParticipant.objects.get_or_create(
            session=live_session, user=request.user, defaults={
                'role': 'counselor' if hasattr(
                    request.user, 'counselor_profile') else 'student'})

        return JsonResponse({
            'success': True,
            'session_data': {
                'room_id': room_id,
                'session_type': live_session.session_type,
                'status': live_session.status,
                'participant_role': participant.role
            }
        })

    except LiveSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def live_session_view(request, room_id):
    """Render the live session interface"""
    try:
        # Try to get existing live session
        live_session = LiveSession.objects.get(room_id=room_id)
    except LiveSession.DoesNotExist:
        # If room_id follows the pattern 'appointment_X', try to create from
        # appointment
        if room_id.startswith('appointment_'):
            try:
                appointment_id = int(room_id.split('_')[1])
                appointment = Appointment.objects.get(id=appointment_id)

                # Check if user has permission to access this appointment
                if not (request.user == appointment.user or
                        (hasattr(request.user, 'counselor_profile') and
                         request.user.counselor_profile == appointment.counselor)):
                    return redirect('index')

                # Create live session for this appointment
                start_time = timezone.make_aware(
                    datetime.combine(
                        appointment.date,
                        appointment.time))
                end_time = start_time + timedelta(hours=1)

                live_session = LiveSession.objects.create(
                    appointment=appointment,
                    room_id=room_id,
                    scheduled_start=start_time,
                    scheduled_end=end_time,
                    session_type='video',
                    status='scheduled'
                )
            except (ValueError, Appointment.DoesNotExist):
                return redirect('index')
        else:
            return redirect('index')

    # Check if user has permission to access
    if not (request.user == live_session.appointment.user or
            (hasattr(request.user, 'counselor_profile') and
             request.user.counselor_profile == live_session.appointment.counselor)):
        return redirect('index')

    return render(request, 'mentalhealth/live-session.html', {
        'live_session': live_session,
        'appointment': live_session.appointment,
        'user': request.user
    })


@login_required
def end_live_session(request, room_id):
    """End a live session"""
    try:
        live_session = LiveSession.objects.get(room_id=room_id)

        # Check if user has permission to end session
        if not (request.user == live_session.appointment.user or
                (hasattr(request.user, 'counselor_profile') and
                 request.user.counselor_profile == live_session.appointment.counselor)):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Update session status
        live_session.status = 'completed'
        live_session.actual_end = timezone.now()
        live_session.save()

        # Update appointment status
        appointment = live_session.appointment
        appointment.status = 'completed'
        appointment.save()

        return JsonResponse({'success': True})

    except LiveSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_session_messages(request, room_id):
    """Get chat messages for a session"""
    try:
        live_session = LiveSession.objects.get(room_id=room_id)

        # Check if user has permission
        if not (request.user == live_session.appointment.user or
                (hasattr(request.user, 'counselor_profile') and
                 request.user.counselor_profile == live_session.appointment.counselor)):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        messages = SessionMessage.objects.filter(
            session=live_session).order_by('timestamp')
        messages_data = [{
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
            'message_type': msg.message_type
        } for msg in messages]

        return JsonResponse({'messages': messages_data})

    except LiveSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)


@login_required
def update_session_notes(request, room_id):
    """Update session notes"""
    try:
        live_session = LiveSession.objects.get(room_id=room_id)

        # Only counselors can update notes
        if not (hasattr(request.user, 'counselor_profile') and
                request.user.counselor_profile == live_session.appointment.counselor):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        if request.method == 'POST':
            data = json.loads(request.body)
            live_session.notes = data.get('notes', '')
            live_session.save()

            return JsonResponse({'success': True})

        return JsonResponse({'notes': live_session.notes})

    except LiveSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def test_video_call(request, appointment_id):
    """Test view to verify video call functionality"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        # Check if user has permission
        if not (request.user == appointment.user or
                (hasattr(request.user, 'counselor_profile') and
                 request.user.counselor_profile == appointment.counselor)):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Get or create live session
        live_session, created = LiveSession.objects.get_or_create(
            appointment=appointment,
            defaults={
                'room_id': f'appointment_{appointment.id}',
                'scheduled_start': timezone.now(),
                'scheduled_end': timezone.now() + timedelta(hours=1),
                'session_type': 'video',
                'status': 'scheduled'
            }
        )

        video_call_url = request.build_absolute_uri(
            reverse('live_session_view', kwargs={'room_id': live_session.room_id})
        )

        return render(request, 'mentalhealth/test-video-call.html', {
            'appointment': appointment,
            'live_session': live_session,
            'video_call_url': video_call_url
        })

    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)


@login_required
def websocket_test(request):
    """Test WebSocket connection"""
    return render(request, 'mentalhealth/websocket-test.html')


@login_required
def simple_websocket_test(request):
    """Simple WebSocket test page"""
    return render(request, 'mentalhealth/simple-websocket-test.html')


def generate_mental_health_tips(
        user,
        depression,
        anxiety,
        stress,
        depression_severity,
        anxiety_severity,
        stress_severity,
        user_history,
        dass_analysis):
    """Generate specific mental health tips for moderate/normal scores using OpenAI"""

    # Check if any severity is moderate or normal/mild
    moderate_normal_severities = ['normal', 'mild', 'moderate']
    has_moderate_normal = (
        depression_severity in moderate_normal_severities or
        anxiety_severity in moderate_normal_severities or
        stress_severity in moderate_normal_severities
    )

    if not has_moderate_normal:
        return None

    # Build tips-specific prompt
    prompt = f"Generate 5-7 practical, actionable mental health tips for a university student with DASS21 scores: "
    prompt += f"Depression: {depression} ({depression_severity}), "
    prompt += f"Anxiety: {anxiety} ({anxiety_severity}), "
    prompt += f"Stress: {stress} ({stress_severity}). "

    # Add specific concerns
    if dass_analysis['primary_concerns']:
        prompt += f"\n\nKey concerns from their responses: "
        for concern in dass_analysis['primary_concerns'][:3]:
            prompt += f"- {concern['question']} "

    # Add personalization
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'college_stressors' in context:
            prompt += f"\n\nAcademic context: Student is in {user.get_college_display()} facing {context['college_stressors']}."
        if 'year_challenges' in context:
            prompt += f" As a {user.get_year_level_display()} student, they're dealing with {context['year_challenges']}."

    # Add exercise preferences
    if user_history['exercise_preferences']:
        pref = user_history['exercise_preferences']
        prompt += f"\n\nThey've completed {pref['total_sessions']} relaxation sessions, preferring {pref['preferred_exercise']}."

    prompt += ("\n\nGenerate tips that are: "
               "1. Specific to their DASS21 scores and concerns "
               "2. Tailored to university student life "
               "3. Practical and immediately actionable "
               "4. Focused on prevention and maintenance for moderate/normal mental health "
               "5. Include a mix of academic, social, and self-care strategies "
               "6. Number them 1-7 and keep each tip concise (1-2 sentences) "
               "7. Use encouraging, supportive language "
               "8. Avoid medical advice or diagnosis "
               "Format as a bulleted list with <b>bold</b> key actions.")

    try:
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not openai.api_key:
            logger.warning("OpenAI API key not configured for tips generation")
            return generate_fallback_tips(
                user,
                depression,
                anxiety,
                stress,
                depression_severity,
                anxiety_severity,
                stress_severity,
                user_history,
                dass_analysis)

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
        logger.info(f"AI-generated tips created for user {user.id}")
        return {
            'tips': tips,
            'source': 'openai',
            'generated_for': 'moderate_normal'
        }
    except Exception as e:
        logger.error(f"Tips generation error for user {user.id}: {str(e)}")
        return generate_fallback_tips(
            user,
            depression,
            anxiety,
            stress,
            depression_severity,
            anxiety_severity,
            stress_severity,
            user_history,
            dass_analysis)


def generate_fallback_tips(
        user,
        depression,
        anxiety,
        stress,
        depression_severity,
        anxiety_severity,
        stress_severity,
        user_history,
        dass_analysis):
    """Generate fallback tips when OpenAI is not available"""

    tips = []

    # Depression tips for moderate/normal
    if depression_severity in ['mild', 'moderate', 'normal']:
        tips.extend([
            "1. <b>Maintain a consistent sleep schedule</b> of 7-9 hours per night to support emotional regulation.",
            "2. <b>Practice daily gratitude</b> by noting 3 things you're thankful for each evening.",
            "3. <b>Stay connected with friends</b> through regular social activities, even small ones like coffee chats."
        ])

    # Anxiety tips for moderate/normal
    if anxiety_severity in ['mild', 'moderate', 'normal']:
        tips.extend([
            "4. <b>Use the 4-7-8 breathing technique</b>: inhale for 4 counts, hold for 7, exhale for 8 when feeling anxious.",
            "5. <b>Break tasks into smaller steps</b> to reduce overwhelm and build momentum.",
            "6. <b>Practice progressive muscle relaxation</b> for 10 minutes daily to release physical tension."
        ])

    # Stress tips for moderate/normal
    if stress_severity in ['mild', 'moderate', 'normal']:
        tips.extend([
            "7. <b>Try the Pomodoro Technique</b>: 25 minutes focused work followed by 5-minute breaks.",
            "8. <b>Incorporate short walks</b> between classes to clear your mind and reduce stress.",
            "9. <b>Set boundaries</b> around study time and leisure time to maintain work-life balance."
        ])

    # Academic-specific tips
    if user_history['academic_context']:
        context = user_history['academic_context']
        if 'college_stressors' in context:
            if 'engineering' in context['college_stressors'].lower():
                tips.append(
                    "10. <b>For technical coursework</b>, schedule regular review sessions to prevent last-minute stress.")
            elif 'business' in context['college_stressors'].lower():
                tips.append(
                    "10. <b>For case studies</b>, discuss complex topics with classmates to gain different perspectives.")
            elif 'arts' in context['college_stressors'].lower():
                tips.append(
                    "10. <b>For creative projects</b>, set aside time for free-writing or sketching to overcome blocks.")

    # Exercise preference tips
    if user_history['exercise_preferences']:
        pref = user_history['exercise_preferences']
        if pref['preferred_exercise'] == 'PMR':
            tips.append(
                "11. <b>Continue with Progressive Muscle Relaxation</b> - it's working well for you!")
        elif pref['preferred_exercise'] == 'EFT':
            tips.append(
                "11. <b>Use Emotional Freedom Technique tapping</b> when you need quick stress relief.")
        elif pref['preferred_exercise'] == 'Breathing':
            tips.append(
                "11. <b>Build on your breathing exercises</b> with longer sessions for deeper relaxation.")

    # Limit to 7 tips and format
    final_tips = tips[:7]
    formatted_tips = "\n".join(final_tips)

    return {
        'tips': formatted_tips,
        'source': 'fallback',
        'generated_for': 'moderate_normal'
    }
