"""
Configuración de URLs optimizadas para el sistema de calificación FEI.
Incluye endpoints para todas las funcionalidades necesarias del sistema ecuestre.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'parameters', views.EvaluationParameterViewSet, basename='evaluation-parameter')
router.register(r'competition-parameters', views.CompetitionParameterViewSet, basename='competition-parameter')
router.register(r'scores', views.ScoreViewSet, basename='score')

urlpatterns = [
    # ViewSets
    path('', include(router.urls)),
    
    # Tarjeta de calificación
    path('scorecard/<int:competition_id>/<int:participant_id>/', 
         views.JudgeScoreCardView.as_view(), 
         name='judge-scorecard'),
    
    # Endpoints de calificación
    path('score/bulk-submit/',
         views.ScoreViewSet.as_view({'post': 'bulk_submit'}),
         name='score-bulk-submit'),
    
    # Rankings
    path('rankings/<int:competition_id>/', 
         views.RankingListView.as_view(), 
         name='competition-rankings'),
    
    path('rankings/<int:competition_id>/<int:participant_id>/', 
         views.RankingDetailView.as_view(), 
         name='participant-ranking'),
    
    # Recalcular rankings
    path('rankings/<int:competition_id>/recalculate/', 
         views.recalculate_rankings, 
         name='recalculate-rankings'),
    
    # Estadísticas de jueces
    path('statistics/judge/<int:judge_id>/',
         views.judge_statistics,
         name='judge-statistics'),
    
    path('statistics/judge/',
         views.judge_statistics,
         name='current-judge-statistics'),
    
    # Comparación de jueces
    path('compare-judges/<int:competition_id>/<int:participant_id>/',
         views.compare_judges,
         name='compare-judges'),
    
    # Parámetros de competencia
    path('competition/<int:competition_id>/parameters/', 
         views.competition_parameters, 
         name='competition-parameters'),
    
    # Sincronización con Firebase
    path('sync-status/<int:competition_id>/',
         views.sync_status,
         name='sync-status'),
    
    path('force-sync/<int:competition_id>/',
         views.force_sync,
         name='force-sync'),
    
    # Datos offline
    path('offline/sync/', 
         views.OfflineDataView.as_view(), 
         name='sync-offline-data'),
    
    path('offline/pending/', 
         views.OfflineDataSyncListView.as_view(), 
         name='offline-pending'),
]