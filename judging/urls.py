from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'parameters', views.EvaluationParameterViewSet)
router.register(r'competition-parameters', views.CompetitionParameterViewSet)
router.register(r'scores', views.ScoreViewSet)

urlpatterns = [
    # ViewSets
    path('', include(router.urls)),
    
    # Tarjeta de calificación
    path('scorecard/<int:competition_id>/<int:participant_id>/', 
         views.JudgeScoreCardView.as_view(), 
         name='judge_scorecard'),
    
    # Rankings
    path('rankings/<int:competition_id>/', 
         views.RankingListView.as_view(), 
         name='competition_rankings'),
    
    # Recalcular rankings
    path('rankings/<int:competition_id>/recalculate/', 
         views.recalculate_rankings, 
         name='recalculate_rankings'),
    
    # Parámetros de competencia
    path('competition/<int:competition_id>/parameters/', 
         views.competition_parameters, 
         name='competition_parameters'),
    
    # Datos offline
    path('offline/sync/', 
         views.OfflineDataView.as_view(), 
         name='sync_offline_data'),
]