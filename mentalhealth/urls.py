from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .decorators import counselor_required  # Import the decorator
from .views import send_confirmation_email
from .views import force_logout
from .views import appointment_list
from .views import appointment_detail
from .views import counselor_setup
from .views import create_live_session
from .views import join_live_session
from .views import live_session_view
from .views import end_live_session
from .views import get_session_messages
from .views import update_session_notes
from .views import test_view
# from .views import update_counselor

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user-profile'),
    path('dass21-test/', views.dass21_test, name='dass21_test'),

    # Counselor-specific URLs (protected with decorator)
    path('counselor-dashboard/',
         counselor_required(views.counselor_dashboard),
         name='counselor_dashboard'),
    path('counselor/schedule/',
         counselor_required(views.counselor_schedule),
         name='counselor_schedule'),
    path('counselor/reports/',
         counselor_required(views.counselor_reports),
         name='counselor_reports'),
    path('counselor/archive/',
         counselor_required(views.counselor_archive),
         name='counselor_archive'),
    path('counselor/profile/',
         counselor_required(views.counselor_profile),
         name='counselor_profile'),
    path('counselor/appointment/<int:pk>/',
         views.appointment_detail,
         name='counselor_appointment_detail'),
    path('counselor/setup/<str:token>/', counselor_setup,
         name='counselor_setup'),

    # Appointment URLs
    path('appointments/create/',
          counselor_required(views.create_appointment),
          name='create_appointment'),
    path('appointments/<int:pk>/',
          counselor_required(views.appointment_detail),
          name='appointment_detail'),
    path('appointments/<int:pk>/view/',
          counselor_required(views.appointment_detail_view),
          name='appointment_detail_view'),
    path('counselor/appointment/<int:pk>/',
          counselor_required(views.appointment_detail),
          name='counselor_appointment_detail'),

    # Report URLs
    path('reports/create/',
         counselor_required(views.create_report),
         name='create_report'),
    path('reports/<int:pk>/',
         counselor_required(views.report_detail),
         name='report_detail'),
    path('reports/<int:pk>/export/<str:format_type>/',
         counselor_required(views.report_export),
         name='report_export'),
    path('reports/<int:pk>/request-followup/',
         views.request_followup,
         name='request_followup'),
    path('reports/<int:pk>/edit/',
         counselor_required(views.edit_report),
         name='edit_report'),
    path('api/reports/',
         views.report_api,
         name='report_api'),
    path('api/reports/<int:pk>/',
         views.report_api,
         name='report_api_detail'),
    path('api/reports/export/',
         counselor_required(views.export_reports),
         name='export_reports'),

    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-appointments/', views.admin_appointments,
          name='admin_appointments'),
    path('admin-personnel/', views.admin_personnel, name='admin_personnel'),
    path('admin-archive/', views.admin_archive, name='admin_archive'),
    path('admin-followup-requests/', views.admin_followup_requests,
          name='admin_followup_requests'),
    path('admin-followup-requests/<int:request_id>/approve-deny/',
          views.approve_deny_followup, name='approve_deny_followup'),

    # API Endpoints
    path('api/welcome/', views.welcome_api, name='welcome_api'),
    path('api/welcome-logging/', views.welcome_with_logging, name='welcome_with_logging'),
    path('api/welcome-logged/', views.welcome, name='welcome_logged'),
    path('api/welcome-new/', views.welcome_new, name='welcome_new'),
    path('api/welcome-metadata/', views.welcome_with_metadata, name='welcome_with_metadata'),
    path('api/welcome-method-path/', views.welcome_with_method_path_logging, name='welcome_with_method_path_logging'),
    path('api/health/', views.health_check, name='health_check'),
    path('api/appointments/', appointment_list, name='appointment-list'),
    path('api/appointments/<pk>', appointment_detail,
          name='appointment-detail'),
    path('api/appointments/<pk>/', appointment_detail,
          name='appointment-detail-slash'),
    path('api/test/', views.test_view, name='test'),
    path('api/appointment-detail/<int:pk>/', views.appointment_detail_api,
         name='appointment-detail-api'),
    path('api/counselors/', views.add_counselor, name='add_counselor'),
    path('api/counselors/<int:counselor_id>/', views.update_counselor,
         name='update_counselor'),
    path('api/counselors/<int:counselor_id>/archive/', views.archive_counselor,
         name='archive_counselor'),
    path('api/ai-feedback/', views.ai_feedback, name='ai_feedback'),
    path('api/generate-tips/', views.generate_ai_tips, name='generate_ai_tips'),

    # Archive API endpoints
    path('api/archive/stats/', counselor_required(views.archive_stats), name='archive_stats'),
    path('api/archive/data/', counselor_required(views.archive_data), name='archive_data'),
    path('api/archive/export/', counselor_required(views.archive_export), name='archive_export'),

    # Other URLs
    path('save-dass-results/', views.save_dass_results, name='save_dass_results'),
    path('validate-field/', views.validate_field_ajax, name='validate_field_ajax'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verify-prompt/', views.verify_prompt, name='verify_prompt'),
    path('resend-verification/', views.resend_verification,
         name='resend_verification'),
    path('scheduler/', views.scheduler, name='scheduler'),
    path('get-slots/<int:counselor_id>/', views.get_counselor_slots,
         name='get_slots'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('send-appointment-email/', send_confirmation_email,
         name='send-email'),
    path('cancel/<str:token>/', views.cancel_appointment, name='cancel_appointment'),
    path('force-logout/', force_logout, name='force_logout'),
    path('admin-data/', views.admin_data, name='admin_data'),
    path('schedule/update/', views.update_schedule, name='update_schedule'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/clear-all/', views.clear_all_notifications,
         name='clear_all_notifications'),
    path('notifications/<int:notification_id>/clear/', views.clear_notification,
         name='clear_notification'),
    
    # Feedback URLs
    path('feedback/<int:appointment_id>/', views.feedback_form,
         name='feedback_form'),
    path('submit-feedback/', views.submit_feedback,
         name='submit_feedback'),
    path('skip-feedback/', views.skip_feedback,
         name='skip_feedback'),

    # Live Session URLs
    path('live-session/create/<int:appointment_id>/', create_live_session,
          name='create_live_session'),
    path('live-session/join/<str:room_id>/', join_live_session,
          name='join_live_session'),
    path('live-session/<str:room_id>/', live_session_view,
          name='live_session_view'),
    path('live-session/<str:room_id>/end/', end_live_session,
          name='end_live_session'),
    path('live-session/<str:room_id>/messages/', get_session_messages,
          name='get_session_messages'),
    path('live-session/<str:room_id>/notes/', update_session_notes,
          name='update_session_notes'),
    path('test-video-call/<int:appointment_id>/',
          views.test_video_call,
          name='test_video_call'),
    path('websocket-test/', views.websocket_test, name='websocket_test'),
    path('simple-websocket-test/', views.simple_websocket_test,
          name='simple_websocket_test'),

    # Follow-up URLs
    path('followup/<int:request_id>/schedule/',
          counselor_required(views.schedule_followup),
          name='schedule_followup'),
    path('followup/<int:request_id>/consent/',
          views.accept_followup,
          name='accept_followup'),
    path('followup/<int:request_id>/details/',
          counselor_required(views.followup_details),
          name='followup_details'),
    path('followup-sessions/',
          views.followup_sessions,
          name='followup_sessions'),
    path('followup-session/<int:appointment_id>/',
          views.followup_session,
          name='followup_session'),
    path('submit-followup/',
          views.submit_followup,
          name='submit_followup'),

    # Password Reset URLs
    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    # Settings API URLs
    path('api/settings/', views.user_settings_api, name='user_settings_api'),
    path('api/settings/reset/', views.reset_settings_api, name='reset_settings_api'),

    # Temporary migration endpoint for Railway
    path('run-migrations/', views.run_migrations, name='run_migrations'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)