"""
Servicio mejorado para el cálculo de puntuaciones según el sistema FEI de 3 celdas.
Este módulo implementa funciones optimizadas para la evaluación de jinetes 
según la normativa FEI.
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
    from .models import Ranking, Score, CompetitionParameter
    from competitions.models import Competition, Participant
    
    try:
        competition = Competition.objects.get(id=competition_id)
        participants = Participant.objects.filter(
            competition=competition, 
            is_withdrawn=False
        ).select_related('rider', 'horse', 'category')
        
        # Obtener parámetros de evaluación para esta competencia
        parameters = CompetitionParameter.objects.filter(
            competition=competition
        ).select_related('parameter')
        
        # Calcular y actualizar ranking para cada participante
        rankings_data = []
        
        for participant in participants:
            # Obtener todas las calificaciones de este participante agrupadas por juez
            judge_scores = {}
            scores = Score.objects.filter(
                competition=competition,
                participant=participant
            ).select_related('judge', 'parameter', 'parameter__parameter')
            
            for score in scores:
                if score.judge_id not in judge_scores:
                    judge_scores[score.judge_id] = []
                judge_scores[score.judge_id].append(score)
            
            # Calcular el promedio por juez
            judge_averages = []
            for judge_id, scores_list in judge_scores.items():
                avg = calculate_average_score(scores_list)
                percentage = convert_to_percentage(avg)
                judge_averages.append({
                    'judge_id': judge_id,
                    'average': avg,
                    'percentage': percentage
                })
            
            # Calcular el promedio final (promedio de los promedios de jueces)
            if judge_averages:
                total_percentage = sum(ja['percentage'] for ja in judge_averages)
                avg_percentage = total_percentage / len(judge_averages)
                final_average = (avg_percentage / Decimal('100')) * Decimal('10')
                
                # Formatear a 2 decimales
                final_average = final_average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                avg_percentage = avg_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                final_average = Decimal('0.00')
                avg_percentage = Decimal('0.00')
            
            # Guardar para determinar posiciones después
            rankings_data.append({
                'participant': participant,
                'participant_id': participant.id,
                'average': final_average,
                'percentage': avg_percentage,
                'judge_averages': judge_averages
            })
        
        # Ordenar por porcentaje y asignar posiciones
        sorted_rankings = sorted(rankings_data, key=lambda x: x['percentage'], reverse=True)
        
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
            
            # Añadir posición al diccionario
            ranking_data['position'] = position
        
        # Sincronizar con Firebase (si está disponible)
        try:
            from .firebase import sync_rankings
            sync_rankings(competition_id, sorted_rankings)
        except ImportError:
            logger.warning("Módulo Firebase no disponible. No se sincronizarán los rankings.")
        except Exception as e:
            logger.error(f"Error al sincronizar rankings con Firebase: {e}")
        
        return sorted_rankings
    
    except Exception as e:
        logger.error(f"Error al actualizar rankings: {e}")
        # Re-lanzar para manejo superior
        raise


def calculate_judge_scoring_statistics(judge_id: int, competition_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calcula estadísticas de calificación para un juez específico.
    
    Args:
        judge_id: ID del juez
        competition_id: ID de la competencia (opcional, si se quiere filtrar)
    
    Returns:
        Dict: Estadísticas de calificación del juez
    """
    from .models import Score
    from django.db.models import Avg, Min, Max, Count
    
    query = Score.objects.filter(judge_id=judge_id)
    
    if competition_id:
        query = query.filter(competition_id=competition_id)
    
    stats = query.aggregate(
        avg_score=Avg('value'),
        min_score=Min('value'),
        max_score=Max('value'),
        count=Count('id'),
        avg_result=Avg('calculated_result')
    )
    
    # Convertir a tipos nativos de Python
    for key in stats:
        if stats[key] is not None and isinstance(stats[key], Decimal):
            stats[key] = float(stats[key].quantize(Decimal('0.01')))
    
    # Añadir distribución de puntuaciones
    distribution = {}
    for i in range(11):  # 0 a 10
        count = query.filter(value=i).count()
        distribution[i] = count
    
    stats['distribution'] = distribution
    
    return stats


def compare_judge_scores(competition_id: int, participant_id: int) -> Dict[str, Any]:
    """
    Compara las calificaciones de diferentes jueces para un participante.
    
    Args:
        competition_id: ID de la competencia
        participant_id: ID del participante
    
    Returns:
        Dict: Comparación de calificaciones entre jueces
    """
    from .models import Score
    from django.db.models import Avg
    
    # Obtener todas las calificaciones para este participante
    scores = Score.objects.filter(
        competition_id=competition_id,
        participant_id=participant_id
    ).select_related('judge', 'parameter', 'parameter__parameter')
    
    # Agrupar por juez
    judges_data = {}
    parameters_list = set()
    
    for score in scores:
        judge_id = score.judge_id
        parameter_id = score.parameter.parameter.id
        parameter_name = score.parameter.parameter.name
        
        if judge_id not in judges_data:
            judges_data[judge_id] = {
                'id': judge_id,
                'name': f"{score.judge.first_name} {score.judge.last_name}",
                'scores': {},
                'average': 0,
                'parameters_count': 0
            }
        
        judges_data[judge_id]['scores'][parameter_id] = {
            'value': float(score.value),
            'result': float(score.calculated_result),
            'parameter_name': parameter_name
        }
        
        parameters_list.add((parameter_id, parameter_name))
    
    # Calcular promedios por juez
    for judge_id, data in judges_data.items():
        scores_sum = sum(s['value'] for s in data['scores'].values())
        data['parameters_count'] = len(data['scores'])
        data['average'] = round(scores_sum / data['parameters_count'], 2) if data['parameters_count'] > 0 else 0
    
    # Calcular variaciones y consenso
    parameter_variations = {}
    for param_id, param_name in parameters_list:
        values = []
        for judge_data in judges_data.values():
            if param_id in judge_data['scores']:
                values.append(judge_data['scores'][param_id]['value'])
        
        if values:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            
            parameter_variations[param_id] = {
                'parameter_name': param_name,
                'min': min_val,
                'max': max_val,
                'average': round(avg_val, 2),
                'variation': round(max_val - min_val, 2),
                'consensus': round(((max_val - min_val) <= 2), 2)  # Consideramos consenso si la variación es menor o igual a 2
            }
    
    return {
        'judges': list(judges_data.values()),
        'parameters': list(parameter_variations.values()),
        'judges_count': len(judges_data),
        'parameters_count': len(parameters_list)
    }