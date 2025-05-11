"""
Production settings for ecuestre_project project.
"""

import os
from .base import *

DEBUG = False

# Obtener secreto desde variables de entorno
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Permitir solo los dominios donde estará alojada la aplicación
ALLOWED_HOSTS = ['sistema-ecuestre.apsan.org', 'www.sistema-ecuestre.apsan.org']

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://sistema-ecuestre.apsan.org",
    "https://www.sistema-ecuestre.apsan.org",
]

# Database
# Configurar base de datos PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ecuestre_db'),
        'USER': os.environ.get('DB_USER', 'ecuestre_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Channel layers con Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get('REDIS_HOST', 'localhost'), 
                       int(os.environ.get('REDIS_PORT', 6379)))],
        },
    },
}

# Firebase settings for production
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS_PATH')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True