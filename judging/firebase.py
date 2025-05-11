"""
Integración con Firebase Realtime Database para el sistema ecuestre
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from typing import Dict, List, Any, Optional
from django.conf import settings

from competitions.models import Competition, Participant
from .models import Ranking, Score


# Inicialización de Firebase
def initialize_firebase():
    """Inicializa la conexión con Firebase si no está ya inicializada"""
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS
        
        if not cred_path or not os.path.exists(cred_path):
            raise ValueError("Credenciales de Firebase no configuradas correctamente")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL
        })


def get_firebase_ref(path: str):
    """
    Obtiene una referencia a un nodo de Firebase
    
    Args:
        path: Ruta en la base de datos
    
    Returns:
        Referencia de Firebase
    """
    initialize_firebase()
    return db.reference(path)


def sync_rankings(competition_id: int, rankings: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Sincroniza los rankings con Firebase
    
    Args:
        competition_id: ID de la competencia
        rankings: Lista de rankings precalculados (opcional)
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    # Obtener datos si no fueron proporcionados
    if not rankings:
        competition = Competition.objects.get(id=competition_id)
        rankings_queryset = Ranking.objects.filter(
            competition=competition
        ).select_related(
            'participant', 
            'participant__rider', 
            'participant__horse'
        ).order_by('position')
        
        rankings = []
        for rank in rankings_queryset:
            participant = rank.participant
            rankings.append({
                'participant': participant,
                'average': rank.average_score,
                'percentage': rank.percentage,
                'position': rank.position
            })
    
    # Preparar datos para Firebase
    firebase_data = {}
    for ranking in rankings:
        participant = ranking['participant']
        rider = participant.rider
        horse = participant.horse
        
        firebase_data[str(participant.id)] = {
            'rider': {
                'id': rider.id,
                'firstName': rider.first_name,
                'lastName': rider.last_name,
                'nationality': rider.nationality or ''
            },
            'horse': {
                'id': horse.id,
                'name': horse.name,
                'breed': horse.breed or ''
            },
            'number': participant.number,
            'average': float(ranking['average']),
            'percentage': float(ranking['percentage']),
            'position': ranking.get('position', 0)
        }
    
    # Subir a Firebase
    rankings_ref = get_firebase_ref(f'rankings/{competition_id}')
    rankings_ref.set(firebase_data)
    
    return True


def sync_scores(score_id: int) -> bool:
    """
    Sincroniza una calificación específica con Firebase
    
    Args:
        score_id: ID de la calificación
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    score = Score.objects.select_related(
        'judge', 'participant', 'competition', 'parameter'
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
        'updatedAt': score.updated_at.isoformat()
    }
    
    # Subir a Firebase
    scores_ref = get_firebase_ref(
        f'scores/{score.competition.id}/{score.participant.id}/{score.judge.id}/{score.parameter.parameter.id}'
    )
    scores_ref.set(score_data)
    
    return True


def sync_participant_scores(competition_id: int, participant_id: int, judge_id: int = None) -> bool:
    """
    Sincroniza todas las calificaciones de un participante
    
    Args:
        competition_id: ID de la competencia
        participant_id: ID del participante
        judge_id: ID del juez (opcional, si se quieren solo las de un juez)
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
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
            judge_scores[score.judge_id] = {}
        
        judge_scores[score.judge_id][score.parameter.parameter.id] = {
            'id': score.id,
            'value': float(score.value),
            'calculatedResult': float(score.calculated_result),
            'parameterName': score.parameter.parameter.name,
            'coefficient': score.parameter.effective_coefficient,
            'updatedAt': score.updated_at.isoformat()
        }
    
    # Subir a Firebase
    for judge_id, params in judge_scores.items():
        scores_ref = get_firebase_ref(
            f'scores/{competition_id}/{participant_id}/{judge_id}'
        )
        scores_ref.set(params)
    
    return True


def listen_for_score_changes(competition_id: int, callback):
    """
    Escucha cambios en las calificaciones en Firebase
    
    Args:
        competition_id: ID de la competencia
        callback: Función a llamar cuando haya cambios
    """
    scores_ref = get_firebase_ref(f'scores/{competition_id}')
    scores_ref.listen(callback)


def update_score_from_firebase(data: Dict[str, Any]) -> bool:
    """
    Actualiza una calificación a partir de datos recibidos de Firebase
    
    Args:
        data: Datos de la calificación
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    try:
        competition_id = data.get('competitionId')
        participant_id = data.get('participantId')
        judge_id = data.get('judgeId')
        parameter_id = data.get('parameterId')
        value = data.get('value')
        
        if not all([competition_id, participant_id, judge_id, parameter_id, value is not None]):
            return False
        
        # Obtener parámetro de la competencia
        from .models import CompetitionParameter
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
                # calculated_result se calcula automáticamente en el save()
            }
        )
        
        # Actualizar rankings
        from .services import update_participant_rankings
        update_participant_rankings(competition_id)
        
        return True
    
    except Exception as e:
        print(f"Error al actualizar calificación desde Firebase: {e}")
        return False