# backend/evaluaciones/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EvaluacionViewSet,
    PuntuacionViewSet
)

# Crear el router para los ViewSets
router = DefaultRouter()
router.register(r'evaluaciones', EvaluacionViewSet)
router.register(r'puntuaciones', PuntuacionViewSet)

urlpatterns = [
    # Incluir las URLs generadas por el router
    path('', include(router.urls)),
]