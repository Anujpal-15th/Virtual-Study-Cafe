"""
Django settings for virtualcafe project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
import logging

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")
    # Fallback: load from system environment
    pass

# Note: For production, use environment variables
# For now, settings are configured directly below


# ========================================
# SECURITY SETTINGS
# ========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h5j#k7@x^2v&m*9p$q!r+s_t%u(w)z~a3b4c5d6e7f8g9h0i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allowed hosts for security
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')


# Application definition
INSTALLED_APPS = [
    # Django Channels must be before django.contrib.staticfiles
    'daphne',
    
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    
    # Our custom apps
    'accounts',  
    'rooms',
    'tracker',  
    'notifications', 
    'solo',  
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'virtualcafe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-level templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ASGI application for Django Channels
WSGI_APPLICATION = 'virtualcafe.wsgi.application'
ASGI_APPLICATION = 'virtualcafe.asgi.application'

# ========================================
# DJANGO CHANNELS CONFIGURATION
# ========================================

# Django Channels Layer Configuration
# This uses Redis as the messaging backend for WebSocket communication
# Get Redis URL from environment variable
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379')

# Development: Using InMemoryChannelLayer (no Redis needed)
# Production: Use RedisChannelLayer with proper Redis server
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# For production with Redis, uncomment below and comment above:
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [REDIS_URL],
#         },
#     },
# }


# ========================================
# DATABASE CONFIGURATION
# ========================================

# Database selection: PostgreSQL or SQLite
# Default: SQLite (for development, no setup needed)
# If USE_POSTGRES=True in .env, switch to PostgreSQL

USE_POSTGRES = os.getenv('USE_POSTGRES', 'False') == 'True'

if USE_POSTGRES:
    # PostgreSQL Configuration (Production/Advanced)
    # Requires: PostgreSQL server installed and database created
    # Example: CREATE DATABASE virtualcafe_db; CREATE USER virtualcafe_user WITH PASSWORD 'password';
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'virtualcafe_db'),          # Database name
            'USER': os.getenv('DB_USER', 'virtualcafe_user'),        # Database user
            'PASSWORD': os.getenv('DB_PASSWORD', 'VirtualCafe@123'), # Database password
            'HOST': os.getenv('DB_HOST', 'localhost'),               # Database host
            'PORT': os.getenv('DB_PORT', '5432'),                    # Database port
        }
    }
    logger.info("Using PostgreSQL database")
else:
    # SQLite Configuration (Development/Default)
    # SQLite is a file-based database, perfect for development
    # No server needed, database stored in db.sqlite3 file
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    logger.info("Using SQLite database")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files (User uploads like avatars)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'


# ========================================
# EMAIL SETTINGS (for password reset)
# ========================================

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'sout.anujpal@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ppirnmtyjqedsvxb')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@virtualcafe.com')
