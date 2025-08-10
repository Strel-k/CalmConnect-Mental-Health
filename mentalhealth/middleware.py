"""
Security middleware for CalmConnect
"""
import time
import logging
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.urls import resolve
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """Enhanced security middleware"""
    
    def process_request(self, request):
        """Process incoming requests for security checks"""
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        request.client_ip = ip
        
        # Check for suspicious activity
        self._check_suspicious_activity(request)
        
        return None
    
    def _check_suspicious_activity(self, request):
        """Check for suspicious activity patterns"""
        ip = request.client_ip
        
        # Track request rate per IP
        cache_key = f"requests_per_ip:{ip}"
        requests = cache.get(cache_key, 0)
        
        # Allow up to 100 requests per minute per IP
        if requests > 100:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            # Consider blocking aggressive IPs
            return HttpResponseTooManyRequests("Rate limit exceeded")
        
        cache.set(cache_key, requests + 1, 60)  # 1 minute window


class LoginSecurityMiddleware(MiddlewareMixin):
    """Middleware to handle login security"""
    
    def process_request(self, request):
        """Process login security"""
        
        # Check for failed login attempts
        if request.path == '/login/' and request.method == 'POST':
            self._check_failed_login_attempts(request)
        
        # Auto-logout inactive sessions
        if request.user.is_authenticated:
            self._check_session_timeout(request)
        
        return None
    
    def _check_failed_login_attempts(self, request):
        """Check and limit failed login attempts"""
        ip = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR'))
        username = request.POST.get('username', '')
        
        # Track attempts by IP and username
        ip_key = f"failed_login_ip:{ip}"
        user_key = f"failed_login_user:{username}"
        
        ip_attempts = cache.get(ip_key, 0)
        user_attempts = cache.get(user_key, 0)
        
        # Block if too many attempts
        if ip_attempts >= 10:  # 10 attempts per IP per hour
            logger.warning(f"Login blocked for IP {ip} - too many attempts")
            cache.set(ip_key, ip_attempts + 1, 3600)  # Extend block
            return HttpResponseTooManyRequests("Too many login attempts from this IP")
        
        if user_attempts >= 5:  # 5 attempts per username per hour
            logger.warning(f"Login blocked for user {username} - too many attempts")
            cache.set(user_key, user_attempts + 1, 3600)  # Extend block
            return HttpResponseTooManyRequests("Too many login attempts for this user")
    
    def _check_session_timeout(self, request):
        """Check for session timeout and suspicious activity"""
        if not request.session.get('last_activity'):
            request.session['last_activity'] = time.time()
            return
        
        last_activity = request.session['last_activity']
        current_time = time.time()
        
        # Check if session has been inactive for too long
        max_inactive = getattr(settings, 'SESSION_COOKIE_AGE', 3600)
        if current_time - last_activity > max_inactive:
            logger.info(f"Session timeout for user {request.user.username}")
            logout(request)
            return redirect('login')
        
        # Update last activity
        request.session['last_activity'] = current_time
        
        # Check for session hijacking indicators
        self._check_session_hijacking(request)
    
    def _check_session_hijacking(self, request):
        """Check for potential session hijacking"""
        current_ip = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR'))
        current_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        stored_ip = request.session.get('login_ip')
        stored_user_agent = request.session.get('login_user_agent')
        
        if not stored_ip:
            # First request - store fingerprint
            request.session['login_ip'] = current_ip
            request.session['login_user_agent'] = current_user_agent
            return
        
        # Check for changes that might indicate hijacking
        if stored_ip != current_ip and not self._is_same_network(stored_ip, current_ip):
            logger.warning(f"IP change detected for user {request.user.username}: {stored_ip} -> {current_ip}")
            # In a real environment, you might want to force re-authentication
            
        if stored_user_agent != current_user_agent:
            logger.warning(f"User agent change for user {request.user.username}")
    
    def _is_same_network(self, ip1, ip2):
        """Check if two IPs are from the same network (simplified)"""
        try:
            # Simple check for same /24 subnet
            return '.'.join(ip1.split('.')[:-1]) == '.'.join(ip2.split('.')[:-1])
        except:
            return False


class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware for security audit logging"""
    
    def process_request(self, request):
        """Log security-relevant requests"""
        
        # Log sensitive endpoint access
        sensitive_paths = [
            '/admin/',
            '/api/ai-feedback/',
            '/counselor-dashboard/',
            '/admin-dashboard/'
        ]
        
        if any(request.path.startswith(path) for path in sensitive_paths):
            self._log_access(request)
    
    def _log_access(self, request):
        """Log access to sensitive endpoints"""
        logger.info(f"Access to {request.path} - User: {request.user.username if request.user.is_authenticated else 'Anonymous'} - IP: {getattr(request, 'client_ip', 'Unknown')}")


class ContentSecurityMiddleware(MiddlewareMixin):
    """Middleware for Content Security Policy"""
    
    def process_response(self, request, response):
        """Add security headers to response"""
        
        if not settings.DEBUG:
            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' wss: ws:; "
                "media-src 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response['Content-Security-Policy'] = csp
            
            # Additional security headers
            response['Permissions-Policy'] = (
                "geolocation=(), microphone=(self), camera=(self), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "speaker=(self)"
            )
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
