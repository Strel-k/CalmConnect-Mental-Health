"""
Secure models for handling sensitive psychological data.
Provides encrypted storage and access control for DASS test results.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DASSResult
from .utils import (
    DataEncryption, DASSDataValidator, AuditLogger,
    ConsentManager, DataIntegrity
)


class SecureDASSResult(DASSResult):
    """
    Enhanced DASSResult model with field-level encryption and security features.
    """

    # Encrypted fields for sensitive data
    encrypted_answers = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted JSON containing all DASS-21 answers"
    )
    encrypted_depression_score = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted depression score"
    )
    encrypted_anxiety_score = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted anxiety score"
    )
    encrypted_stress_score = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted stress score"
    )

    # Security and audit fields
    data_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of original data for integrity verification"
    )
    consent_given = models.BooleanField(
        default=False,
        help_text="Whether user consented to data collection and storage"
    )
    consent_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When consent was given"
    )
    encryption_version = models.CharField(
        max_length=10,
        default='v1',
        help_text="Version of encryption used"
    )
    access_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this record has been accessed"
    )
    last_accessed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this record was accessed"
    )

    class Meta:
        verbose_name = 'Secure DASS Result'
        verbose_name_plural = 'Secure DASS Results'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track if this is a new instance for encryption logic
        self._is_new = self.pk is None

    def save(self, *args, **kwargs):
        """Override save to handle encryption and validation"""
        user = kwargs.pop('user', None)  # Get user from kwargs if provided

        # Validate consent before saving
        if not self.consent_given:
            if user:
                self.consent_given = ConsentManager.validate_consent(
                    user, 'dass_assessment'
                )
                if self.consent_given:
                    self.consent_timestamp = timezone.now()
            else:
                raise ValidationError(
                    "User consent required for DASS assessment data storage"
                )

        # Encrypt sensitive data before saving
        if self.answers and not self.encrypted_answers:
            # Validate answers first
            DASSDataValidator.validate_answers(self.answers)

            # Encrypt answers
            self.encrypted_answers = DataEncryption.encrypt_data(self.answers)

            # Generate integrity hash
            self.data_hash = DataIntegrity.generate_hash(self.answers)

        # Encrypt scores if they exist
        if self.depression_score is not None and not self.encrypted_depression_score:
            self.encrypted_depression_score = DataEncryption.encrypt_data(
                self.depression_score
            )

        if self.anxiety_score is not None and not self.encrypted_anxiety_score:
            self.encrypted_anxiety_score = DataEncryption.encrypt_data(
                self.anxiety_score
            )

        if self.stress_score is not None and not self.encrypted_stress_score:
            self.encrypted_stress_score = DataEncryption.encrypt_data(
                self.stress_score
            )

        # Validate scores
        if (self.depression_score is not None and
            self.anxiety_score is not None and
            self.stress_score is not None):
            DASSDataValidator.validate_scores(
                self.depression_score,
                self.anxiety_score,
                self.stress_score
            )

        super().save(*args, **kwargs)

    @property
    def decrypted_answers(self):
        """Get decrypted answers with access logging"""
        if not self.encrypted_answers:
            return self.answers  # Fallback to unencrypted if available

        try:
            decrypted = DataEncryption.decrypt_data(self.encrypted_answers)

            # Log access for audit trail
            self._log_access('answers_decrypt')

            # Verify data integrity
            if not DataIntegrity.verify_integrity(decrypted, self.data_hash):
                AuditLogger.log_security_event(
                    'data_integrity_violation',
                    self.user,
                    {'resource_id': self.id, 'field': 'answers'}
                )
                raise ValidationError("Data integrity check failed")

            return decrypted
        except Exception as e:
            AuditLogger.log_security_event(
                'decryption_failure',
                self.user,
                {'resource_id': self.id, 'error': str(e)}
            )
            raise ValidationError("Failed to decrypt answers")

    @property
    def decrypted_depression_score(self):
        """Get decrypted depression score"""
        if not self.encrypted_depression_score:
            return self.depression_score

        try:
            decrypted = DataEncryption.decrypt_data(
                self.encrypted_depression_score
            )
            self._log_access('depression_score_decrypt')
            return decrypted
        except Exception as e:
            AuditLogger.log_security_event(
                'decryption_failure',
                self.user,
                {'resource_id': self.id, 'field': 'depression_score', 'error': str(e)}
            )
            raise ValidationError("Failed to decrypt depression score")

    @property
    def decrypted_anxiety_score(self):
        """Get decrypted anxiety score"""
        if not self.encrypted_anxiety_score:
            return self.anxiety_score

        try:
            decrypted = DataEncryption.decrypt_data(
                self.encrypted_anxiety_score
            )
            self._log_access('anxiety_score_decrypt')
            return decrypted
        except Exception as e:
            AuditLogger.log_security_event(
                'decryption_failure',
                self.user,
                {'resource_id': self.id, 'field': 'anxiety_score', 'error': str(e)}
            )
            raise ValidationError("Failed to decrypt anxiety score")

    @property
    def decrypted_stress_score(self):
        """Get decrypted stress score"""
        if not self.encrypted_stress_score:
            return self.stress_score

        try:
            decrypted = DataEncryption.decrypt_data(
                self.encrypted_stress_score
            )
            self._log_access('stress_score_decrypt')
            return decrypted
        except Exception as e:
            AuditLogger.log_security_event(
                'decryption_failure',
                self.user,
                {'resource_id': self.id, 'field': 'stress_score', 'error': str(e)}
            )
            raise ValidationError("Failed to decrypt stress score")

    def _log_access(self, action):
        """Log access to encrypted data"""
        self.access_count += 1
        self.last_accessed = timezone.now()
        # Save without triggering validation/encryption again
        super().save(update_fields=['access_count', 'last_accessed'])

        AuditLogger.log_dass_access(
            self.user,
            action,
            self.id,
            {
                'access_count': self.access_count,
                'timestamp': self.last_accessed.isoformat()
            }
        )

    def get_secure_data(self, user):
        """
        Get all decrypted data with proper access control.
        Only the data owner or authorized personnel can access.
        """
        # Check if user has permission to access this data
        if user != self.user and not user.is_staff:
            AuditLogger.log_security_event(
                'unauthorized_access_attempt',
                user,
                {'resource_id': self.id, 'resource_owner': self.user.id}
            )
            raise ValidationError("Access denied: insufficient permissions")

        return {
            'id': self.id,
            'user_id': self.user.id,
            'date_taken': self.date_taken,
            'answers': self.decrypted_answers,
            'depression_score': self.decrypted_depression_score,
            'anxiety_score': self.decrypted_anxiety_score,
            'stress_score': self.decrypted_stress_score,
            'depression_severity': self.depression_severity,
            'anxiety_severity': self.anxiety_severity,
            'stress_severity': self.stress_severity,
            'consent_given': self.consent_given,
            'consent_timestamp': self.consent_timestamp,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
        }


class DASSDataRetentionPolicy(models.Model):
    """
    Manages data retention policies for DASS test results.
    """

    RETENTION_POLICIES = [
        ('standard', 'Standard Retention (7 years)'),
        ('extended', 'Extended Retention (indefinite)'),
        ('anonymized', 'Anonymized Only'),
        ('deleted', 'Marked for Deletion'),
    ]

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='dass_retention_policies'
    )
    policy_type = models.CharField(
        max_length=20,
        choices=RETENTION_POLICIES,
        default='standard'
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    retention_until = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(
        blank=True,
        help_text="Reason for retention policy choice"
    )
    approved_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_retention_policies',
        help_text="Staff member who approved this policy"
    )

    class Meta:
        verbose_name = 'DASS Data Retention Policy'
        verbose_name_plural = 'DASS Data Retention Policies'
        unique_together = ['user', 'policy_type']

    def __str__(self):
        return f"{self.user.username} - {self.get_policy_type_display()}"
