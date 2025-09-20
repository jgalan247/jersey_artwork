# Create this file: artworks/middleware/demo_middleware.py
"""
Middleware to handle demo mode features and simulate functionality
"""
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
import random
import uuid


class DemoModeMiddleware(MiddlewareMixin):
    """Middleware to handle demo mode features"""
    
    def process_request(self, request):
        """Add demo mode flag to all requests"""
        request.demo_mode = getattr(settings, 'DEMO_MODE', False)
        request.is_demo = request.demo_mode
        
        # Auto-verify emails in demo mode
        if request.demo_mode and request.user.is_authenticated:
            if hasattr(request.user, 'email_verified') and not request.user.email_verified:
                request.user.email_verified = True
                request.user.save()
        
        return None
    
    def process_response(self, request, response):
        """Add demo mode headers if needed"""
        if getattr(request, 'demo_mode', False):
            response['X-Demo-Mode'] = 'true'
        return response


class SimulatedPaymentMiddleware(MiddlewareMixin):
    """Simulate payment processing in demo mode"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Intercept payment views in demo mode"""
        if not getattr(settings, 'DEMO_MODE', False):
            return None
        
        # Intercept SumUp callback/webhook in demo mode
        if request.path.startswith('/payments/sumup/callback'):
            # Simulate successful payment after a few seconds
            if 'demo_payment' in request.session:
                checkout_id = request.session.pop('demo_payment')
                # Simulate success
                messages.success(
                    request, 
                    "✅ Payment simulation successful! (Demo Mode - No real payment processed)"
                )
                return redirect('payments:success')
        
        return None


class AutoSubscriptionMiddleware(MiddlewareMixin):
    """Auto-create subscriptions for artists in demo mode"""
    
    def process_request(self, request):
        """Ensure all artists have active subscriptions in demo"""
        if not getattr(settings, 'DEMO_MODE', False):
            return None
        
        if request.user.is_authenticated and request.user.user_type == 'artist':
            # Auto-create subscription if missing
            if not hasattr(request.user, 'subscription'):
                from subscriptions.models import Subscription
                from datetime import timedelta
                from django.utils import timezone
                
                Subscription.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'status': 'active',
                        'monthly_price': settings.SUBSCRIPTION_CONFIG['MONTHLY_PRICE'],
                        'trial_end': timezone.now() + timedelta(days=30),
                        'current_period_end': timezone.now() + timedelta(days=30),
                        'next_billing_date': timezone.now() + timedelta(days=30)
                    }
                )
        
        return None


# Additional Demo Helper Functions

def simulate_email_verification(user):
    """Instantly verify email in demo mode"""
    if settings.DEMO_MODE:
        user.email_verified = True
        user.save()
        return True
    return False


def simulate_payment_success(order):
    """Simulate successful payment for demo"""
    if settings.DEMO_MODE:
        from django.utils import timezone
        order.is_paid = True
        order.paid_at = timezone.now()
        order.status = 'processing'
        order.transaction_id = f'DEMO-{uuid.uuid4().hex[:8].upper()}'
        order.save()
        return True
    return False


def get_demo_payment_methods():
    """Return demo payment methods for display"""
    return [
        {
            'name': 'SumUp',
            'logo': 'sumup-logo.png',
            'test_cards': [
                {'number': '4111 1111 1111 1111', 'type': 'Visa', 'result': 'Success'},
                {'number': '5555 5555 5555 4444', 'type': 'Mastercard', 'result': 'Success'},
                {'number': '4000 0000 0000 0002', 'type': 'Visa', 'result': 'Decline'},
            ]
        },
        {
            'name': 'CityPay',
            'logo': 'citypay-logo.png',
            'note': 'Subscription payments (coming soon)'
        }
    ]


def create_demo_notification(request, message_type='info'):
    """Create consistent demo notifications"""
    demo_messages = {
        'payment_success': '✅ Payment simulated successfully! In production, this would process through SumUp.',
        'email_sent': '📧 Email notification simulated! Check console for email content.',
        'subscription_activated': '🎉 Subscription activated! (Demo Mode - No payment required)',
        'artwork_uploaded': '🎨 Artwork uploaded! Auto-approved for demo.',
        'order_placed': '📦 Order placed successfully! (Demo Mode)',
    }
    
    if message_type in demo_messages:
        messages.info(request, f"DEMO: {demo_messages[message_type]}")