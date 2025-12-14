from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import BaseUserManager
from django.utils.crypto import get_random_string


def get_default_counselor():
    """Get the first available counselor or create a default one"""
    # This will be handled in the migration or view logic
    return 1  # Return a default ID for now


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('The Email must be set')
            
        email = self.normalize_email(email)
        
        # Handle staff users differently
        if extra_fields.get('is_staff'):
            if 'student_id' not in extra_fields:
                extra_fields['student_id'] = f"staff-{get_random_string(8)}"
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        # Set default values for required fields
        extra_fields.setdefault('age', 0)
        extra_fields.setdefault('student_id', 'admin000')
        extra_fields.setdefault('full_name', 'Admin User')
        extra_fields.setdefault('gender', 'Prefer not to say')
        extra_fields.setdefault('college', 'CBA')
        extra_fields.setdefault('program', 'Administration')
        extra_fields.setdefault('year_level', '4')
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def generate_verification_token(self):
        if not self.verification_token:
            self.verification_token = get_random_string(64)
            self.save()
        return self.verification_token

    # Fix indentation for these fields
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    # Your existing custom fields
    age = models.PositiveIntegerField(null=True, blank=True)
    full_name = models.CharField(max_length=255)

    GENDER_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Non-binary', 'Non-binary'),
        ('Prefer not to say', 'Prefer not to say'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    COLLEGE_CHOICES = [
        ('CASS', 'College of Arts and Social Sciences'),
        ('CEN', 'College of Engineering'),
        ('CBA', 'College of Business Administration'),
        ('COF', 'College of Fisheries'),
        ('CAG', 'College of Agriculture'),
        ('CHSI', 'College of Home Science and Industry'),
        ('CED', 'College of Education'),
        ('COS', 'College of Sciences'),
        ('CVSM', 'College of Veterinary Science and Medicine'),
    ]
    college = models.CharField(max_length=10, choices=COLLEGE_CHOICES)
    program = models.CharField(max_length=255)

    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]
    year_level = models.CharField(max_length=2, choices=YEAR_CHOICES)
    profile_picture = models.ImageField(upload_to='users/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} - {self.full_name}"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'custom_user'


class DASSResult(models.Model):
    # FIXED: Changed from User to settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    # Raw scores (multiplied by 2 for DASS-21)
    depression_score = models.IntegerField()
    anxiety_score = models.IntegerField()
    stress_score = models.IntegerField()
    # Severity levels
    depression_severity = models.CharField(max_length=50)
    anxiety_severity = models.CharField(max_length=50)
    stress_severity = models.CharField(max_length=50)
    # Store all answers as JSON
    answers = models.JSONField()

    # Follow-up assessment fields
    is_followup = models.BooleanField(default=False, help_text="Whether this is a follow-up assessment")
    followup_appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='followup_assessments',
        help_text="The follow-up appointment this assessment is for"
    )

    def __str__(self):
        return (
            f"DASS-21 Results for {self.user.username} on "
            f"{self.date_taken}"
        )


class RelaxationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise_type = models.CharField(max_length=100)
    duration_seconds = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class Counselor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    unit = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='counselors/', blank=True, null=True)
    available_days = models.JSONField(default=list)
    available_start_time = models.TimeField(null=True, blank=True)
    available_end_time = models.TimeField(null=True, blank=True)
    # New field for individual day schedules
    day_schedules = models.JSONField(
        default=dict, 
        help_text="Individual schedules for each day"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='counselor_profile',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('counselor', 'Cancelled'),
        ('cancelled', 'Cancelled'),
    ]
    
    SESSION_TYPE_CHOICES = [
        ('face_to_face', 'Face-to-Face'),
        ('remote', 'Remote/Online'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    counselor = models.ForeignKey(
        'Counselor',
        on_delete=models.PROTECT,
        default=get_default_counselor
    )
    date = models.DateField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    time = models.TimeField()
    services = models.JSONField()
    reason = models.TextField()
    phone = models.CharField(max_length=20)
    course_section = models.CharField(max_length=100)
    session_type = models.CharField(
        max_length=20, 
        choices=SESSION_TYPE_CHOICES, 
        default='face_to_face',
        help_text="Type of counseling session"
    )
    video_call_url = models.URLField(
        blank=True, 
        null=True,
        help_text="Video call URL for remote sessions"
    )
    dass_result = models.ForeignKey(
        DASSResult, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_deadline = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_token = models.CharField(
        max_length=64, unique=True, null=True, blank=True
    )

    def __str__(self):
        return (
            f"Appointment for {self.user.full_name} with "
            f"{self.counselor.name} on {self.date} at {self.time}"
        )


class Report(models.Model):
    REPORT_TYPES = [
        ('assessment', 'Assessment Report'),
        ('session', 'Session Report'),
        ('urgent', 'Urgent Report'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('draft', 'Draft'),
    ]
    counselor = models.ForeignKey(
        Counselor, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.get_report_type_display()} - {self.title}"
        )


class FollowupRequest(models.Model):
    """Model for follow-up session requests from reports"""
    STATUS_CHOICES = [
        ('pending', 'Pending Admin Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    REQUESTER_CHOICES = [
        ('counselor', 'Counselor'),
        ('student', 'Student'),
    ]

    # Relationships
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='followup_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followup_requests_made'
    )
    requester_type = models.CharField(
        max_length=10,
        choices=REQUESTER_CHOICES
    )

    # Request details
    reason = models.TextField(help_text="Reason for requesting follow-up")
    requested_date = models.DateField(null=True, blank=True, help_text="Preferred date for follow-up")
    requested_time = models.TimeField(null=True, blank=True, help_text="Preferred time for follow-up")

    # Admin approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(blank=True, help_text="Admin review notes")
    approved_denied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='followup_requests_reviewed'
    )
    approved_denied_at = models.DateTimeField(null=True, blank=True)

    # Final scheduling (set by counselor after approval)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    session_type = models.CharField(
        max_length=20,
        choices=[
            ('face_to_face', 'Face-to-Face'),
            ('remote', 'Remote/Online'),
        ],
        default='face_to_face'
    )

    # Resulting appointment (created after scheduling)
    resulting_appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='followup_request'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Follow-up Request'
        verbose_name_plural = 'Follow-up Requests'

    def __str__(self):
        return f"Follow-up request for {self.report.title} by {self.requested_by.full_name}"

    @property
    def student(self):
        """Get the student involved in this follow-up request"""
        return self.report.user

    @property
    def counselor(self):
        """Get the counselor involved in this follow-up request"""
        return self.report.counselor

    @property
    def can_be_scheduled(self):
        """Check if this request can be scheduled (approved but not yet scheduled)"""
        return self.status == 'approved' and not self.scheduled_date

    @property
    def can_be_approved_denied(self):
        """Check if this request can be approved/denied by admin"""
        return self.status == 'pending'


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('report', 'Report'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
        ('feedback', 'Feedback'),
        ('followup', 'Follow-up'),
        ('general', 'General'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default='general'
    )
    category = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default='general'
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='normal'
    )
    url = models.CharField(max_length=255, blank=True, null=True)
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    read = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read', 'dismissed']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_icon(self):
        """Get appropriate icon for notification type"""
        icons = {
            'appointment': 'bx-calendar',
            'report': 'bx-file',
            'system': 'bx-cog',
            'reminder': 'bx-bell',
            'feedback': 'bx-message-dots',
            'general': 'bx-info-circle',
        }
        return icons.get(self.type, 'bx-info-circle')
    
    def get_color(self):
        """Get appropriate color for notification priority"""
        colors = {
            'low': '#6c757d',
            'normal': '#007bff',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        return colors.get(self.priority, '#007bff')


class Feedback(models.Model):
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    counselor = models.ForeignKey(
        'Counselor',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    
    # Rating fields (1-5 stars)
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    professionalism_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    helpfulness_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    recommend_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    # Text feedback
    positive_feedback = models.TextField(blank=True)
    improvement_feedback = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    skipped = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['appointment', 'user']  # One feedback per appointment per user
    
    def __str__(self):
        return f"Feedback for {self.appointment} by {self.user.full_name}"
    
    @property
    def has_ratings(self):
        """Check if any ratings were provided"""
        return any([
            self.overall_rating,
            self.professionalism_rating,
            self.helpfulness_rating,
            self.recommend_rating
        ])
    
    @property
    def average_rating(self):
        """Calculate average rating from all provided ratings"""
        ratings = [r for r in [
            self.overall_rating,
            self.professionalism_rating,
            self.helpfulness_rating,
            self.recommend_rating
        ] if r is not None]
        return sum(ratings) / len(ratings) if ratings else None


class LiveSession(models.Model):
    SESSION_TYPES = [
        ('video', 'Video Call'),
        ('audio', 'Audio Only'),
        ('chat', 'Text Chat'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('waiting', 'Waiting Room'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='live_session'
    )
    session_type = models.CharField(
        max_length=20, 
        choices=SESSION_TYPES, 
        default='video'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled'
    )
    
    # WebRTC/Session Management
    room_id = models.CharField(max_length=100, unique=True, blank=True)
    session_token = models.CharField(max_length=255, blank=True)
    meeting_url = models.URLField(blank=True)
    
    # Timing
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Session Data
    notes = models.TextField(blank=True)
    recording_url = models.URLField(blank=True)  # If recording is enabled
    session_data = models.JSONField(default=dict)  # Store session metadata
    
    # Security & Privacy
    is_recorded = models.BooleanField(default=False)
    consent_given = models.BooleanField(default=False)
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('supervised', 'Supervised'),
            ('training', 'Training'),
        ],
        default='private'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return (f"Live Session: {self.appointment.user.full_name} with "
                f"{self.appointment.counselor.name}")
    
    @property
    def duration_minutes(self):
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 60
        return None
    
    def generate_room_id(self):
        """Generate unique room ID for the session"""
        import uuid
        self.room_id = f"session_{uuid.uuid4().hex[:12]}"
        self.save()
        return self.room_id


class SessionParticipant(models.Model):
    """Track participants in live sessions"""
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('student', 'Student'),
            ('counselor', 'Counselor'),
            ('observer', 'Observer'),
        ]
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    connection_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        blank=True
    )
    
    class Meta:
        unique_together = ['session', 'user']


class SessionMessage(models.Model):
    """Store chat messages during live sessions"""
    session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('system', 'System'),
            ('file', 'File'),
        ],
        default='text'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class UserBehaviorLog(models.Model):
    """Track user behavior patterns for AI personalization"""
    BEHAVIOR_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('dass_test', 'DASS21 Test Completion'),
        ('exercise', 'Relaxation Exercise'),
        ('appointment_booked', 'Appointment Booked'),
        ('appointment_attended', 'Appointment Attended'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('feedback_submitted', 'Feedback Submitted'),
        ('profile_updated', 'Profile Updated'),
        ('notification_read', 'Notification Read'),
        ('page_view', 'Page View'),
        ('session_start', 'Live Session Start'),
        ('session_end', 'Live Session End'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    behavior_type = models.CharField(max_length=30, choices=BEHAVIOR_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, help_text="Additional context data")
    session_id = models.CharField(max_length=100, blank=True, help_text="Session identifier for grouping related actions")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'behavior_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.behavior_type} at {self.timestamp}"


class MentalHealthTipsCache(models.Model):
    """Cache AI-generated mental health tips to reduce API calls and handle rate limits"""

    # Cache key components
    depression_severity = models.CharField(max_length=20)
    anxiety_severity = models.CharField(max_length=20)
    stress_severity = models.CharField(max_length=20)
    risk_level = models.CharField(max_length=20)
    college = models.CharField(max_length=10, blank=True)
    year_level = models.CharField(max_length=2, blank=True)

    # Cached content
    tips_content = models.TextField()
    tips_title = models.CharField(max_length=100, default='💡 Mental Health Tips')
    source = models.CharField(max_length=20, default='openai')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['depression_severity', 'anxiety_severity', 'stress_severity',
                          'risk_level', 'college', 'year_level']
        indexes = [
            models.Index(fields=['depression_severity', 'anxiety_severity', 'stress_severity']),
            models.Index(fields=['risk_level', 'college', 'year_level']),
            models.Index(fields=['last_used', 'usage_count']),
        ]

    def __str__(self):
        return f"Tips cache: {self.depression_severity}/{self.anxiety_severity}/{self.stress_severity} - {self.risk_level}"

    def increment_usage(self):
        """Increment usage count when tip is retrieved"""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'last_used'])



class UserSettings(models.Model):
    """User settings for application preferences and accessibility"""

    # User reference
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')

    # Theme and appearance
    dark_mode = models.BooleanField(default=False, help_text="Enable dark mode theme")
    font_size = models.CharField(
        max_length=20,
        choices=[
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
            ('extra_large', 'Extra Large'),
        ],
        default='medium',
        help_text="Preferred font size"
    )

    # Notification preferences
    notification_preferences = models.JSONField(
        default=dict,
        help_text="Notification preferences with frequency settings"
    )

    # Language and localization
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
        ],
        default='en',
        help_text="Preferred application language"
    )

    # Accessibility options
    high_contrast = models.BooleanField(default=False, help_text="Enable high contrast mode")
    screen_reader = models.BooleanField(default=False, help_text="Optimize for screen readers")
    reduced_motion = models.BooleanField(default=False, help_text="Reduce animations and transitions")

    # Data privacy settings
    analytics_tracking = models.BooleanField(default=True, help_text="Allow analytics tracking")
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('counselors_only', 'Counselors Only'),
            ('private', 'Private'),
        ],
        default='counselors_only',
        help_text="Profile visibility to other users"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'
        db_table = 'user_settings'

    def __str__(self):
        return f"Settings for {self.user.username}"

    def get_notification_setting(self, notification_type, default=True):
        """Get notification preference for a specific type"""
        return self.notification_preferences.get(notification_type, default)

    def set_notification_setting(self, notification_type, enabled, frequency='daily'):
        """Set notification preference for a specific type"""
        if not self.notification_preferences:
            self.notification_preferences = {}
        self.notification_preferences[notification_type] = {
            'enabled': enabled,
            'frequency': frequency
        }
        self.save()

    @property
    def default_notification_preferences(self):
        """Get default notification preferences structure"""
        return {
            'assignment_reminders': {'enabled': True, 'frequency': 'daily'},
            'grade_updates': {'enabled': True, 'frequency': 'weekly'},
            'study_session_alerts': {'enabled': True, 'frequency': 'daily'},
            'appointment_reminders': {'enabled': True, 'frequency': 'daily'},
            'followup_notifications': {'enabled': True, 'frequency': 'weekly'},
        }


class MoodPrediction(models.Model):
    """Store AI-generated mood predictions and trend analysis"""
    PREDICTION_TYPES = [
        ('short_term', 'Short Term (1-7 days)'),
        ('medium_term', 'Medium Term (1-4 weeks)'),
        ('long_term', 'Long Term (1-3 months)'),
    ]

    CONFIDENCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prediction_date = models.DateTimeField(auto_now_add=True)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)

    # Predicted scores
    predicted_depression = models.FloatField(help_text="Predicted depression score (0-42)")
    predicted_anxiety = models.FloatField(help_text="Predicted anxiety score (0-42)")
    predicted_stress = models.FloatField(help_text="Predicted stress score (0-42)")

    # Trend analysis
    depression_trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('worsening', 'Worsening'),
        ('unknown', 'Unknown'),
    ], default='unknown')

    anxiety_trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('worsening', 'Worsening'),
        ('unknown', 'Unknown'),
    ], default='unknown')

    stress_trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('worsening', 'Worsening'),
        ('unknown', 'Unknown'),
    ], default='unknown')

    # Prediction reasoning and insights
    prediction_reasoning = models.TextField(help_text="AI reasoning for the prediction")
    behavioral_insights = models.JSONField(default=dict, help_text="Key behavioral patterns identified")
    risk_factors = models.JSONField(default=list, help_text="Identified risk factors")
    protective_factors = models.JSONField(default=list, help_text="Identified protective factors")

    # Recommendations
    recommended_actions = models.JSONField(default=list, help_text="Suggested actions based on prediction")
    follow_up_date = models.DateField(help_text="Suggested date for follow-up assessment")

    # Metadata
    based_on_data_points = models.IntegerField(default=0, help_text="Number of data points used for prediction")
    prediction_model = models.CharField(max_length=50, default='ai_feedback', help_text="Model/version used for prediction")

    class Meta:
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['user', 'prediction_date']),
            models.Index(fields=['user', 'prediction_type']),
        ]

    def __str__(self):
        return f"Mood Prediction for {self.user.username} - {self.prediction_type} ({self.prediction_date.date()})"


