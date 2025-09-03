from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views import View
from django.http import HttpResponse
from .forms import CustomerRegistrationForm, ArtistRegistrationForm, ResendVerificationForm
from .models import User
from .tokens import email_verification_token

from .forms import (
    CustomUserCreationForm, LoginForm, CustomerProfileForm, 
    ArtistProfileForm, UserUpdateForm
)
from .models import User, CustomerProfile, ArtistProfile

def register_view(request):
    """User registration view following Django conventions."""
    if request.user.is_authenticated:
        return redirect('artworks:list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                login(request, user)
                messages.success(request, f'Welcome to Jersey Artwork, {user.first_name}!')
                
                # Redirect based on user type
                if user.user_type == 'artist':
                    messages.info(request, 'Please complete your artist profile.')
                    return redirect('accounts:profile')
                else:
                    return redirect('artworks:list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('artworks:gallery')  # or wherever you want logged-in users to go
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using email (username field)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not user.email_verified:
                messages.warning(
                    request,
                    'Please verify your email before logging in. '
                    f'<a href="{reverse("accounts:resend_verification")}">Resend verification email</a>',
                    extra_tags='safe'  # Allows HTML in message
                )
                return render(request, 'accounts/login.html')
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next or default
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirect based on user type
            if user.user_type == 'artist':
                return redirect('artworks:my_artworks')
            return redirect('artworks:gallery')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Logout view following Django conventions."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('artworks:list')

@login_required
def profile_view(request):
    """User profile view following Django conventions."""
    user_form = UserUpdateForm(instance=request.user)
    profile_form = None
    
    # Get or create profile based on user type
    if request.user.user_type == 'customer':
        profile, created = CustomerProfile.objects.get_or_create(user=request.user)
        profile_form = CustomerProfileForm(instance=profile)
    elif request.user.user_type == 'artist':
        profile, created = ArtistProfile.objects.get_or_create(
            user=request.user,
            defaults={'display_name': request.user.get_full_name()}
        )
        profile_form = ArtistProfileForm(instance=profile)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if request.user.user_type == 'customer':
            profile_form = CustomerProfileForm(request.POST, instance=profile)
        elif request.user.user_type == 'artist':
            profile_form = ArtistProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('accounts:profile')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    
    template_name = f'accounts/{request.user.user_type}_profile.html'
    return render(request, template_name, context)

class ArtistProfileDetailView(DetailView):
    """Public artist profile view following Django conventions."""
    model = ArtistProfile
    template_name = 'accounts/artist_detail.html'
    context_object_name = 'artist'
    
    def get_queryset(self):
        return ArtistProfile.objects.filter(is_approved=True).select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add artist's artworks
        context['artworks'] = self.object.artworks.filter(status='active')[:12]
        return context

# accounts/views.py



def send_verification_email(request, user):
    """Helper function to send verification email"""
    current_site = get_current_site(request)
    subject = 'Verify your email - Jersey Artwork'
    
    # Generate token and uid
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create verification link
    verification_link = f"http://{current_site.domain}{reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})}"
    
    # Render email content
    message = render_to_string('accounts/email/verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'verification_link': verification_link,
    })
    
    # Send email
    send_mail(
        subject,
        message,
        'noreply@jerseyartwork.je',
        [user.email],
        html_message=message,
        fail_silently=False,
    )


def register_customer(request):
    """Customer registration view"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send verification email
            send_verification_email(request, user)
            
            messages.success(
                request, 
                'Registration successful! Please check your email to verify your account.'
            )
            return redirect('accounts:login')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register_customer.html', {'form': form})


def register_artist(request):
    """Artist registration view"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = ArtistRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send verification email
            send_verification_email(request, user)
            
            messages.success(
                request, 
                'Registration successful! Please check your email to verify your account. '
                'After verification, you can choose a subscription plan to start selling.'
            )
            return redirect('accounts:login')
    else:
        form = ArtistRegistrationForm()
    
    return render(request, 'accounts/register_artist.html', {'form': form})


def verify_email(request, uidb64, token):
    """Verify email address using token from email link"""
    try:
        # Decode the user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and email_verification_token.check_token(user, token):
        # Token is valid, verify the email
        user.email_verified = True
        user.save()
        
        messages.success(
            request, 
            'Your email has been verified successfully! You can now log in.'
        )
        
        # Log the user in automatically
        login(request, user)
        
        # Redirect based on user type
        if user.user_type == 'artist':
            # Check if artist has subscription
            if not hasattr(user, 'subscription') or not user.subscription.is_active:
                return redirect('subscriptions:plans')
            return redirect('accounts:artist_dashboard')
        else:
            return redirect('/')
    else:
        messages.error(
            request, 
            'Invalid verification link. The link may have expired or been used already.'
        )
        return redirect('accounts:resend_verification')


def resend_verification(request):
    """Resend verification email"""
    if request.method == 'POST':
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Send new verification email
            send_verification_email(request, user)
            
            messages.success(
                request,
                f'Verification email sent to {email}. Please check your inbox.'
            )
            return redirect('accounts:login')
    else:
        form = ResendVerificationForm()
    
    return render(request, 'accounts/resend_verification.html', {'form': form})





@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounts/profile.html')


@login_required
def artist_dashboard(request):
    """Artist dashboard view"""
    if request.user.user_type != 'artist':
        messages.error(request, 'Access denied. Artists only.')
        return redirect('/')
    
    # Check email verification
    if not request.user.email_verified:
        messages.warning(
            request,
            'Please verify your email to access all features.'
        )
    
    # Check subscription status
    has_subscription = hasattr(request.user, 'subscription') and request.user.subscription.is_active
    
    context = {
        'has_subscription': has_subscription,
        'email_verified': request.user.email_verified,
    }
    
    return render(request, 'accounts/artist_dashboard.html', context)