# backend/rankings/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RankingViewSet,
    ResultadoRankingViewSet,
    CertificadoViewSet
)

# Crear el router para los ViewSets
router = DefaultRouter()
router.register(r'rankings', RankingViewSet)
router.register(r'resultados', ResultadoRankingViewSet)
router.register(r'certificados', CertificadoViewSet)

urlpatterns = [
    # Incluir las URLs generadas por el router
    path('', include(router.urls)),
]