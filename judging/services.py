"""
Servicios de cálculo para el sistema de evaluación FEI (3 celdas)
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Any, Optional
from django.db.models import Avg, F
from django.db import transaction

from .models import Score, CompetitionParameter, Ranking, FirebaseSync
from competitions.models import Competition, Participant


def calculate_parameter_score(judge_score: float, coefficient: int) -> int:
    """
    Calcula el resultado para un parámetro según la normativa FEI
    
    Args:
        judge_score: Calificación del juez (0-10)
        coefficient: Coeficiente según tablas FEI
    
    Returns:
        int: Resultado calculado (no debe exceder 10 y debe ser un entero)
    """
    # Validar rango de calificación (0-10)
    if judge_score < 0 or judge_score > 10:
        raise ValueError('La calificación debe estar entre 0 y 10')
    
    # Realizar el cálculo según la fórmula FEI
    result = float(judge_score) * coefficient
    
    # El resultado no debe exceder 10
    result = min(result, 10)
    
    # El resultado debe ser un número entero
    return round(result)


def calculate_average_score(scores: List[Score]) -> Decimal:
    """
    Calcula el promedio de todas las calificaciones de un jinete
    
    Args:
        scores: Lista de calificaciones
    
    Returns:
        Decimal: Promedio de calificaciones
    """
    if not scores:
        return Decimal('0.00')
    
    total = sum(score.calculated_result for score in scores)
    return Decimal(total) / Decimal(len(scores))


def convert_to_percentage(average: Decimal) -> Decimal:
    """
    Convierte un promedio a porcentaje (0-100%)
    
    Args:
        average: Promedio de calificaciones (0-10)
    
    Returns:
        Decimal: Porcentaje (0-100)
    """
    percentage = (average / Decimal('10')) * Decimal('100')
    return percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_judge_ranking(scores: List[Score], parameters: List[CompetitionParameter]) -> Dict[str, Decimal]:
    """
    Calcula el ranking para un juez específico
    
    Args:
        scores: Lista de calificaciones de un juez
        parameters: Lista de parámetros de la competencia
    
    Returns:
        Dict: Diccionario con average y percentage
    """
    if not scores:
        return {'average': Decimal('0.00'), 'percentage': Decimal('0.00')}
    
    average = calculate_average_score(scores)
    percentage = convert_to_percentage(average)
    
    return {
        'average': average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'percentage': percentage
    }


def calculate_final_ranking(judge_rankings: List[Dict[str, Decimal]]) -> Dict[str, Decimal]:
    """
    Calcula el ranking final combinando las calificaciones de todos los jueces
    
    Args:
        judge_rankings: Lista de rankings por juez
    
    Returns:
        Dict: Ranking final
    """
    if not judge_rankings:
        return {'average': Decimal('0.00'), 'percentage': Decimal('0.00')}
    
    # Promediar los porcentajes de todos los jueces
    total_percentage = sum(ranking['percentage'] for ranking in judge_rankings)
    average_percentage = total_percentage / Decimal(len(judge_rankings))
    
    # Convertir de nuevo a promedio (0-10)
    final_average = (average_percentage / Decimal('100')) * Decimal('10')
    
    return {
        'average': final_average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'percentage': average_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    }


@transaction.atomic
def update_participant_rankings(competition_id: int) -> None:
    """
    Actualiza los rankings de todos los participantes en una competencia
    
    Args:
        competition_id: ID de la competencia
    """
    competition = Competition.objects.get(id=competition_id)
    participants = Participant.objects.filter(competition=competition, is_withdrawn=False)
    
    # Calcular y actualizar ranking para cada participante
    rankings = []
    positions = {}
    
    for participant in participants:
        # Obtener calificaciones agrupadas por juez
        judge_scores = {}
        
        scores = Score.objects.filter(
            competition=competition,
            participant=participant
        ).select_related('judge', 'parameter')
        
        for score in scores:
            if score.judge_id not in judge_scores:
                judge_scores[score.judge_id] = []
            judge_scores[score.judge_id].append(score)
        
        # Calcular ranking para cada juez
        judge_rankings = []
        parameters = CompetitionParameter.objects.filter(competition=competition)
        
        for judge_id, scores_list in judge_scores.items():
            ranking = calculate_judge_ranking(scores_list, parameters)
            judge_rankings.append(ranking)
        
        # Calcular ranking final
        final_ranking = calculate_final_ranking(judge_rankings)
        
        # Guardar para determinar posiciones después
        rankings.append({
            'participant': participant,
            'average': final_ranking['average'],
            'percentage': final_ranking['percentage']
        })
    
    # Ordenar por porcentaje y asignar posiciones
    sorted_rankings = sorted(rankings, key=lambda x: x['percentage'], reverse=True)
    
    for position, ranking_data in enumerate(sorted_rankings, 1):
        participant = ranking_data['participant']
        
        # Actualizar o crear objeto Ranking
        ranking, created = Ranking.objects.update_or_create(
            competition=competition,
            participant=participant,
            defaults={
                'average_score': ranking_data['average'],
                'percentage': ranking_data['percentage'],
                'position': position
            }
        )
        
        # Guardar posición para Firebase
        positions[participant.id] = position
    
    # Trigger Firebase sync
    sync_rankings_to_firebase(competition_id, rankings=sorted_rankings)
    
    return sorted_rankings


def sync_rankings_to_firebase(competition_id: int, rankings: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Sincroniza los rankings con Firebase Realtime Database
    
    Args:
        competition_id: ID de la competencia
        rankings: Lista de rankings precalculados (opcional)
    
    Returns:
        bool: True si la sincronización fue exitosa
    """
    try:
        # Aquí se implementará la sincronización con Firebase
        # Esto se desarrollará en judging/firebase.py
        
        # Marcar como sincronizado
        sync_record, created = FirebaseSync.objects.get_or_create(
            competition_id=competition_id,
            defaults={'is_synced': True}
        )
        
        if not created:
            sync_record.is_synced = True
            sync_record.error_message = None
            sync_record.save()
        
        return True
        
    except Exception as e:
        # Registrar error
        FirebaseSync.objects.update_or_create(
            competition_id=competition_id,
            defaults={
                'is_synced': False,
                'error_message': str(e)
            }
        )
        
        # Re-lanzar para manejo superior
        raise