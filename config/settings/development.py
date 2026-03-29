"""Development settings."""
from .base import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use console backend in dev so emails appear in the terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow all in dev
CORS_ALLOW_ALL_ORIGINS = True

# Use in-memory cache in dev (no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INTERNAL_IPS = ['127.0.0.1']

# Django debug toolbar (optional – install separately if desired)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
