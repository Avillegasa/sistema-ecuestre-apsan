"""
ASGI config for ecuestre_project project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')

# Obtener la aplicación ASGI de Django
django_asgi_app = get_asgi_application()

# Importar después de configurar DJANGO_SETTINGS_MODULE
from judging.routing import websocket_urlpatterns

# Configuración del protocolo para ASGI
# Configuración del protocolo para ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})