from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'', views.CompetitionViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'riders', views.RiderViewSet)
router.register(r'horses', views.HorseViewSet)
router.register(r'participants', views.ParticipantViewSet)

urlpatterns = [
    # ViewSets
    path('', include(router.urls)),
    
    # Endpoints adicionales
    path('<int:competition_id>/participants/', views.competition_participants, name='competition_participants'),
]