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
        print("No hay calificaciones para calcular promedio.")
        return Decimal('0.00')
    
    # CORRECCIÓN: Extraer explícitamente los valores
    values = []
    for i, score in enumerate(scores):
        if hasattr(score, 'calculated_result'):
            # Extraer el valor calculated_result
            value = float(score.calculated_result)
            print(f"Score #{i+1}: valor calculated_result = {value}")
            values.append(value)
        elif hasattr(score, 'value'):
            # Tal vez solo tiene value (sin resultado calculado)
            value = float(score.value)
            print(f"Score #{i+1}: valor directo = {value}")
            values.append(value)
        elif isinstance(score, (int, float, Decimal)):
            # Es un valor numérico directo
            value = float(score)
            print(f"Score #{i+1}: valor numérico = {value}")
            values.append(value)
        else:
            # Desconocido, intenta convertir
            try:
                value = float(score)
                print(f"Score #{i+1}: valor convertido = {value}")
                values.append(value)
            except (TypeError, ValueError):
                print(f"Score #{i+1}: No se pudo convertir a número: {score}")
    
    if not values:
        print("ADVERTENCIA: No se pudieron extraer valores numéricos de los scores")
        return Decimal('0.00')
    
    # Calcular promedio
    total = sum(values)
    if len(values) == 0:
        print("ADVERTENCIA: División por cero al calcular promedio")
        return Decimal('0.00')
    
    avg = Decimal(str(total / len(values)))
    print(f"Promedio calculado: {float(avg)} (suma: {total}, cantidad: {len(values)})")
    
    # CORRECCIÓN: Agrega logging para depuración
    if avg == 0 and total > 0:
        print(f"ADVERTENCIA: Promedio calculado como 0 aunque el total es {total} (valores: {values})")
    
    return avg.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def convert_to_percentage(average: Decimal) -> Decimal:
    """
    Convierte un promedio a porcentaje (0-100%).
    
    Args:
        average: Promedio de calificaciones (0-10)
    
    Returns:
        Decimal: Porcentaje (0-100) con 2 decimales
    """
    # CORRECCIÓN: Asegúrate de que average sea un Decimal y no cero
    if average is None:
        return Decimal('0.00')
    
    if not isinstance(average, Decimal):
        average = Decimal(str(average))
    
    # CORRECCIÓN: Asegúrate de que la multiplicación ocurra con Decimals
    percentage = (average / Decimal('10')) * Decimal('100')
    
    # CORRECCIÓN: Verifica que el resultado no sea cero antes de retornar
    if percentage == 0 and average > 0:
        logger.warning(f"Problema en la conversión a porcentaje: average={average}, porcentaje calculado={percentage}")
    
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
    
    # MODIFICACIÓN: Extraer los valores calculated_result explícitamente
    results = [float(score.calculated_result) for score in scores]
    
    # Imprime los valores para depuración
    print(f"Valores calculated_result para juez {judge_id}, participante {participant_id}: {results}")
    
    # Calcular promedio manualmente si es necesario
    if results:
        avg = sum(results) / len(results)
        average = Decimal(str(avg))
        # Convertir a porcentaje manualmente: (promedio / 10) * 100
        percentage = (average / Decimal('10')) * Decimal('100')
    else:
        average = Decimal('0.00')
        percentage = Decimal('0.00')
    
    # Imprimir los resultados calculados
    print(f"Juez {judge_id}, Participante {participant_id}: average={float(average)}, percentage={float(percentage)}%")
    
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
    
     # MODIFICACIÓN: Calcular promedio de porcentajes de todos los jueces con depuración
    percentages = [jr['percentage'] for jr in judge_rankings]
    print(f"Porcentajes para participante {participant_id}: {[float(p) for p in percentages]}")
    
    if percentages:
        total_percentage = sum(float(p) for p in percentages)
        avg_percentage = Decimal(str(total_percentage / len(percentages)))
        # Verificar que no sea cero
        if avg_percentage == 0 and any(p > 0 for p in percentages):
            print(f"ERROR: avg_percentage es 0 aunque hay porcentajes > 0")
    else:
        avg_percentage = Decimal('0.00')
    
    # Convertir de nuevo a promedio (0-10)
    final_average = (avg_percentage / Decimal('100')) * Decimal('10')
    
    # Imprimir resultado final
    print(f"Ranking final participante {participant_id}: average={float(final_average)}, percentage={float(avg_percentage)}%")
    
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
        
        print(f"Procesando {participants.count()} participantes para la competencia {competition.name}")
        
        # Obtener jueces asignados
        judges = CompetitionJudge.objects.filter(
            competition=competition
        ).values_list('judge_id', flat=True)
        
        print(f"Jueces asignados a la competencia: {len(judges)}")
        
        rankings_data = []
        
        # Para cada participante, calcular ranking combinando calificaciones de todos los jueces
        for participant in participants:
            print(f"\nCalculando ranking para participante: {participant} (ID: {participant.id})")
            
            # Guardar posición anterior para determinar cambios de posición
            try:
                previous_ranking = Ranking.objects.get(
                    competition=competition,
                    participant=participant
                )
                previous_position = previous_ranking.position
                print(f"Posición anterior: {previous_position}")
            except Ranking.DoesNotExist:
                previous_position = None
                print("No hay ranking previo")
            
            # Verificar si hay calificaciones para este participante
            score_count = Score.objects.filter(
                competition_id=competition_id,
                participant_id=participant.id
            ).count()
            print(f"Calificaciones encontradas: {score_count}")
            
            # Calcular ranking final
            final_ranking = calculate_final_ranking(competition.id, participant.id)
            
            print(f"Ranking calculado: promedio={float(final_ranking['average'])}, porcentaje={float(final_ranking['percentage'])}%")
            
            # Añadir datos adicionales
            final_ranking['participant'] = participant
            final_ranking['previous_position'] = previous_position
            
            rankings_data.append(final_ranking)
        
        # Ordenar por porcentaje y asignar posiciones
        rankings_data.sort(key=lambda x: x['percentage'], reverse=True)
        
        print("\nRankings ordenados por porcentaje:")
        for i, rank in enumerate(rankings_data):
            print(f"Posición {i+1}: {rank['participant']} - {float(rank['percentage'])}%")
        
        # Actualizar posiciones en la base de datos
        for position, ranking_data in enumerate(rankings_data, 1):
            participant = ranking_data['participant']
            percentage = ranking_data.get('percentage', Decimal('0.00'))
            average = ranking_data.get('average', Decimal('0.00'))
            
            print(f"\nGuardando ranking: Participante={participant}, Promedio={float(average)}, Porcentaje={float(percentage)}%")
            
            # Verifica que percentage no sea cero si hay calificaciones
            if float(percentage) == 0:
                has_scores = Score.objects.filter(
                    competition_id=competition_id,
                    participant=participant
                ).exists()
                if has_scores:
                    print(f"ADVERTENCIA: Porcentaje es 0 aunque hay calificaciones para {participant}")
                    # Recalcular en el momento
                    scores = Score.objects.filter(
                        competition_id=competition_id,
                        participant=participant
                    )
                    results = [float(s.calculated_result) for s in scores]
                    if results:
                        avg = sum(results) / len(results)
                        new_percentage = (avg / 10) * 100
                        percentage = Decimal(str(new_percentage))
                        print(f"Porcentaje recalculado: {float(percentage)}%")
            
            Ranking.objects.update_or_create(
                competition=competition,
                participant=participant,
                defaults={
                    'average_score': average,
                    'percentage': percentage,
                    'position': position
                }
            )
            
            # Verifica después de guardar
            saved_ranking = Ranking.objects.get(competition=competition, participant=participant)
            print(f"Ranking guardado: {saved_ranking}, Porcentaje guardado: {float(saved_ranking.percentage)}%")
            
            # Actualizar posición en el diccionario
            ranking_data['position'] = position
        
        # Sincronizar con Firebase si está disponible
        try:
            from .firebase import sync_rankings
            sync_success = sync_rankings(competition_id, rankings_data)
            print(f"Sincronización con Firebase: {'Exitosa' if sync_success else 'Fallida'}")
        except ImportError:
            print("Módulo Firebase no disponible. No se sincronizarán los rankings.")
        except Exception as e:
            logger.error(f"Error al sincronizar rankings con Firebase: {e}")
            print(f"Error en sincronización Firebase: {str(e)}")
        
        return rankings_data
    
    except Exception as e:
        logger.error(f"Error al actualizar rankings: {e}")
        import traceback
        traceback.print_exc()
        print(f"ERROR en update_participant_rankings: {str(e)}")
        raise

def calculate_judge_scoring_statistics(judge_id: int, competition_id: int = None) -> dict:
    """
    Calcula estadísticas de calificación de un juez.
    
    Args:
        judge_id: ID del juez
        competition_id: ID de la competencia (opcional)
    
    Returns:
        Dict: Estadísticas de calificación
    """
    from .models import Score
    from django.db.models import Avg, Count, Min, Max
    from collections import defaultdict
    
    # Construir query base
    query = Score.objects.filter(judge_id=judge_id)
    
    # Filtrar por competencia si se especifica
    if competition_id:
        query = query.filter(competition_id=competition_id)
    
    # Calcular estadísticas generales
    stats = query.aggregate(
        avg_score=Avg('value'),
        min_score=Min('value'),
        max_score=Max('value'),
        count=Count('id'),
        avg_result=Avg('calculated_result')
    )
    
    # Si no hay calificaciones, devolver valores por defecto
    if not stats['count']:
        return {
            'avg_score': 0,
            'min_score': 0,
            'max_score': 0,
            'count': 0,
            'avg_result': 0,
            'distribution': {},
            'competition_stats': {}
        }
    
    # Calcular distribución de calificaciones
    distribution = defaultdict(int)
    for score in query.values_list('value', flat=True):
        # Redondear a entero para agrupar
        rounded = round(float(score))
        distribution[rounded] += 1
    
    # Convertir a diccionario normal
    distribution_dict = dict(distribution)
    
    # Calcular estadísticas por competencia
    competition_stats = {}
    if not competition_id:
        competitions = query.values_list('competition_id', flat=True).distinct()
        for comp_id in competitions:
            comp_query = query.filter(competition_id=comp_id)
            comp_stats = comp_query.aggregate(
                avg_score=Avg('value'),
                count=Count('id')
            )
            competition_stats[comp_id] = comp_stats
    
    return {
        'avg_score': float(stats['avg_score']) if stats['avg_score'] else 0,
        'min_score': float(stats['min_score']) if stats['min_score'] else 0,
        'max_score': float(stats['max_score']) if stats['max_score'] else 0,
        'count': stats['count'],
        'avg_result': float(stats['avg_result']) if stats['avg_result'] else 0,
        'distribution': distribution_dict,
        'competition_stats': competition_stats
    }


def compare_judge_scores(competition_id: int, participant_id: int) -> dict:
    """
    Compara calificaciones entre jueces para un participante.
    
    Args:
        competition_id: ID de la competencia
        participant_id: ID del participante
    
    Returns:
        Dict: Comparación de calificaciones
    """
    from .models import Score
    from competitions.models import CompetitionJudge
    from django.db.models import Avg
    
    # Obtener jueces asignados a la competencia
    judges = CompetitionJudge.objects.filter(
        competition_id=competition_id
    ).select_related('judge').order_by('id')
    
    # Si no hay jueces, devolver datos básicos
    if not judges:
        return {
            'judges': [],
            'parameters': [],
            'judges_count': 0,
            'parameters_count': 0
        }
    
    # Obtener parámetros de competencia
    from .models import CompetitionParameter
    parameters = CompetitionParameter.objects.filter(
        competition_id=competition_id
    ).select_related('parameter').order_by('order')
    
    # Obtener calificaciones para cada juez
    judge_scores = {}
    for judge in judges:
        scores = Score.objects.filter(
            competition_id=competition_id,
            participant_id=participant_id,
            judge=judge.judge
        ).select_related('parameter', 'parameter__parameter')
        
        judge_scores[judge.judge.id] = {
            'judge_id': judge.judge.id,
            'judge_name': f"{judge.judge.first_name} {judge.judge.last_name}",
            'is_head_judge': judge.is_head_judge,
            'scores': {score.parameter.parameter_id: float(score.value) for score in scores}
        }
    
    # Calcular promedio por parámetro
    param_averages = {}
    for param in parameters:
        scores = Score.objects.filter(
            competition_id=competition_id,
            participant_id=participant_id,
            parameter=param
        ).aggregate(avg=Avg('value'))
        
        param_averages[param.parameter.id] = float(scores['avg']) if scores['avg'] else 0
    
    # Preparar datos de respuesta
    judges_data = []
    for judge in judges:
        judges_data.append({
            'id': judge.judge.id,
            'name': f"{judge.judge.first_name} {judge.judge.last_name}",
            'is_head_judge': judge.is_head_judge,
            'scores': judge_scores.get(judge.judge.id, {}).get('scores', {})
        })
    
    parameters_data = []
    for param in parameters:
        parameters_data.append({
            'id': param.parameter.id,
            'name': param.parameter.name,
            'coefficient': param.effective_coefficient,
            'order': param.order,
            'average': param_averages.get(param.parameter.id, 0)
        })
    
    return {
        'judges': judges_data,
        'parameters': parameters_data,
        'judges_count': len(judges_data),
        'parameters_count': len(parameters_data)
    }