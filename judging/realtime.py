"""
Módulo de integración entre WebSockets y Firebase para el sistema ecuestre.
Proporciona funciones para la sincronización bidireccional y manejo de eventos.
"""
import logging
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

from .models import Score, Ranking, FirebaseSync

logger = logging.getLogger(__name__)

def sync_score_to_all_clients(score):
    """
    Sincroniza una calificación a todos los sistemas conectados.
    Actualiza Firebase y notifica a los clientes WebSocket.
    
    Args:
        score: Objeto Score a sincronizar
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    try:
        # Sincronizar con Firebase
        from .firebase import sync_scores
        firebase_success = sync_scores(score.id)
        
        # Notificar a clientes WebSocket
        channel_layer = get_channel_layer()
        score_data = {
            'id': score.id,
            'judge_id': score.judge_id,
            'parameter_id': score.parameter.parameter_id,
            'value': float(score.value),
            'calculated_result': float(score.calculated_result),
            'is_edited': score.is_edited,
            'updated_at': score.updated_at.isoformat() if score.updated_at else None
        }
        
        # Nombre del grupo WebSocket para este participante
        room_group_name = f'scores_{score.competition_id}_{score.participant_id}'
        
        # Enviar mensaje al grupo
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'score_message',
                'score': score_data
            }
        )
        
        logger.info(f"Calificación {score.id} sincronizada a todos los clientes")
        return True
    except Exception as e:
        logger.error(f"Error al sincronizar calificación a todos los clientes: {e}")
        return False


def sync_rankings_to_all_clients(competition_id):
    """
    Sincroniza los rankings de una competencia a todos los sistemas conectados.
    Actualiza Firebase y notifica a los clientes WebSocket.
    
    Args:
        competition_id: ID de la competencia
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    try:
        # Sincronizar con Firebase
        from .firebase import sync_rankings
        firebase_success = sync_rankings(competition_id)
        
        # Notificar a clientes WebSocket
        channel_layer = get_channel_layer()
        
        # Obtener rankings actuales
        rankings = Ranking.objects.filter(
            competition_id=competition_id
        ).select_related(
            'participant', 'participant__rider', 'participant__horse'
        ).order_by('position')
        
        # Formatear para enviar por WebSocket
        rankings_data = []
        for ranking in rankings:
            participant = ranking.participant
            rider = participant.rider
            horse = participant.horse
            
            rankings_data.append({
                'id': ranking.id,
                'participant_id': participant.id,
                'position': ranking.position,
                'average': float(ranking.average_score),
                'percentage': float(ranking.percentage),
                'rider': {
                    'id': rider.id,
                    'first_name': rider.first_name,
                    'last_name': rider.last_name,
                    'nationality': rider.nationality or ''
                },
                'horse': {
                    'id': horse.id,
                    'name': horse.name,
                    'breed': horse.breed or ''
                },
                'number': participant.number,
                'order': participant.order,
                'withdrawn': participant.is_withdrawn
            })
        
        # Nombre del grupo WebSocket para esta competencia
        room_group_name = f'rankings_{competition_id}'
        
        # Enviar mensaje al grupo
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'rankings_update',
                'rankings': rankings_data
            }
        )
        
        logger.info(f"Rankings de competencia {competition_id} sincronizados a todos los clientes")
        return True
    except Exception as e:
        logger.error(f"Error al sincronizar rankings a todos los clientes: {e}")
        return False


def handle_firebase_score_update(data):
    """
    Maneja una actualización de calificación desde Firebase.
    Actualiza la base de datos y notifica a los clientes WebSocket.
    
    Args:
        data: Datos de la calificación
    
    Returns:
        bool: True si el manejo fue exitoso
    """
    try:
        with transaction.atomic():
            # Actualizar la base de datos
            from .firebase import update_score_from_firebase
            db_success = update_score_from_firebase(data)
            
            if not db_success:
                logger.warning("No se pudo actualizar la calificación en la base de datos")
                return False
            
            # Obtener la calificación actualizada
            from .models import Score
            score = Score.objects.get(
                competition_id=data.get('competitionId'),
                participant_id=data.get('participantId'),
                judge_id=data.get('judgeId'),
                parameter__parameter_id=data.get('parameterId')
            )
            
            # Notificar a clientes WebSocket
            sync_score_to_all_clients(score)
            
            return True
    except Exception as e:
        logger.error(f"Error al manejar actualización de calificación desde Firebase: {e}")
        return False


def handle_firebase_ranking_update(competition_id, data):
    """
    Maneja una actualización de rankings desde Firebase.
    Actualiza la base de datos y notifica a los clientes WebSocket.
    
    Args:
        competition_id: ID de la competencia
        data: Datos de los rankings
    
    Returns:
        bool: True si el manejo fue exitoso
    """
    try:
        # Actualizar los rankings en la base de datos
        from .services import update_participant_rankings
        rankings_data = update_participant_rankings(competition_id, recalculate_all=True)
        
        # Notificar a clientes WebSocket
        sync_rankings_to_all_clients(competition_id)
        
        return True
    except Exception as e:
        logger.error(f"Error al manejar actualización de rankings desde Firebase: {e}")
        return False


def initialize_firebase_listeners():
    """
    Inicializa los listeners de Firebase para actualizaciones en tiempo real.
    """
    try:
        from .firebase import listen_for_score_changes
        
        # Obtener competencias activas
        from competitions.models import Competition
        active_competitions = Competition.objects.filter(status='active')
        
        for competition in active_competitions:
            # Escuchar cambios en calificaciones
            listen_for_score_changes(competition.id, lambda data: handle_firebase_score_update(data))
            
            logger.info(f"Listener de Firebase iniciado para competencia {competition.id}")
    except Exception as e:
        logger.error(f"Error al inicializar listeners de Firebase: {e}")