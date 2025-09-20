"""
Enhanced security views for Jersey Artwork platform.
"""
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from artworks.security import WebhookSignatureValidator, require_artist
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    """
    Health check endpoint for monitoring.
    """

    def get(self, request):
        """Return health status."""
        try:
            # Check database connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            # Check cache connection
            from django.core.cache import cache
            cache.set('health_check', 'ok', 30)

            return JsonResponse({
                'status': 'healthy',
                'service': 'jersey-artwork',
                'database': 'connected',
                'cache': 'connected'
            })
        except Exception as e:
            logger.error(f'Health check failed: {str(e)}')
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=503)


class CSRFFailureView(View):
    """
    Custom CSRF failure view with better user experience.
    """

    def dispatch(self, request, *args, **kwargs):
        """Handle CSRF failure."""
        logger.warning(f'CSRF failure from IP: {request.META.get("REMOTE_ADDR")}')

        if request.is_ajax():
            return JsonResponse({
                'error': 'CSRF verification failed. Please refresh the page and try again.'
            }, status=403)

        return HttpResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Security Check Failed</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen flex items-center justify-center px-4">
                    <div class="max-w-md w-full text-center">
                        <h1 class="text-2xl font-bold text-gray-900 mb-4">Security Check Failed</h1>
                        <p class="text-gray-600 mb-6">
                            Your request could not be verified for security reasons.
                            This can happen if you've been inactive for a while.
                        </p>
                        <button onclick="window.location.reload()"
                                class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                            Refresh Page
                        </button>
                    </div>
                </div>
            </body>
            </html>
        """, status=403)


class SecurePaymentWebhookView(View):
    """
    Base class for secure payment webhook handling.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Verify webhook signature before processing."""
        # Log webhook attempt
        logger.info(f'Webhook received from IP: {request.META.get("REMOTE_ADDR")}')

        # Verify signature
        if not self.verify_signature(request):
            logger.warning('Invalid webhook signature')
            return JsonResponse({'error': 'Invalid signature'}, status=401)

        return super().dispatch(request, *args, **kwargs)

    def verify_signature(self, request):
        """Override in subclass to implement provider-specific verification."""
        raise NotImplementedError


class SumUpWebhookView(SecurePaymentWebhookView):
    """
    Secure SumUp webhook handler.
    """

    def verify_signature(self, request):
        """Verify SumUp webhook signature."""
        signature = request.headers.get('X-Sumup-Signature')
        if not signature:
            return False

        return WebhookSignatureValidator.verify_sumup_signature(
            request.body,
            signature,
            settings.SUMUP_WEBHOOK_SECRET
        )

    def post(self, request):
        """Process verified webhook."""
        try:
            data = json.loads(request.body)
            event_type = data.get('event_type')

            logger.info(f'Processing SumUp webhook: {event_type}')

            # Process based on event type
            if event_type == 'payment.success':
                self.handle_payment_success(data)
            elif event_type == 'payment.failed':
                self.handle_payment_failed(data)

            return JsonResponse({'status': 'processed'})

        except Exception as e:
            logger.error(f'Webhook processing error: {str(e)}')
            return JsonResponse({'error': 'Processing failed'}, status=500)

    def handle_payment_success(self, data):
        """Handle successful payment."""
        # Implementation here
        pass

    def handle_payment_failed(self, data):
        """Handle failed payment."""
        # Implementation here
        pass


class SecureArtistDashboardView(LoginRequiredMixin, View):
    """
    Secure artist dashboard with proper access control.
    """

    def dispatch(self, request, *args, **kwargs):
        """Verify user is an artist."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.user_type != 'artist':
            logger.warning(f'Non-artist user {request.user.id} attempted to access artist dashboard')
            raise PermissionDenied('This area is restricted to artists only.')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Display artist dashboard."""
        # Implementation here
        pass