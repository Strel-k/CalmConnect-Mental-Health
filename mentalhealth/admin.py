from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import DASSResult, RelaxationLog, CustomUser
from .models import Appointment, Counselor, FollowupRequest

# Register your models here.
admin.site.register(DASSResult)
admin.site.register(RelaxationLog)

# Only ONE registration method for CustomUser - choose either:

# OPTION 1: Using the decorator (recommended)
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'email_verified', 'is_active')
    list_filter = ('email_verified', 'is_active')
    search_fields = ('username', 'email', 'full_name', 'student_id')
    
    # Add these fieldsets to maintain password and permissions handling
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'student_id', 'age', 'gender')}),
        ('Academic Info', {'fields': ('college', 'program', 'year_level')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'full_name', 'student_id'),
        }),
    )
    
@admin.register(Counselor)
class CounselorAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'rank', 'is_active', 'linked_user')
    
    def linked_user(self, obj):
        return obj.user.username if obj.user else "Not linked"
    linked_user.short_description = 'User Account'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'counselor', 'date', 'time', 'status')
    raw_id_fields = ('user', 'counselor', 'dass_result')


@admin.register(FollowupRequest)
class FollowupRequestAdmin(admin.ModelAdmin):
    list_display = ('report', 'requested_by', 'requester_type', 'status', 'created_at')
    list_filter = ('status', 'requester_type', 'created_at')
    search_fields = ('report__title', 'requested_by__full_name', 'reason')
    raw_id_fields = ('report', 'requested_by', 'approved_denied_by', 'resulting_appointment')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Request Information', {
            'fields': ('report', 'requested_by', 'requester_type', 'reason')
        }),
        ('Scheduling Preferences', {
            'fields': ('requested_date', 'requested_time')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes', 'approved_denied_by', 'approved_denied_at')
        }),
        ('Final Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time', 'session_type', 'resulting_appointment')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

