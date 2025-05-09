# backend/evaluaciones/utils.py

from django.db.models import Avg, Sum, F, Q, Count, ExpressionWrapper, FloatField
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

def calcular_puntaje_evaluacion(evaluacion):
    """
    Calcula el puntaje total de una evaluación basado en las puntuaciones
    de los criterios y sus pesos respectivos.
    
    Args:
        evaluacion: Instancia del modelo Evaluacion
        
    Returns:
        Decimal: Puntaje total calculado
    """
    from .models import Puntuacion
    
    puntuaciones = Puntuacion.objects.filter(
        evaluacion=evaluacion
    ).select_related('criterio')
    
    if not puntuaciones:
        return None
    
    puntaje_total = Decimal('0.00')
    
    for puntuacion in puntuaciones:
        puntaje_criterio = puntuacion.valor * puntuacion.criterio.peso
        puntaje_total += puntaje_criterio
    
    # Redondear a 2 decimales
    return puntaje_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def verificar_criterios_evaluados(evaluacion):
    """
    Verifica si todos los criterios de la categoría han sido evaluados.
    
    Args:
        evaluacion: Instancia del modelo Evaluacion
        
    Returns:
        bool: True si todos los criterios han sido evaluados, False en caso contrario
        dict: Información detallada sobre los criterios evaluados y faltantes
    """
    from competencias.models import CriterioEvaluacion
    
    # Obtener todos los criterios de la categoría
    criterios = CriterioEvaluacion.objects.filter(
        categoria=evaluacion.inscripcion.categoria
    )
    total_criterios = criterios.count()
    
    # Obtener los criterios que ya han sido evaluados
    criterios_evaluados = evaluacion.puntuaciones.values_list('criterio_id', flat=True)
    criterios_evaluados_count = len(criterios_evaluados)
    
    # Determinar si todos los criterios han sido evaluados
    todos_evaluados = criterios_evaluados_count == total_criterios
    
    # Obtener criterios faltantes si no están todos evaluados
    criterios_faltantes = []
    if not todos_evaluados:
        criterios_faltantes = criterios.exclude(
            id__in=criterios_evaluados
        ).values('id', 'nombre', 'orden')
    
    return {
        'completo': todos_evaluados,
        'evaluados': criterios_evaluados_count,
        'total': total_criterios,
        'criterios_faltantes': list(criterios_faltantes)
    }

def finalizar_evaluacion(evaluacion):
    """
    Finaliza una evaluación, calculando el puntaje total y actualizando su estado.
    
    Args:
        evaluacion: Instancia del modelo Evaluacion
        
    Returns:
        bool: True si la evaluación se finalizó correctamente, False en caso contrario
        str: Mensaje informativo
    """
    # Verificar si todos los criterios han sido evaluados
    verificacion = verificar_criterios_evaluados(evaluacion)
    
    if not verificacion['completo']:
        return False, f"Faltan {verificacion['total'] - verificacion['evaluados']} criterios por evaluar"
    
    # Calcular el puntaje total
    puntaje_total = calcular_puntaje_evaluacion(evaluacion)
    
    if puntaje_total is None:
        return False, "No hay puntuaciones registradas para esta evaluación"
    
    # Actualizar la evaluación
    evaluacion.puntaje_total = puntaje_total
    evaluacion.estado = 'completada'
    evaluacion.fecha_finalizacion = timezone.now()
    evaluacion.save(update_fields=['puntaje_total', 'estado', 'fecha_finalizacion'])
    
    # Verificar si todas las evaluaciones para esta inscripción están completas
    verificar_completitud_inscripcion(evaluacion.inscripcion)
    
    return True, f"Evaluación finalizada exitosamente con puntaje total: {puntaje_total}"

def verificar_completitud_inscripcion(inscripcion):
    """
    Verifica si todas las evaluaciones de una inscripción están completas
    y actualiza el estado de la inscripción si es necesario.
    
    Args:
        inscripcion: Instancia del modelo Inscripcion
    """
    from .models import Evaluacion
    
    # Contar cuántas evaluaciones existen y cuántas están completas
    total_evaluaciones = Evaluacion.objects.filter(inscripcion=inscripcion).count()
    evaluaciones_completas = Evaluacion.objects.filter(
        inscripcion=inscripcion, 
        estado='completada'
    ).count()
    
    # Si todas las evaluaciones están completas, actualizar el estado de la inscripción
    if total_evaluaciones > 0 and total_evaluaciones == evaluaciones_completas:
        inscripcion.estado = 'completada'
        inscripcion.save(update_fields=['estado'])

def obtener_estadisticas_evaluaciones_competencia(competencia_id):
    """
    Obtiene estadísticas de evaluaciones para una competencia.
    
    Args:
        competencia_id: ID de la competencia
        
    Returns:
        dict: Estadísticas de evaluaciones
    """
    from .models import Evaluacion
    from competencias.models import Competencia, Categoria
    
    try:
        competencia = Competencia.objects.get(id=competencia_id)
    except Competencia.DoesNotExist:
        return {'error': 'Competencia no encontrada'}
    
    # Estadísticas generales
    total_evaluaciones = Evaluacion.objects.filter(
        inscripcion__competencia=competencia
    ).count()
    
    evaluaciones_completas = Evaluacion.objects.filter(
        inscripcion__competencia=competencia,
        estado='completada'
    ).count()
    
    evaluaciones_pendientes = Evaluacion.objects.filter(
        inscripcion__competencia=competencia,
        estado='pendiente'
    ).count()
    
    evaluaciones_en_progreso = Evaluacion.objects.filter(
        inscripcion__competencia=competencia,
        estado='en_progreso'
    ).count()
    
    # Estadísticas por categoría
    categorias = Categoria.objects.filter(competencia=competencia)
    estadisticas_categorias = []
    
    for categoria in categorias:
        evaluaciones_categoria = Evaluacion.objects.filter(
            inscripcion__competencia=competencia,
            inscripcion__categoria=categoria
        )
        
        stats_categoria = {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'total': evaluaciones_categoria.count(),
            'completas': evaluaciones_categoria.filter(estado='completada').count(),
            'pendientes': evaluaciones_categoria.filter(estado='pendiente').count(),
            'en_progreso': evaluaciones_categoria.filter(estado='en_progreso').count()
        }
        
        estadisticas_categorias.append(stats_categoria)
    
    # Estadísticas de puntajes
    puntajes = Evaluacion.objects.filter(
        inscripcion__competencia=competencia,
        estado='completada',
        puntaje_total__isnull=False
    ).aggregate(
        promedio=Avg('puntaje_total'),
        maximo=Max('puntaje_total'),
        minimo=Min('puntaje_total')
    )
    
    return {
        'competencia': {
            'id': competencia.id,
            'nombre': competencia.nombre,
            'estado': competencia.estado
        },
        'totales': {
            'evaluaciones': total_evaluaciones,
            'completas': evaluaciones_completas,
            'pendientes': evaluaciones_pendientes,
            'en_progreso': evaluaciones_en_progreso,
            'porcentaje_completitud': (evaluaciones_completas / total_evaluaciones * 100) if total_evaluaciones > 0 else 0
        },
        'puntajes': {
            'promedio': float(puntajes['promedio']) if puntajes['promedio'] else None,
            'maximo': float(puntajes['maximo']) if puntajes['maximo'] else None,
            'minimo': float(puntajes['minimo']) if puntajes['minimo'] else None
        },
        'categorias': estadisticas_categorias
    }

def obtener_puntajes_por_criterio(evaluacion):
    """
    Obtiene un desglose de los puntajes por criterio para una evaluación.
    
    Args:
        evaluacion: Instancia del modelo Evaluacion
        
    Returns:
        list: Lista de diccionarios con la información de puntaje por criterio
    """
    from .models import Puntuacion
    
    puntuaciones = Puntuacion.objects.filter(
        evaluacion=evaluacion
    ).select_related('criterio')
    
    resultado = []
    
    for puntuacion in puntuaciones:
        puntaje_ponderado = puntuacion.valor * puntuacion.criterio.peso
        porcentaje = (puntuacion.valor / puntuacion.criterio.puntaje_maximo) * 100
        
        resultado.append({
            'criterio_id': puntuacion.criterio.id,
            'criterio_nombre': puntuacion.criterio.nombre,
            'criterio_orden': puntuacion.criterio.orden,
            'puntaje_maximo': float(puntuacion.criterio.puntaje_maximo),
            'peso': float(puntuacion.criterio.peso),
            'valor': float(puntuacion.valor),
            'puntaje_ponderado': float(puntaje_ponderado),
            'porcentaje': float(porcentaje),
            'comentario': puntuacion.comentario
        })
    
    # Ordenar por el orden del criterio
    return sorted(resultado, key=lambda x: x['criterio_orden'])