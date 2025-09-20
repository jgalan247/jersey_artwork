"""
Demo settings for Digital Ocean deployment
Based on settings_local2.py but configured for demo presentation
"""
import os
from pathlib import Path
import dj_database_url
from decimal import Decimal

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY - Use environment variables on Digital Ocean
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-demo-key-change-this-in-production')

# DEMO MODE FLAG - This enables all our demo features
DEMO_MODE = True
DEBUG = False  # Keep False for professional appearance

ALLOWED_HOSTS = [
    'jerseyhomepage.je',
    'www.jerseyhomepage.je',
    '.ondigitalocean.app',  # Keep this for the app URL
    'localhost',
    '127.0.0.1',
]

# Add your actual domain when you get it
if os.environ.get('APP_DOMAIN'):
    ALLOWED_HOSTS.append(os.environ.get('APP_DOMAIN'))

# Update CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://jerseyhomepage.je',
    'https://www.jerseyhomepage.je',
    'https://*.ondigitalocean.app',
    'http://localhost:8000',
]

# Update CORS settings  
CORS_ALLOWED_ORIGINS = [
    'https://jerseyhomepage.je',
    'https://www.jerseyhomepage.je',
    'https://*.ondigitalocean.app',
    'http://127.0.0.1:8000',
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'corsheaders',
    'whitenoise.runserver_nostatic',  # For static files
    
    # Local apps
    'accounts',
    'artworks',
    'cart',
    'orders',
    'payments',
    'subscriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'artworks.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'artworks.wsgi.application'

# DATABASE - Digital Ocean provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',  # Fallback for local testing
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation (keep simple for demo)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6}  # Simplified for demo
    },
]

# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# Static files with WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if os.path.exists(BASE_DIR / 'static') else []

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_COMPRESS_OFFLINE = True
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Media files (use local storage for demo, can upgrade to Spaces later)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# If using Digital Ocean Spaces (optional)
if os.environ.get('USE_SPACES') == 'true':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.environ.get('SPACES_KEY')
    AWS_SECRET_ACCESS_KEY = os.environ.get('SPACES_SECRET')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('SPACES_BUCKET')
    AWS_S3_ENDPOINT_URL = f'https://{os.environ.get("SPACES_REGION")}.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = 'public-read'

# Email Configuration - DEMO MODE (no real emails)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Logs to console
# AUTO-VERIFY ALL USERS IN DEMO MODE
AUTO_VERIFY_EMAIL = True

# Security settings for production
# Detect if running locally (via runserver or LOCAL_TEST env var)
import sys
IS_RUNSERVER = 'runserver' in sys.argv
IS_LOCAL_TEST = os.environ.get('LOCAL_TEST', 'false').lower() == 'true' or IS_RUNSERVER

# Disable HTTPS for local development, enable for production
SECURE_SSL_REDIRECT = False if IS_LOCAL_TEST else True  # True for Digital Ocean
SESSION_COOKIE_SECURE = False if IS_LOCAL_TEST else True  # True for Digital Ocean  
CSRF_COOKIE_SECURE = False if IS_LOCAL_TEST else True  # True for Digital Ocean
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 7200  # 2 hours for demo

# SUBSCRIPTION CONFIGURATION
SUBSCRIPTION_CONFIG = {
    'MONTHLY_PRICE': Decimal('15.00'),
    'CURRENCY': 'GBP',
    'TRIAL_DAYS': 14,
    'GRACE_PERIOD_DAYS': 3,
    'FEATURES': {
        'MAX_ARTWORKS': 100,
        'FEATURED_LISTINGS': 3,
        'COMMISSION_RATE': Decimal('0.00'),
    }
}

# PAYMENT CONFIGURATION - DEMO/TEST MODE
PAYMENT_PROVIDER = 'sumup'
PAYMENT_TEST_MODE = True  # Always test mode for demo

# SumUp Demo Configuration
SUMUP_BASE_URL = 'https://api.sumup.com'
SUMUP_API_URL = 'https://api.sumup.com/v0.1'
SUMUP_CLIENT_ID = os.environ.get('SUMUP_CLIENT_ID', 'demo_client_id')
SUMUP_CLIENT_SECRET = os.environ.get('SUMUP_CLIENT_SECRET', 'demo_secret')
SUMUP_MERCHANT_CODE = os.environ.get('SUMUP_MERCHANT_CODE', 'DEMO_MERCHANT')
SUMUP_ACCESS_TOKEN = os.environ.get('SUMUP_ACCESS_TOKEN', 'demo_token')

# CityPay Demo Configuration
CITYPAY_BASE_URL = 'https://sandbox.citypay.com'  # Use sandbox
CITYPAY_MERCHANT_ID = os.environ.get('CITYPAY_MERCHANT_ID', 'demo_merchant')
CITYPAY_LICENCE = os.environ.get('CITYPAY_LICENCE', 'demo_licence')



CORS_ALLOW_CREDENTIALS = True

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Cache configuration (use database cache for demo)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'demo_cache_table',
    }
}

# Logging Configuration for Digital Ocean
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Demo Mode Settings
if DEMO_MODE:
    # Show demo banner in admin
    ADMIN_SITE_HEADER = "Jersey Artwork Platform - DEMO MODE"
    
    # Demo notice for templates
    DEMO_NOTICE = "This is a demonstration environment. No real transactions will be processed."
    
    # Auto-approve all artist registrations
    AUTO_APPROVE_ARTISTS = True
    
    # Skip payment verification
    SKIP_PAYMENT_VERIFICATION = True


# Add domain to email settings
DEFAULT_FROM_EMAIL = 'Jersey Artwork <noreply@jerseyhomepage.je>'

print("=== DEMO SETTINGS LOADED ===")
print(f"Demo Mode: {DEMO_MODE}")
print(f"Debug: {DEBUG}")
print(f"Database: {DATABASES['default'].get('ENGINE', 'Not configured')}")
print("============================")