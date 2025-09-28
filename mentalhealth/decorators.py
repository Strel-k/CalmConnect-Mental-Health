from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def verified_required(view_func):
    """
    Decorator that checks if the user is authenticated and email-verified.
    If not, redirects to the appropriate page (login or verification prompt).
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.email_verified:
            return redirect('verify_prompt')
        return view_func(request, *args, **kwargs)
    return wrapper


def counselor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.debug("Unauthenticated user attempting to access counselor page")
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')

        if not hasattr(request.user, 'counselor_profile'):
            logger.debug(f"User {request.user.username} has these attributes: "
                        f"{dir(request.user)}")
            logger.warning(f"User {request.user.username} without counselor profile "
                          f"attempting to access counselor page")
            messages.error(request, "You don't have permission to access this page.")
            return redirect('index')

        # Check if the counselor profile is active
        if not request.user.counselor_profile.is_active:
            logger.warning(f"Archived counselor {request.user.username} "
                          f"attempting to access counselor page")
            messages.error(request, "Your account has been archived. "
                                  "Please contact the administrator.")
            return redirect('index')

        logger.debug(f"Granting counselor access to {request.user.username}")
        return view_func(request, *args, **kwargs)
    return wrapper


def api_staff_required(view_func):
    """
    Decorator for API views that checks if the user is staff or superuser.
    Returns JSON response instead of redirect for unauthorized access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'Staff access required'
            }, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper
