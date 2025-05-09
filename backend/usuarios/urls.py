# backend/usuarios/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    JineteViewSet,
    JuezViewSet,
    EntrenadorViewSet,
    CaballoViewSet
)

# Crear el router para los ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'jinetes', JineteViewSet)
router.register(r'jueces', JuezViewSet)
router.register(r'entrenadores', EntrenadorViewSet)
router.register(r'caballos', CaballoViewSet)

urlpatterns = [
    # Incluir las URLs generadas por el router
    path('', include(router.urls)),
]