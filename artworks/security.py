"""
Security utilities and middleware for the Jersey Artwork platform.
"""
import hashlib
import hmac
import time
import logging
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect
import bleach

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Configure rate limits per endpoint pattern
        self.rate_limits = {
            '/accounts/login/': (5, 300),  # 5 attempts per 5 minutes
            '/accounts/register/': (3, 600),  # 3 registrations per 10 minutes
            '/api/': (100, 60),  # 100 API calls per minute
            '/payments/': (10, 60),  # 10 payment attempts per minute
            '/artworks/upload/': (5, 300),  # 5 uploads per 5 minutes
        }

    def __call__(self, request):
        # Check rate limits
        if not self._check_rate_limit(request):
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')

        response = self.get_response(request)
        return response

    def _check_rate_limit(self, request):
        """Check if request exceeds rate limit."""
        if settings.DEBUG:
            return True  # Skip rate limiting in development

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)
        path = request.path

        # Find matching rate limit rule
        for pattern, (limit, window) in self.rate_limits.items():
            if path.startswith(pattern):
                cache_key = f'rate_limit:{pattern}:{client_id}'

                # Get current count
                current_count = cache.get(cache_key, 0)

                if current_count >= limit:
                    logger.warning(f'Rate limit exceeded for {client_id} on {pattern}')
                    return False

                # Increment counter
                cache.set(cache_key, current_count + 1, window)
                break

        return True

    def _get_client_id(self, request):
        """Get unique client identifier."""
        if request.user.is_authenticated:
            return f'user_{request.user.id}'

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')

        return f'ip_{ip}'


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        if not settings.DEBUG:
            response['Content-Security-Policy'] = '; '.join(csp_directives)

            # Strict Transport Security
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response


class WebhookSignatureValidator:
    """
    Validate webhook signatures from payment providers.
    """

    @staticmethod
    def verify_sumup_signature(request_body, signature, secret):
        """Verify SumUp webhook signature."""
        if not secret:
            logger.error('SumUp webhook secret not configured')
            return False

        expected_signature = hmac.new(
            secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def verify_citypay_signature(request_body, signature, secret):
        """Verify CityPay webhook signature."""
        if not secret:
            logger.error('CityPay webhook secret not configured')
            return False

        expected_signature = hmac.new(
            secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)


def require_artist(view_func):
    """
    Decorator to ensure user is an authenticated artist.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.user_type != 'artist':
            logger.warning(f'Non-artist user {request.user.id} attempted to access artist-only view')
            return HttpResponseForbidden('This page is only accessible to artists.')

        return view_func(request, *args, **kwargs)

    return wrapped_view


def require_customer(view_func):
    """
    Decorator to ensure user is an authenticated customer.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.user_type != 'customer':
            logger.warning(f'Non-customer user {request.user.id} attempted to access customer-only view')
            return HttpResponseForbidden('This page is only accessible to customers.')

        return view_func(request, *args, **kwargs)

    return wrapped_view


class InputSanitizer:
    """
    Sanitize user input to prevent XSS attacks.
    """

    # Allowed HTML tags for rich text fields
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 's',
        'ul', 'ol', 'li', 'blockquote', 'a', 'h3', 'h4'
    ]

    # Allowed attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
    }

    @classmethod
    def sanitize_html(cls, html_content):
        """
        Sanitize HTML content to prevent XSS.

        Args:
            html_content: Raw HTML string

        Returns:
            Sanitized HTML string
        """
        if not html_content:
            return html_content

        return bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )

    @classmethod
    def sanitize_text(cls, text):
        """
        Sanitize plain text input.

        Args:
            text: Raw text string

        Returns:
            Sanitized text string
        """
        if not text:
            return text

        # Remove any HTML tags
        text = bleach.clean(text, tags=[], strip=True)

        # Escape special characters
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        return text

    @classmethod
    def sanitize_filename(cls, filename):
        """
        Sanitize filename to prevent directory traversal.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        import os
        # Get just the filename without path
        filename = os.path.basename(filename)

        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00', '\n', '\r', '\t']
        for char in dangerous_chars:
            filename = filename.replace(char, '')

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename


class SessionSecurity:
    """
    Enhanced session security utilities.
    """

    @staticmethod
    def rotate_session_key(request):
        """Rotate session key for security."""
        if hasattr(request, 'session'):
            request.session.cycle_key()

    @staticmethod
    def check_session_validity(request):
        """Check if session is still valid."""
        if not hasattr(request, 'session'):
            return False

        # Check session age
        session_age = request.session.get('_session_init_time')
        if session_age:
            current_time = time.time()
            # Session expires after 2 hours of inactivity
            if current_time - session_age > 7200:
                request.session.flush()
                return False

        # Update last activity time
        request.session['_last_activity'] = time.time()
        return True

    @staticmethod
    def initialize_session(request):
        """Initialize secure session."""
        request.session['_session_init_time'] = time.time()
        request.session['_last_activity'] = time.time()
        request.session.set_expiry(7200)  # 2 hours


def verify_recaptcha(view_func):
    """
    Decorator to verify reCAPTCHA for forms.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.method == 'POST' and not settings.DEBUG:
            import requests

            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                return JsonResponse({'error': 'Please complete the reCAPTCHA'}, status=400)

            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response,
                'remoteip': request.META.get('REMOTE_ADDR')
            }

            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if not result.get('success'):
                logger.warning(f'reCAPTCHA verification failed for IP {request.META.get("REMOTE_ADDR")}')
                return JsonResponse({'error': 'reCAPTCHA verification failed'}, status=400)

        return view_func(request, *args, **kwargs)

    return wrapped_view