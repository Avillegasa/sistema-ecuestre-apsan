"""
Enrutamiento WebSocket para actualizaciones en tiempo real.
"""
from django.urls import re_path
from . import consumers

# URL patterns para WebSockets
websocket_urlpatterns = [
    # Para actualizaciones de calificaciones por participante
    re_path(
        r'ws/scores/(?P<competition_id>\d+)/(?P<participant_id>\d+)/$',
        consumers.ScoreConsumer.as_asgi()
    ),
    
    # Para actualizaciones de rankings por competencia
    re_path(
        r'ws/rankings/(?P<competition_id>\d+)/$',
        consumers.RankingConsumer.as_asgi()
    ),
]