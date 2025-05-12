"""
Integración optimizada con Firebase Realtime Database para el sistema ecuestre.
Implementa sincronización bidireccional para calificaciones y rankings en tiempo real.
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from typing import Dict, List, Any, Optional, Union
from django.conf import settings
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Variables globales para mantener estado de Firebase
_firebase_initialized = False
_firebase_app = None

def initialize_firebase():
    """
    Inicializa la conexión con Firebase si no está ya inicializada.
    """
    global _firebase_initialized, _firebase_app
    
    if not _firebase_initialized:
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS', None)
        
        if not cred_path or not os.path.exists(cred_path):
            logger.warning("Credenciales de Firebase no configuradas. Funcionalidad limitada.")
            return False
        
        try:
            # Obtener la URL de la base de datos de settings
            database_url = getattr(settings, 'FIREBASE_DATABASE_URL', None)
            if not database_url:
                logger.warning("URL de Firebase no configurada. Funcionalidad limitada.")
                return False
            
            # Inicializar la aplicación Firebase
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
            _firebase_initialized = True
            logger.info("Firebase inicializado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Firebase: {e}")
            return False
    
    return _firebase_initialized

def get_firebase_ref(path: str):
    """
    Obtiene una referencia a un nodo de Firebase.
    
    Args:
        path: Ruta en la base de datos
    
    Returns:
        Referencia de Firebase
    
    Raises:
        Exception: Si no se puede obtener la referencia
    """
    try:
        initialize_firebase()
        return db.reference(path)
    except Exception as e:
        logger.error(f"Error al obtener referencia Firebase para {path}: {e}")
        raise


def decimal_to_float(obj):
    """
    Convierte objetos Decimal a float para serialización JSON.
    
    Args:
        obj: Objeto a convertir
    
    Returns:
        Objeto convertido
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    else:
        return obj


def sync_rankings(competition_id: int, rankings: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Sincroniza los rankings con Firebase.
    
    Args:
        competition_id: ID de la competencia
        rankings: Lista de rankings precalculados (opcional)
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    if not initialize_firebase():
        logger.warning("Firebase no inicializado. No se sincronizarán los rankings.")
        return False
    
    try:
        # Obtener datos si no fueron proporcionados
        if not rankings:
            from .models import Ranking
            from competitions.models import Participant
            
            rankings_queryset = Ranking.objects.filter(
                competition_id=competition_id
            ).select_related(
                'participant', 
                'participant__rider', 
                'participant__horse',
                'participant__category'
            ).order_by('position')
            
            rankings = []
            for rank in rankings_queryset:
                participant = rank.participant
                rankings.append({
                    'participant': participant,
                    'participant_id': participant.id,
                    'average': rank.average_score,
                    'percentage': rank.percentage,
                    'position': rank.position
                })
        
        # Preparar datos para Firebase
        firebase_data = {}
        for ranking in rankings:
            participant = ranking.get('participant')
            participant_id = ranking.get('participant_id') or participant.id if participant else None
            
            if not participant_id:
                continue
                
            if hasattr(participant, 'rider') and hasattr(participant, 'horse'):
                rider = participant.rider
                horse = participant.horse
                category = participant.category
                
                firebase_data[str(participant_id)] = {
                    'rider': {
                        'id': rider.id,
                        'firstName': rider.first_name,
                        'lastName': rider.last_name,
                        'nationality': rider.nationality or '',
                        'fullName': f"{rider.first_name} {rider.last_name}"
                    },
                    'horse': {
                        'id': horse.id,
                        'name': horse.name,
                        'breed': horse.breed or '',
                        'color': horse.color or ''
                    },
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'code': category.code
                    } if category else {},
                    'number': participant.number,
                    'order': participant.order,
                    'average': decimal_to_float(ranking.get('average')),
                    'percentage': decimal_to_float(ranking.get('percentage')),
                    'position': ranking.get('position', 0),
                    'previousPosition': getattr(participant, 'previous_position', None),
                    'withdrawn': participant.is_withdrawn
                }
            else:
                # Datos simplificados si no hay relaciones cargadas
                firebase_data[str(participant_id)] = {
                    'participant_id': participant_id,
                    'average': decimal_to_float(ranking.get('average')),
                    'percentage': decimal_to_float(ranking.get('percentage')),
                    'position': ranking.get('position', 0)
                }
        
        # Subir a Firebase
        rankings_ref = get_firebase_ref(f'rankings/{competition_id}')
        rankings_ref.set(firebase_data)
        
        # Actualizar estado de sincronización
        from .models import FirebaseSync
        FirebaseSync.objects.update_or_create(
            competition_id=competition_id,
            defaults={
                'is_synced': True,
                'error_message': None
            }
        )
        
        logger.info(f"Rankings sincronizados para competencia {competition_id}: {len(rankings)} participantes")
        return True
        
    except Exception as e:
        logger.error(f"Error al sincronizar rankings con Firebase: {e}")
        
        # Registrar error
        from .models import FirebaseSync
        FirebaseSync.objects.update_or_create(
            competition_id=competition_id,
            defaults={
                'is_synced': False,
                'error_message': str(e)
            }
        )
        
        # No relanzar para manejo superior
        return False  # Cambiado de raise para evitar propagación de errores


def sync_scores(score_id: int) -> bool:
    """
    Sincroniza una calificación específica con Firebase.
    
    Args:
        score_id: ID de la calificación
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    try:
        from .models import Score
        
        score = Score.objects.select_related(
            'judge', 'participant', 'competition', 'parameter', 'parameter__parameter'
        ).get(id=score_id)
        
        # Preparar datos para Firebase
        score_data = {
            'id': score.id,
            'judgeId': score.judge.id,
            'judgeName': f"{score.judge.first_name} {score.judge.last_name}",
            'parameterId': score.parameter.parameter.id,
            'parameterName': score.parameter.parameter.name,
            'value': float(score.value),
            'calculatedResult': float(score.calculated_result),
            'comments': score.comments or '',
            'isEdited': score.is_edited,
            'updatedAt': score.updated_at.isoformat() if score.updated_at else None
        }
        
        # Subir a Firebase
        scores_ref = get_firebase_ref(
            f'scores/{score.competition.id}/{score.participant.id}/{score.judge.id}/{score.parameter.parameter.id}'
        )
        scores_ref.set(score_data)
        
        logger.info(f"Calificación {score_id} sincronizada con Firebase")
        return True
        
    except Exception as e:
        logger.error(f"Error al sincronizar calificación {score_id} con Firebase: {e}")
        # Re-lanzar para manejo superior
        raise


def sync_participant_scores(competition_id: int, participant_id: int, judge_id: Optional[int] = None) -> bool:
    """
    Sincroniza todas las calificaciones de un participante.
    
    Args:
        competition_id: ID de la competencia
        participant_id: ID del participante
        judge_id: ID del juez (opcional, si se quieren solo las de un juez)
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    try:
        from .models import Score
        
        # Construir query base
        scores_query = Score.objects.filter(
            competition_id=competition_id,
            participant_id=participant_id
        ).select_related(
            'judge', 'parameter', 'parameter__parameter'
        )
        
        # Filtrar por juez si se especifica
        if judge_id:
            scores_query = scores_query.filter(judge_id=judge_id)
        
        # Agrupar por juez
        judge_scores = {}
        for score in scores_query:
            if score.judge_id not in judge_scores:
                judge_scores[score.judge_id] = {
                    'judgeId': score.judge_id,
                    'judgeName': f"{score.judge.first_name} {score.judge.last_name}",
                    'parameters': {}
                }
            
            judge_scores[score.judge_id]['parameters'][score.parameter.parameter.id] = {
                'id': score.id,
                'value': float(score.value),
                'calculatedResult': float(score.calculated_result),
                'parameterName': score.parameter.parameter.name,
                'coefficient': score.parameter.effective_coefficient,
                'comments': score.comments or '',
                'isEdited': score.is_edited,
                'updatedAt': score.updated_at.isoformat() if score.updated_at else None
            }
        
        # Subir a Firebase
        for judge_id, judge_data in judge_scores.items():
            scores_ref = get_firebase_ref(
                f'scores/{competition_id}/{participant_id}/{judge_id}'
            )
            scores_ref.set(judge_data)
        
        logger.info(f"Calificaciones sincronizadas para participante {participant_id} en competencia {competition_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error al sincronizar calificaciones con Firebase: {e}")
        # Re-lanzar para manejo superior
        raise


def listen_for_score_changes(competition_id: int, callback):
    """
    Escucha cambios en las calificaciones en Firebase.
    
    Args:
        competition_id: ID de la competencia
        callback: Función a llamar cuando haya cambios
    """
    try:
        scores_ref = get_firebase_ref(f'scores/{competition_id}')
        scores_ref.listen(callback)
        logger.info(f"Escuchando cambios en calificaciones para competencia {competition_id}")
    except Exception as e:
        logger.error(f"Error al escuchar cambios en Firebase: {e}")
        raise


def update_score_from_firebase(data: Dict[str, Any]) -> bool:
    """
    Actualiza una calificación a partir de datos recibidos de Firebase.
    
    Args:
        data: Datos de la calificación
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    try:
        from .models import Score, CompetitionParameter
        
        competition_id = data.get('competitionId')
        participant_id = data.get('participantId')
        judge_id = data.get('judgeId')
        parameter_id = data.get('parameterId')
        value = data.get('value')
        
        if not all([competition_id, participant_id, judge_id, parameter_id, value is not None]):
            logger.warning(f"Datos incompletos recibidos de Firebase: {data}")
            return False
        
        # Obtener parámetro de la competencia
        param = CompetitionParameter.objects.get(
            competition_id=competition_id,
            parameter_id=parameter_id
        )
        
        # Actualizar o crear calificación
        score, created = Score.objects.update_or_create(
            competition_id=competition_id,
            participant_id=participant_id,
            judge_id=judge_id,
            parameter=param,
            defaults={
                'value': value,
                'comments': data.get('comments', ''),
                'is_edited': data.get('isEdited', False),
                'edit_reason': data.get('editReason', 'Actualización desde Firebase')
                # calculated_result se calcula automáticamente en el save()
            }
        )
        
        logger.info(
            f"Calificación {'creada' if created else 'actualizada'} desde Firebase: "
            f"competencia {competition_id}, participante {participant_id}, "
            f"juez {judge_id}, parámetro {parameter_id}"
        )
        
        # Actualizar rankings
        from .services import update_participant_rankings
        update_participant_rankings(competition_id)
        
        return True
    
    except Exception as e:
        logger.error(f"Error al actualizar calificación desde Firebase: {e}")
        return False


def verify_firebase_connection() -> Dict[str, Any]:
    """
    Verifica la conexión con Firebase y devuelve estado.
    
    Returns:
        Dict: Estado de la conexión
    """
    try:
        initialize_firebase()
        
        # Intentar leer un nodo de prueba
        test_ref = get_firebase_ref('connection-test')
        test_ref.set({
            'timestamp': {'.sv': 'timestamp'},
            'message': 'Test connection'
        })
        
        test_data = test_ref.get()
        
        return {
            'connected': True,
            'timestamp': test_data.get('timestamp'),
            'message': 'Conexión exitosa con Firebase'
        }
    except Exception as e:
        logger.error(f"Error al verificar conexión con Firebase: {e}")
        return {
            'connected': False,
            'error': str(e),
            'message': 'Error de conexión con Firebase'
        }


def delete_competition_data(competition_id: int) -> bool:
    """
    Elimina todos los datos de una competencia en Firebase.
    
    Args:
        competition_id: ID de la competencia
    
    Returns:
        bool: True si la eliminación fue exitosa
    """
    try:
        # Eliminar rankings
        rankings_ref = get_firebase_ref(f'rankings/{competition_id}')
        rankings_ref.delete()
        
        # Eliminar calificaciones
        scores_ref = get_firebase_ref(f'scores/{competition_id}')
        scores_ref.delete()
        
        logger.info(f"Datos eliminados de Firebase para competencia {competition_id}")
        return True
    except Exception as e:
        logger.error(f"Error al eliminar datos de Firebase: {e}")
        return False