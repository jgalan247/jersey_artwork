"""
Production settings for Jersey Artwork platform.
Optimized for Digital Ocean App Platform deployment.
"""
import os
import sys
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY CONFIGURATION
# ============================================

# CRITICAL: Must be set in environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable must be set for production')

# NEVER run with debug in production
DEBUG = False

# Allowed hosts must be explicitly configured
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError('ALLOWED_HOSTS must be configured for production')

# CSRF Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_FAILURE_VIEW = 'artworks.views.csrf_failure'

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 7200  # 2 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # Serve static files in production
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'django_ratelimit',
    'storages',  # For Digital Ocean Spaces

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
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'artworks.security.RateLimitMiddleware',  # Custom rate limiting
    'artworks.security.SecurityHeadersMiddleware',  # Custom security headers
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

# Digital Ocean Managed Database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to individual settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 10,
            }
        }
    }

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased for production
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

# STATIC FILES CONFIGURATION (Digital Ocean Spaces)
# ============================================

# Use Digital Ocean Spaces for static and media files
USE_SPACES = os.environ.get('USE_SPACES', 'True') == 'True'

if USE_SPACES:
    # Digital Ocean Spaces settings
    AWS_ACCESS_KEY_ID = os.environ.get('SPACES_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('SPACES_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('SPACES_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = f"https://{os.environ.get('SPACES_REGION')}.digitaloceanspaces.com"
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'static'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('SPACES_CDN_DOMAIN', f"{AWS_STORAGE_BUCKET_NAME}.{os.environ.get('SPACES_REGION')}.digitaloceanspaces.com")

    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

    # Media files
    DEFAULT_FILE_STORAGE = 'artworks.storage_backends.MediaStorage'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Local static files with WhiteNoise
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [BASE_DIR / 'static']
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise settings
WHITENOISE_AUTOREFRESH = False
WHITENOISE_COMPRESS_OFFLINE = True

# FILE UPLOAD SECURITY
# ============================================

# Maximum file upload size
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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/jersey_artwork/error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/jersey_artwork/security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'artworks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console', 'file', 'security'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    raise ValueError('Email configuration must be set for production')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Jersey Artwork <noreply@jerseyartwork.com>')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = '[Jersey Artwork] '

# Admin notifications
ADMINS = [
    (admin.split(':')[0], admin.split(':')[1])
    for admin in os.environ.get('ADMINS', '').split(',')
    if ':' in admin
]

MANAGERS = ADMINS

# CACHE CONFIGURATION
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'jersey_artwork',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# SUBSCRIPTION CONFIGURATION
# ============================================

SUBSCRIPTION_CONFIG = {
    'MONTHLY_PRICE': Decimal(os.environ.get('ARTIST_SUBSCRIPTION_PRICE', '15.00')),
    'CURRENCY': os.environ.get('SUBSCRIPTION_CURRENCY', 'GBP'),
    'TRIAL_DAYS': int(os.environ.get('SUBSCRIPTION_TRIAL_DAYS', '14')),
    'GRACE_PERIOD_DAYS': int(os.environ.get('SUBSCRIPTION_GRACE_PERIOD', '3')),
    'FEATURES': {
        'MAX_ARTWORKS': int(os.environ.get('MAX_ARTWORKS_PER_ARTIST', '100')),
        'FEATURED_LISTINGS': int(os.environ.get('FEATURED_LISTINGS', '3')),
        'COMMISSION_RATE': Decimal('0.00'),
    }
}

# PAYMENT CONFIGURATION
# ============================================

PAYMENT_PROVIDER = os.environ.get('PAYMENT_PROVIDER', 'sumup')

# SumUp Configuration
SUMUP_BASE_URL = os.environ.get('SUMUP_BASE_URL', 'https://api.sumup.com')
SUMUP_API_URL = os.environ.get('SUMUP_API_URL', 'https://api.sumup.com/v0.1')
SUMUP_CLIENT_ID = os.environ.get('SUMUP_CLIENT_ID')
SUMUP_CLIENT_SECRET = os.environ.get('SUMUP_CLIENT_SECRET')
SUMUP_MERCHANT_CODE = os.environ.get('SUMUP_MERCHANT_CODE')
SUMUP_ACCESS_TOKEN = os.environ.get('SUMUP_ACCESS_TOKEN')
SUMUP_WEBHOOK_SECRET = os.environ.get('SUMUP_WEBHOOK_SECRET')

# CityPay Configuration
CITYPAY_BASE_URL = os.environ.get('CITYPAY_BASE_URL', 'https://api.citypay.com')
CITYPAY_MERCHANT_ID = os.environ.get('CITYPAY_MERCHANT_ID')
CITYPAY_LICENCE = os.environ.get('CITYPAY_LICENCE')
CITYPAY_WEBHOOK_SECRET = os.environ.get('CITYPAY_WEBHOOK_SECRET')

# CORS Configuration
# ============================================

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
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

# RECAPTCHA Configuration
# ============================================

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Sentry Configuration (Error Tracking)
# ============================================

SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )