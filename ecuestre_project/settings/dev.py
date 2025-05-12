"""
Development settings for ecuestre_project project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Para ambiente de desarrollo, usar el backend de desarrollo de channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}

# Firebase settings for development (el archivo real se añadirá más tarde)
FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, 'credentials', 'firebase-credentials-dev.json')
FIREBASE_DATABASE_URL = 'https://tu-proyecto-firebase.firebaseio.com'