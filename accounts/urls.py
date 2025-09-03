from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/artist/', views.register_artist, name='register_artist'),
    
    # Email verification
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
]