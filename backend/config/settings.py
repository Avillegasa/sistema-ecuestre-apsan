
import os
from datetime import timedelta 
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x7pz7ujwqfu+g^7^61=q^&@u7%89bbbay-hq81^z#1f^46_owt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    
    # Aplicaciones propias
    'usuarios',
    'competencias',
    'evaluaciones',
    'rankings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_ecuestre',
        'USER': 'postgres',  # Usuario de la base de datos
        'PASSWORD': 'root',  # Contraseña de la base de datos
        'HOST': 'localhost',  # O dirección IP de tu base de datos
        'PORT': '5432',       # Puerto por defecto de PostgreSQL
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-es'  # Español

TIME_ZONE = 'America/La_Paz'  # Zona horaria de Bolivia

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# Configuración de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Configuración de JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend React
]

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Configuración de Swagger para documentación de API
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
}


# Modificaciones a añadir en backend/config/settings.py

# Configuración de caché mejorada
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ecuestre-cache',
        'TIMEOUT': 3600,  # 1 hora por defecto
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,  # Fracción de entradas a eliminar cuando se alcanza MAX_ENTRIES
        },
    }
}

# En producción, se recomienda usar Redis o Memcached:
"""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
"""

# Configuración REST framework con manejador de excepciones personalizado
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'config.exceptions.handle_exception',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# Configuración para mejorar el rendimiento de la base de datos
DATABASE_OPTIONS = {
    'ATOMIC_REQUESTS': True,  # Cada solicitud en su propia transacción
    'CONN_MAX_AGE': 60,  # Mantener conexiones abiertas durante 60 segundos
}

# Mejoras de logging para desarrollo y producción
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
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'ecuestre.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'competencias': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'evaluaciones': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'rankings': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Mejoras de seguridad para producción
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True  # Solo en producción (False en desarrollo)
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Estas configuraciones de seguridad deben estar comentadas en desarrollo
"""
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
"""

# Configuración de archivos estáticos para producción con WhiteNoise
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Middleware adicional para rendimiento y seguridad
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Agregar para servir archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Soporte para internacionalización
]

# Optimización de consultas con debug_toolbar en desarrollo
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# Configuración avanzada para PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_ecuestre',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,  # Mantener conexiones abiertas durante 60 segundos
        'OPTIONS': {
            'client_encoding': 'UTF8',
            'sslmode': 'disable',  # Cambiar a 'require' en producción
        },
        'TEST': {
            'NAME': 'test_sistema_ecuestre',
        },
    }
}

# Optimización de configuración de SimpleJWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    # Configuración de seguridad adicional
    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'usuarios.Usuario',
    'UPDATE_LAST_LOGIN': True,
}

# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend React en desarrollo
]

# En producción, usar el dominio real:
"""
CORS_ALLOWED_ORIGINS = [
    "https://www.sistema-ecuestre.com",
]
"""

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Asegurar que los directorios de los medios existan
import os
os.makedirs(os.path.join(MEDIA_ROOT, 'caballos'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'perfiles'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'certificados'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'comprobantes'), exist_ok=True)

# Configuración para validación de imágenes
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Validación de tipos de archivo
VALID_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
VALID_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx']

# Integración con signals para invalidar caché
from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete

def connect_signals():
    """Conectar las señales para invalidar caché automáticamente"""
    from competencias.models import Competencia, Categoria, Inscripcion
    from evaluaciones.models import Evaluacion
    from rankings.models import Ranking, ResultadoRanking
    from config.optimizations import invalidate_model_caches
    
    # Conectar señales para cada modelo relevante
    post_save.connect(invalidate_model_caches, sender=Competencia)
    post_delete.connect(invalidate_model_caches, sender=Competencia)
    
    post_save.connect(invalidate_model_caches, sender=Categoria)
    post_delete.connect(invalidate_model_caches, sender=Categoria)
    
    post_save.connect(invalidate_model_caches, sender=Inscripcion)
    post_delete.connect(invalidate_model_caches, sender=Inscripcion)
    
    post_save.connect(invalidate_model_caches, sender=Evaluacion)
    post_delete.connect(invalidate_model_caches, sender=Evaluacion)
    
    post_save.connect(invalidate_model_caches, sender=Ranking)
    post_delete.connect(invalidate_model_caches, sender=Ranking)
    
    post_save.connect(invalidate_model_caches, sender=ResultadoRanking)
    post_delete.connect(invalidate_model_caches, sender=ResultadoRanking)

# La función connect_signals() debe ser llamada en AppConfig.ready()