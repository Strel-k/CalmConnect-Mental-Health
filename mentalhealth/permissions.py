"""
Custom permissions for DASS test data access control.
Ensures only authorized users can access sensitive psychological data.
"""

from rest_framework import permissions
from .utils import AuditLogger


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access all data
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Users can access their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # For DASS results, check ownership
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id

        return False


class CanAccessDASSData(permissions.BasePermission):
    """
    Permission class for accessing DASS test data.
    Allows access to own data, staff, and assigned counselors.
    """

    def has_permission(self, request, view):
        """Check if user has general permission to access DASS endpoints"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permission for DASS data"""
        user = request.user

        # Staff and superusers have full access
        if user.is_staff or user.is_superuser:
            AuditLogger.log_dass_access(
                user,
                'staff_access_granted',
                getattr(obj, 'id', None) or getattr(obj, 'pk', None)
            )
            return True

        # Users can access their own DASS results
        if hasattr(obj, 'user') and obj.user == user:
            return True

        # Counselors can access DASS data for their clients
        if hasattr(user, 'counselor_profile'):
            counselor = user.counselor_profile
            # Check if counselor has appointments with this user
            if hasattr(obj, 'user') and obj.user.appointments.filter(
                counselor=counselor
            ).exists():
                AuditLogger.log_dass_access(
                    user,
                    'counselor_access_granted',
                    getattr(obj, 'id', None) or getattr(obj, 'pk', None),
                    {'client_id': obj.user.id}
                )
                return True

        # Log access denial
        AuditLogger.log_security_event(
            'dass_access_denied',
            user,
            {
                'resource_id': getattr(obj, 'id', None) or getattr(obj, 'pk', None),
                'resource_type': obj.__class__.__name__
            }
        )

        return False


class CanCreateDASSResult(permissions.BasePermission):
    """
    Permission to create DASS results.
    Only authenticated users can create their own results.
    """

    def has_permission(self, request, view):
        """Check if user can create DASS results"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Additional checks can be added here (e.g., rate limiting)
        return True

    def has_object_permission(self, request, view, obj):
        """DASS creation doesn't have object-level permissions"""
        return True


class CanModifyDASSResult(permissions.BasePermission):
    """
    Permission to modify DASS results.
    Only staff can modify existing results for security reasons.
    """

    def has_permission(self, request, view):
        """Check if user can modify DASS results"""
        return (request.user and
                request.user.is_authenticated and
                request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        """Only staff can modify DASS results"""
        if not (request.user.is_staff or request.user.is_superuser):
            AuditLogger.log_security_event(
                'unauthorized_modification_attempt',
                request.user,
                {'resource_id': obj.id}
            )
            return False

        return True


class HasDASSConsent(permissions.BasePermission):
    """
    Permission that checks if user has given consent for DASS testing.
    """

    def has_permission(self, request, view):
        """Check if user has consented to DASS testing"""
        from .utils import ConsentManager

        if not request.user or not request.user.is_authenticated:
            return False

        has_consent = ConsentManager.validate_consent(
            request.user,
            'dass_assessment'
        )

        if not has_consent:
            AuditLogger.log_security_event(
                'consent_required_access_attempt',
                request.user,
                {'endpoint': request.path}
            )

        return has_consent


class RateLimitedDASSAccess(permissions.BasePermission):
    """
    Rate limiting permission for DASS endpoints.
    """

    def has_permission(self, request, view):
        """Implement rate limiting for DASS access"""
        # This would integrate with django-ratelimit or similar
        # For now, just check authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Rate limiting at object level"""
        # Could implement per-object rate limiting here
        return self.has_permission(request, view)
