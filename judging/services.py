"""
Servicio de cálculo para el sistema FEI (3 celdas).
Implementa los algoritmos de calificación y ranking según normativa ecuestre FEI.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Any, Optional
from django.db.models import Avg, F, Sum
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def calculate_parameter_score(judge_score: float, coefficient: int, max_value: int = 10) -> int:
    """
    Calcula el resultado para un parámetro según la normativa FEI.
    
    Args:
        judge_score: Calificación del juez (0-10)
        coefficient: Coeficiente según tablas FEI
        max_value: Valor máximo permitido (por defecto 10)
    
    Returns:
        int: Resultado calculado (no debe exceder max_value y debe ser un entero)
    
    Raises:
        ValueError: Si la calificación está fuera del rango 0-10
    """
    # Validar rango de calificación (0-10)
    if not 0 <= judge_score <= 10:
        raise ValueError(f'La calificación debe estar entre 0 y 10, recibido: {judge_score}')
    
    # Realizar el cálculo según la fórmula FEI
    result = float(judge_score) * coefficient
    
    # El resultado no debe exceder el valor máximo
    result = min(result, max_value)
    
    # El resultado debe ser un número entero
    return round(result)


def calculate_average_score(scores: List[Any]) -> Decimal:
    """
    Calcula el promedio de todas las calificaciones de un jinete.
    
    Args:
        scores: Lista de calificaciones (pueden ser objetos Score o valores numéricos)
    
    Returns:
        Decimal: Promedio de calificaciones con 2 decimales
    """
    if not scores:
        return Decimal('0.00')
    
    # Comprobar si los elementos son objetos Score o valores numéricos
    if hasattr(scores[0], 'calculated_result'):
        total = sum(float(score.calculated_result) for score in scores)
    else:
        total = sum(float(score) for score in scores)
    
    avg = Decimal(total) / Decimal(len(scores))
    return avg.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def convert_to_percentage(average: Decimal) -> Decimal:
    """
    Convierte un promedio a porcentaje (0-100%).
    
    Args:
        average: Promedio de calificaciones (0-10)
    
    Returns:
        Decimal: Porcentaje (0-100) con 2 decimales
    """
    percentage = (average / Decimal('10')) * Decimal('100')
    return percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_judge_ranking(judge_id: int, competition_id: int, participant_id: int) -> Dict[str, Any]:
    """
    Calcula el ranking de un juez para un participante específico.
    
    Args:
        judge_id: ID del juez
        competition_id: ID de la competencia
        participant_id: ID del participante
    
    Returns:
        Dict: Resultado del ranking para este juez
    """
    from .models import Score
    
    scores = Score.objects.filter(
        judge_id=judge_id,
        competition_id=competition_id,
        participant_id=participant_id
    )
    
    # Si no hay calificaciones, devolver valores predeterminados
    if not scores.exists():
        return {
            'judge_id': judge_id,
            'average': Decimal('0.00'),
            'percentage': Decimal('0.00'),
            'scores_count': 0
        }
    
    # Calcular promedio y porcentaje
    average = calculate_average_score(list(scores))
    percentage = convert_to_percentage(average)
    
    return {
        'judge_id': judge_id,
        'average': average,
        'percentage': percentage,
        'scores_count': scores.count()
    }


def calculate_final_ranking(competition_id: int, participant_id: int) -> Dict[str, Any]:
    """
    Calcula el ranking final de un participante combinando las calificaciones de todos los jueces.
    
    Args:
        competition_id: ID de la competencia
        participant_id: ID del participante
    
    Returns:
        Dict: Ranking final del participante
    """
    from .models import Score
    from competitions.models import CompetitionJudge
    
    # Obtener jueces asignados a la competencia
    judges = CompetitionJudge.objects.filter(
        competition_id=competition_id
    ).values_list('judge_id', flat=True)
    
    # Calcular ranking para cada juez
    judge_rankings = []
    for judge_id in judges:
        ranking = calculate_judge_ranking(judge_id, competition_id, participant_id)
        judge_rankings.append(ranking)
    
    # Si no hay rankings de jueces, devolver valores predeterminados
    if not judge_rankings:
        return {
            'participant_id': participant_id,
            'average': Decimal('0.00'),
            'percentage': Decimal('0.00'),
            'judge_count': 0
        }
    
    # Calcular promedio de porcentajes de todos los jueces
    total_percentage = sum(ranking['percentage'] for ranking in judge_rankings)
    avg_percentage = total_percentage / len(judge_rankings)
    avg_percentage = avg_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Convertir de nuevo a promedio (0-10)
    final_average = (avg_percentage / Decimal('100')) * Decimal('10')
    final_average = final_average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return {
        'participant_id': participant_id,
        'average': final_average,
        'percentage': avg_percentage,
        'judge_count': len(judge_rankings),
        'judge_rankings': judge_rankings
    }


@transaction.atomic
def update_participant_rankings(competition_id: int, recalculate_all: bool = False) -> List[Dict[str, Any]]:
    """
    Actualiza los rankings de todos los participantes en una competencia.
    
    Args:
        competition_id: ID de la competencia
        recalculate_all: Si es True, recalcula todos los rankings incluso si no hay cambios
    
    Returns:
        List[Dict]: Lista de rankings actualizados
    """
    from .models import Ranking, Score
    from competitions.models import Competition, Participant, CompetitionJudge
    
    try:
        competition = Competition.objects.get(id=competition_id)
        
        # Obtener participantes activos (no retirados)
        participants = Participant.objects.filter(
            competition=competition, 
            is_withdrawn=False
        ).select_related('rider', 'horse', 'category')
        
        # Obtener jueces asignados
        judges = CompetitionJudge.objects.filter(
            competition=competition
        ).values_list('judge_id', flat=True)
        
        rankings_data = []
        
        # Para cada participante, calcular ranking combinando calificaciones de todos los jueces
        for participant in participants:
            # Guardar posición anterior para determinar cambios de posición
            try:
                previous_ranking = Ranking.objects.get(
                    competition=competition,
                    participant=participant
                )
                previous_position = previous_ranking.position
            except Ranking.DoesNotExist:
                previous_position = None
            
            # Calcular ranking final
            final_ranking = calculate_final_ranking(competition.id, participant.id)
            
            # Añadir datos adicionales
            final_ranking['participant'] = participant
            final_ranking['previous_position'] = previous_position
            
            rankings_data.append(final_ranking)
        
        # Ordenar por porcentaje y asignar posiciones
        rankings_data.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Actualizar posiciones en la base de datos
        for position, ranking_data in enumerate(rankings_data, 1):
            participant = ranking_data['participant']
            
            Ranking.objects.update_or_create(
                competition=competition,
                participant=participant,
                defaults={
                    'average_score': ranking_data['average'],
                    'percentage': ranking_data['percentage'],
                    'position': position
                }
            )
            
            # Actualizar posición en el diccionario
            ranking_data['position'] = position
        
        # Sincronizar con Firebase si está disponible
        try:
            from .firebase import sync_rankings
            sync_rankings(competition_id, rankings_data)
        except ImportError:
            logger.warning("Módulo Firebase no disponible. No se sincronizarán los rankings.")
        except Exception as e:
            logger.error(f"Error al sincronizar rankings con Firebase: {e}")
        
        return rankings_data
    
    except Exception as e:
        logger.error(f"Error al actualizar rankings: {e}")
        raise