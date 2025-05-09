# backend/competencias/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompetenciaViewSet,
    CategoriaViewSet,
    CriterioEvaluacionViewSet,
    InscripcionViewSet,
    AsignacionJuezViewSet
)

# Crear el router para los ViewSets
router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'criterios', CriterioEvaluacionViewSet)
router.register(r'inscripciones', InscripcionViewSet)
router.register(r'asignaciones', AsignacionJuezViewSet)

urlpatterns = [
    # Incluir las URLs generadas por el router
    path('', include(router.urls)),
]