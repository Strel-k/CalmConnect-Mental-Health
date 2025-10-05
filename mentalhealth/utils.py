"""
Security utilities for handling sensitive data in CalmConnect.
Provides encryption, decryption, and security validation functions.
"""

import os
import hashlib
import hmac
import json
import base64
import logging
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DataEncryption:
    """Handles encryption/decryption of sensitive psychological data"""

    @staticmethod
    def _get_fernet_key():
        """Generate or retrieve encryption key from settings"""
        key = getattr(settings, 'DASS_ENCRYPTION_KEY', None)
        if not key:
            # Generate a key for development (should be set in production)
            key = base64.urlsafe_b64encode(os.urandom(32))
            logger.warning(
                "Using auto-generated encryption key. "
                "Set DASS_ENCRYPTION_KEY in production!"
            )

        # Ensure key is properly formatted for Fernet
        if isinstance(key, str):
            key = key.encode()

        # Pad or truncate to 32 bytes if necessary
        if len(key) < 32:
            key = key + b'\x00' * (32 - len(key))
        elif len(key) > 32:
            key = key[:32]

        return base64.urlsafe_b64encode(key)

    @classmethod
    def encrypt_data(cls, data):
        """Encrypt sensitive data"""
        if data is None:
            return None

        try:
            fernet = Fernet(cls._get_fernet_key())

            # Convert data to JSON string if it's a dict/list
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, sort_keys=True)
            else:
                data_str = str(data)

            encrypted = fernet.encrypt(data_str.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValidationError("Failed to encrypt sensitive data")

    @classmethod
    def decrypt_data(cls, encrypted_data):
        """Decrypt sensitive data"""
        if not encrypted_data:
            return None

        try:
            fernet = Fernet(cls._get_fernet_key())
            decrypted = fernet.decrypt(encrypted_data.encode())
            data_str = decrypted.decode()

            # Try to parse as JSON, fallback to string
            try:
                return json.loads(data_str)
            except json.JSONDecodeError:
                return data_str
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValidationError("Failed to decrypt sensitive data")


class DataIntegrity:
    """Ensures data integrity and prevents tampering"""

    @staticmethod
    def generate_hash(data):
        """Generate SHA-256 hash of data for integrity checking"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode()).hexdigest()

    @staticmethod
    def verify_integrity(data, expected_hash):
        """Verify data integrity against expected hash"""
        return hmac.compare_digest(
            DataIntegrity.generate_hash(data),
            expected_hash
        )


class DASSDataValidator:
    """Validates DASS-21 test data integrity and security"""

    DASS_QUESTIONS_COUNT = 21
    SCORE_RANGES = {
        'depression': (0, 21),
        'anxiety': (0, 21),
        'stress': (0, 21)
    }

    @staticmethod
    def validate_answers(answers):
        """Validate DASS-21 answers structure and content"""
        if not isinstance(answers, dict):
            raise ValidationError("Answers must be a dictionary")

        if len(answers) != DASSDataValidator.DASS_QUESTIONS_COUNT:
            raise ValidationError(
                f"Must have exactly {DASSDataValidator.DASS_QUESTIONS_COUNT} "
                "answers"
            )

        for question_num in range(1, DASSDataValidator.DASS_QUESTIONS_COUNT + 1):
            if str(question_num) not in answers:
                raise ValidationError(
                    f"Missing answer for question {question_num}"
                )

            answer = answers[str(question_num)]
            if not isinstance(answer, int) or answer not in [0, 1, 2, 3]:
                raise ValidationError(
                    f"Invalid answer for question {question_num}: "
                    "must be 0-3"
                )

        return True

    @staticmethod
    def validate_scores(depression_score, anxiety_score, stress_score):
        """Validate calculated scores are within expected ranges"""
        scores = {
            'depression': depression_score,
            'anxiety': anxiety_score,
            'stress': stress_score
        }

        for score_type, score in scores.items():
            min_val, max_val = DASSDataValidator.SCORE_RANGES[score_type]
            if not isinstance(score, (int, float)) or not (min_val <= score <= max_val):
                raise ValidationError(
                    f"Invalid {score_type} score: must be between "
                    f"{min_val} and {max_val}"
                )

        return True


class ConsentManager:
    """Manages user consent for psychological assessments"""

    @staticmethod
    def validate_consent(user, consent_type='dass_assessment'):
        """Validate that user has given consent for the specified assessment"""
        # Check for consent record in user's profile or separate consent model
        # This would need to be implemented based on your consent tracking system
        return getattr(user, f'{consent_type}_consent', False)

    @staticmethod
    def record_consent(user, consent_type='dass_assessment', consent_given=True):
        """Record user's consent for psychological assessments"""
        # Update user's consent status
        setattr(user, f'{consent_type}_consent', consent_given)
        user.save()


class AuditLogger:
    """Logs access to sensitive psychological data"""

    @staticmethod
    def log_dass_access(user, action, resource_id=None, details=None):
        """Log access to DASS data"""
        logger.info(
            f"DASS_ACCESS: User {user.username} performed {action} on "
            f"resource {resource_id or 'N/A'}",
            extra={
                'user_id': user.id,
                'action': action,
                'resource_id': resource_id,
                'details': details or {},
                'timestamp': None  # Will be added by logging formatter
            }
        )

    @staticmethod
    def log_security_event(event_type, user=None, details=None):
        """Log security-related events"""
        logger.warning(
            f"SECURITY_EVENT: {event_type}",
            extra={
                'user_id': user.id if user else None,
                'event_type': event_type,
                'details': details or {},
            }
        )
