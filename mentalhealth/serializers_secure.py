"""
Secure serializers for DASS test data with proper access control and encryption handling.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DASSResult
from .models_secure import SecureDASSResult
from .utils import (
    DASSDataValidator, ConsentManager, AuditLogger,
    DataEncryption
)


class SecureDASSResultSerializer(serializers.ModelSerializer):
    """
    Secure serializer for DASS results with encryption and access control.
    """

    # Read-only decrypted fields
    answers = serializers.SerializerMethodField()
    depression_score = serializers.SerializerMethodField()
    anxiety_score = serializers.SerializerMethodField()
    stress_score = serializers.SerializerMethodField()

    # Security metadata
    consent_given = serializers.BooleanField(read_only=True)
    consent_timestamp = serializers.DateTimeField(read_only=True)
    access_count = serializers.IntegerField(read_only=True)
    last_accessed = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DASSResult
        fields = [
            'id', 'user', 'date_taken',
            'answers', 'depression_score', 'anxiety_score', 'stress_score',
            'depression_severity', 'anxiety_severity', 'stress_severity',
            'consent_given', 'consent_timestamp',
            'access_count', 'last_accessed'
        ]
        read_only_fields = [
            'id', 'date_taken', 'user',
            'consent_given', 'consent_timestamp',
            'access_count', 'last_accessed'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.secure_instance = None

        # Convert to secure instance if it's a DASSResult
        if self.instance and isinstance(self.instance, DASSResult):
            self.secure_instance = SecureDASSResult.objects.get(pk=self.instance.pk)

    def get_answers(self, obj):
        """Get decrypted answers with access control"""
        if not self._check_access_permission(obj):
            return None
        return self.secure_instance.decrypted_answers if self.secure_instance else obj.answers

    def get_depression_score(self, obj):
        """Get decrypted depression score"""
        if not self._check_access_permission(obj):
            return None
        return (self.secure_instance.decrypted_depression_score
                if self.secure_instance else obj.depression_score)

    def get_anxiety_score(self, obj):
        """Get decrypted anxiety score"""
        if not self._check_access_permission(obj):
            return None
        return (self.secure_instance.decrypted_anxiety_score
                if self.secure_instance else obj.anxiety_score)

    def get_stress_score(self, obj):
        """Get decrypted stress score"""
        if not self._check_access_permission(obj):
            return None
        return (self.secure_instance.decrypted_stress_score
                if self.secure_instance else obj.stress_score)

    def _check_access_permission(self, obj):
        """Check if current user has permission to access decrypted data"""
        if not self.request or not self.request.user:
            return False

        user = self.request.user

        # Users can access their own data
        if obj.user == user:
            return True

        # Staff/admin can access all data
        if user.is_staff or user.is_superuser:
            return True

        # Counselors can access data for their appointments
        if hasattr(user, 'counselor_profile'):
            counselor = user.counselor_profile
            if obj.user.appointments.filter(counselor=counselor).exists():
                return True

        return False

    def create(self, validated_data):
        """Create DASS result with security validations"""
        user = self.request.user if self.request else None

        if not user:
            raise ValidationError("Authentication required")

        # Check consent
        if not ConsentManager.validate_consent(user, 'dass_assessment'):
            raise ValidationError(
                "User consent required for DASS assessment"
            )

        # Validate input data
        answers = validated_data.get('answers')
        if answers:
            DASSDataValidator.validate_answers(answers)

        scores = {
            'depression': validated_data.get('depression_score'),
            'anxiety': validated_data.get('anxiety_score'),
            'stress': validated_data.get('stress_score')
        }

        # Validate scores if all are provided
        if all(score is not None for score in scores.values()):
            DASSDataValidator.validate_scores(**scores)

        # Create instance with user context for security
        instance = DASSResult.objects.create(**validated_data)

        # Log creation
        AuditLogger.log_dass_access(
            user,
            'dass_result_created',
            instance.id,
            {'scores_provided': bool(scores['depression'])}
        )

        return instance

    def update(self, instance, validated_data):
        """Update DASS result with security checks"""
        user = self.request.user if self.request else None

        if not user:
            raise ValidationError("Authentication required")

        # Only allow updates by data owner or staff
        if instance.user != user and not user.is_staff:
            AuditLogger.log_security_event(
                'unauthorized_update_attempt',
                user,
                {'resource_id': instance.id}
            )
            raise ValidationError("Access denied: cannot modify this record")

        # Validate updated data
        answers = validated_data.get('answers')
        if answers:
            DASSDataValidator.validate_answers(answers)

        # Log update
        AuditLogger.log_dass_access(
            user,
            'dass_result_updated',
            instance.id,
            {'fields_updated': list(validated_data.keys())}
        )

        return super().update(instance, validated_data)


class DASSConsentSerializer(serializers.Serializer):
    """
    Serializer for handling DASS test consent.
    """

    consent_given = serializers.BooleanField(required=True)
    consent_timestamp = serializers.DateTimeField(read_only=True)
    consent_type = serializers.CharField(
        default='dass_assessment',
        read_only=True
    )
    privacy_policy_version = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """Record user consent"""
        user = self.context['request'].user
        consent_given = validated_data['consent_given']

        ConsentManager.record_consent(user, 'dass_assessment', consent_given)

        # Log consent action
        AuditLogger.log_dass_access(
            user,
            'consent_updated',
            details={
                'consent_given': consent_given,
                'timestamp': timezone.now().isoformat()
            }
        )

        return {
            'consent_given': consent_given,
            'consent_timestamp': timezone.now(),
            'consent_type': 'dass_assessment',
            'privacy_policy_version': '1.0'
        }


class SecureDASSResultListSerializer(serializers.ModelSerializer):
    """
    List serializer that doesn't expose sensitive decrypted data.
    """

    # Only show metadata, no decrypted content
    has_encrypted_data = serializers.SerializerMethodField()
    consent_status = serializers.SerializerMethodField()

    class Meta:
        model = DASSResult
        fields = [
            'id', 'user', 'date_taken',
            'depression_severity', 'anxiety_severity', 'stress_severity',
            'has_encrypted_data', 'consent_status'
        ]

    def get_has_encrypted_data(self, obj):
        """Check if record has encrypted data"""
        secure_obj = SecureDASSResult.objects.get(pk=obj.pk)
        return bool(secure_obj.encrypted_answers)

    def get_consent_status(self, obj):
        """Get consent status"""
        secure_obj = SecureDASSResult.objects.get(pk=obj.pk)
        return {
            'given': secure_obj.consent_given,
            'timestamp': secure_obj.consent_timestamp
        }
