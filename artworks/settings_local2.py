"""
Local development settings for Jersey Artwork platform.
Optimized for local testing with MailHog and minimal dependencies.
"""
import os
from pathlib import Path
from decimal import Decimal

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY CONFIGURATION
# ============================================

# Simple secret key for local testing
SECRET_KEY = 'django-insecure-local-testing-key-change-in-production'

# Debug mode for local development
DEBUG = True

# Allow localhost connections
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CSRF Settings (relaxed for local testing)
CSRF_COOKIE_SECURE = False  # Allow HTTP for local testing
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'  # Less strict for local testing
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]

# Session Security (relaxed for local testing)
SESSION_COOKIE_SECURE = False  # Allow HTTP for local testing
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 7200  # 2 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep sessions for convenience
SESSION_SAVE_EVERY_REQUEST = True

# Security Headers (basic for local testing)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Less strict for local testing
SECURE_SSL_REDIRECT = False  # No HTTPS redirect for local testing

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps (minimal for local testing)
    'corsheaders',
    # Note: django_ratelimit removed for local testing
    # Note: storages removed for local testing

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Security middleware disabled for local testing
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

# DATABASE CONFIGURATION
# ============================================

# Simple SQLite database for local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local_test.sqlite3',
    }
}

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation (relaxed for local testing)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Reduced for local testing
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# STATIC FILES CONFIGURATION
# ============================================

# Simple static files for local testing
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Use basic static files storage (no manifest)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# FILE UPLOAD SECURITY
# ============================================

# File upload settings (same as production for testing)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf']

# Upload permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# LOGGING CONFIGURATION
# ============================================

# Simple console logging for local testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'artworks': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# EMAIL CONFIGURATION (MAILHOG)
# ============================================

# MailHog configuration for local email testing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

# Email settings
DEFAULT_FROM_EMAIL = 'Jersey Artwork <noreply@jerseyartwork.je>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = '[Jersey Artwork Local] '

# CACHE CONFIGURATION
# ============================================

# Simple in-memory cache for local testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-testing-cache',
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database sessions

# SUBSCRIPTION CONFIGURATION
# ============================================

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

# PAYMENT CONFIGURATION (Testing)
# ============================================

PAYMENT_PROVIDER = 'sumup'

# SumUp Configuration (testing/sandbox)
SUMUP_BASE_URL = 'https://api.sumup.com'
SUMUP_API_URL = 'https://api.sumup.com/v0.1'
SUMUP_CLIENT_ID = 'test-client-id'
SUMUP_CLIENT_SECRET = 'test-client-secret'
SUMUP_MERCHANT_CODE = 'test-merchant'
SUMUP_ACCESS_TOKEN = 'test-access-token'
SUMUP_WEBHOOK_SECRET = 'test-webhook-secret'

# CityPay Configuration (testing)
CITYPAY_BASE_URL = 'https://api.citypay.com'
CITYPAY_MERCHANT_ID = 'test-merchant'
CITYPAY_LICENCE = 'test-licence'
CITYPAY_WEBHOOK_SECRET = 'test-webhook-secret'

# CORS Configuration
# ============================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Demo Mode Settings
# ============================================
DEMO_MODE = True  # Enable demo data creation
AUTO_VERIFY_EMAIL = True  # Auto-verify demo users
AUTO_APPROVE_ARTISTS = True  # Auto-approve demo artists

# Development specific settings
# ============================================

# Show emails in console as backup (in addition to MailHog)
# Uncomment this line if MailHog is not working and you want to see emails in terminal:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow all internal IPs for debug toolbar (if you add it later)
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

print("=== USING LOCAL TESTING SETTINGS ===")
print("- MailHog email backend active")
print("- SQLite database: db_local_test.sqlite3")
print("- Debug mode: ON")
print("- HTTPS redirects: OFF")
print("=====================================")