from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, DASSResult, UserSettings


class DASSResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DASSResult
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    cancelled_at = serializers.DateTimeField(required=False)
    cancellation_reason = serializers.CharField(required=False)
    user = serializers.SerializerMethodField()
    counselor_name = serializers.CharField(
        source='counselor.name', 
        read_only=True
    )
    college = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    dass_result = serializers.PrimaryKeyRelatedField(
        queryset=DASSResult.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'user',
            'counselor',
            'counselor_name',
            'date',
            'time',
            'session_type',
            'services',
            'reason',
            'phone',
            'course_section',
            'dass_result',
            'status',
            'created_at',
            'updated_at',
            'college',
            'program',
            'cancelled_at',
            'cancellation_reason'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': obj.user.full_name,
            'student_id': obj.user.student_id,
            'college': obj.user.get_college_display(),
            'program': obj.user.program
        }
    
    def get_college(self, obj):
        return obj.user.get_college_display()
    
    def get_program(self, obj):
        return obj.user.program
    
    def validate(self, data):
        if data.get('status') == 'cancelled':
            if not data.get('cancellation_reason'):
                data['cancellation_reason'] = 'Cancelled by administrator'
            if not data.get('cancelled_at'):
                data['cancelled_at'] = timezone.now()
        return data

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'cancelled':
            instance.status = 'cancelled'
            instance.cancellation_reason = validated_data.get(
                'cancellation_reason'
            )
            instance.cancelled_at = validated_data.get('cancelled_at')
            instance.save()
            return instance
        return super().update(instance, validated_data)


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'dark_mode',
            'font_size',
            'notification_preferences',
            'language',
            'high_contrast',
            'screen_reader',
            'reduced_motion',
            'analytics_tracking',
            'profile_visibility',
        ]

