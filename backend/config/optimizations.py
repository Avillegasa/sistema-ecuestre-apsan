# backend/config/optimizations.py

from django.db.models import Prefetch, Count, F, Q, Sum, Avg, Max, Min
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def generate_cache_key(prefix, *args, **kwargs):
    """
    Genera una clave de caché única basada en los argumentos proporcionados.
    
    Args:
        prefix (str): Prefijo para la clave de caché
        *args: Argumentos posicionales para incluir en la clave
        **kwargs: Argumentos con nombre para incluir en la clave
        
    Returns:
        str: Clave de caché única
    """
    # Convertir argumentos a una representación de cadena consistente
    key_parts = [prefix]
    
    for arg in args:
        key_parts.append(str(arg))
    
    # Ordenar kwargs por clave para consistencia
    for key in sorted(kwargs.keys()):
        key_parts.append(f"{key}:{kwargs[key]}")
    
    # Crear representación de cadena y calcular hash md5
    key_string = ':'.join(key_parts)
    return f"ecuestre:{hashlib.md5(key_string.encode()).hexdigest()}"

def cached_queryset(prefix, timeout=3600, *args, **kwargs):
    """
    Decorador para almacenar en caché el resultado de una función que devuelve un queryset.
    
    Args:
        prefix (str): Prefijo para la clave de caché
        timeout (int): Tiempo de expiración de la caché en segundos (por defecto 1 hora)
        *args: Argumentos adicionales para la clave de caché
        **kwargs: Argumentos con nombre adicionales para la clave de caché
        
    Returns:
        function: Decorador de función
    """
    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            # Generar clave de caché incluyendo los argumentos de la función
            cache_args = list(args) + list(func_args)
            cache_kwargs = {**kwargs, **func_kwargs}
            cache_key = generate_cache_key(prefix, *cache_args, **cache_kwargs)
            
            # Intentar obtener el resultado de la caché
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Si no está en caché, ejecutar la función
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*func_args, **func_kwargs)
            
            # Almacenar el resultado en caché
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def optimize_query(queryset, select_related=None, prefetch_related=None, annotations=None, only=None):
    """
    Optimiza un queryset aplicando select_related, prefetch_related, 
    annotations y only según los parámetros proporcionados.
    
    Args:
        queryset: Queryset a optimizar
        select_related (list): Lista de campos para select_related
        prefetch_related (list/dict): Lista de campos o dict de Prefetch para prefetch_related
        annotations (dict): Diccionario de anotaciones a aplicar
        only (list): Lista de campos para only
        
    Returns:
        QuerySet: Queryset optimizado
    """
    # Aplicar select_related
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    # Aplicar prefetch_related
    if prefetch_related:
        if isinstance(prefetch_related, dict):
            prefetches = []
            for key, value in prefetch_related.items():
                if isinstance(value, dict):
                    prefetches.append(Prefetch(key, queryset=value['queryset'], to_attr=value.get('to_attr')))
                else:
                    prefetches.append(key)
            queryset = queryset.prefetch_related(*prefetches)
        else:
            queryset = queryset.prefetch_related(*prefetch_related)
    
    # Aplicar annotations
    if annotations:
        queryset = queryset.annotate(**annotations)
    
    # Aplicar only
    if only:
        queryset = queryset.only(*only)
    
    return queryset

def invalidate_cache_prefix(prefix):
    """
    Invalida todas las claves de caché que comienzan con el prefijo dado.
    
    Args:
        prefix (str): Prefijo de las claves a invalidar
    """
    pattern = f"ecuestre:{prefix}*"
    if hasattr(cache, 'delete_pattern'):
        # Algunos backends de caché (como redis_cache) tienen este método
        cache.delete_pattern(pattern)
    else:
        # Fallback para backends que no tienen delete_pattern
        logger.warning(f"Cache backend does not support delete_pattern: {pattern}")

# Optimizaciones para consultas comunes

def get_competencias_with_details(competencia_filter=None, categoria_filter=None):
    """
    Obtiene competencias con categorías, inscripciones y evaluaciones precargas eficientemente.
    
    Args:
        competencia_filter (dict): Filtros para el modelo Competencia
        categoria_filter (dict): Filtros para las categorías relacionadas
        
    Returns:
        QuerySet: Queryset de competencias optimizado
    """
    from competencias.models import Competencia, Categoria, Inscripcion
    from evaluaciones.models import Evaluacion
    
    # Crear querysets base
    inscripciones_queryset = Inscripcion.objects.select_related(
        'jinete__usuario', 
        'caballo'
    )
    
    if categoria_filter:
        categorias_queryset = Categoria.objects.filter(**categoria_filter)
    else:
        categorias_queryset = Categoria.objects.all()
    
    # Aplicar filtros a competencias
    if competencia_filter:
        competencias = Competencia.objects.filter(**competencia_filter)
    else:
        competencias = Competencia.objects.all()
    
    # Optimizar queryset principal
    competencias = competencias.prefetch_related(
        Prefetch('categorias', queryset=categorias_queryset),
        Prefetch(
            'inscripciones', 
            queryset=inscripciones_queryset
        )
    )
    
    return competencias

@cached_queryset('estadisticas_competencia', timeout=1800)
def get_estadisticas_competencia(competencia_id):
    """
    Obtiene estadísticas para una competencia específica con caché.
    
    Args:
        competencia_id: ID de la competencia
        
    Returns:
        dict: Diccionario con estadísticas
    """
    from competencias.models import Competencia, Categoria, Inscripcion
    from evaluaciones.models import Evaluacion
    from django.utils import timezone
    
    try:
        competencia = Competencia.objects.get(id=competencia_id)
    except Competencia.DoesNotExist:
        return {'error': 'Competencia no encontrada'}
    
    # Estadísticas por categoría
    categorias = Categoria.objects.filter(competencia=competencia).annotate(
        total_inscripciones=Count('inscripciones'),
        inscripciones_aprobadas=Count('inscripciones', filter=Q(inscripciones__estado='aprobada')),
        inscripciones_completadas=Count('inscripciones', filter=Q(inscripciones__estado='completada'))
    )
    
    categorias_stats = []
    for categoria in categorias:
        stats = {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'total_inscripciones': categoria.total_inscripciones,
            'inscripciones_aprobadas': categoria.inscripciones_aprobadas,
            'inscripciones_completadas': categoria.inscripciones_completadas,
            'plazas_disponibles': categoria.plazas_disponibles()
        }
        categorias_stats.append(stats)
    
    # Estadísticas generales con una sola consulta
    inscripciones_stats = Inscripcion.objects.filter(competencia=competencia).aggregate(
        total=Count('id'),
        jinetes_unicos=Count('jinete', distinct=True),
        caballos_unicos=Count('caballo', distinct=True)
    )
    
    # Evaluaciones
    evaluaciones_stats = Evaluacion.objects.filter(
        inscripcion__competencia=competencia
    ).aggregate(
        total=Count('id'),
        completas=Count('id', filter=Q(estado='completada')),
        pendientes=Count('id', filter=Q(estado='pendiente')),
        en_progreso=Count('id', filter=Q(estado='en_progreso')),
        puntaje_promedio=Avg('puntaje_total', filter=Q(puntaje_total__isnull=False)),
        puntaje_maximo=Max('puntaje_total'),
        puntaje_minimo=Min('puntaje_total')
    )
    
    # Días restantes o transcurridos
    today = timezone.now().date()
    if today < competencia.fecha_inicio:
        estado_tiempo = 'faltan'
        dias = (competencia.fecha_inicio - today).days
    elif today <= competencia.fecha_fin:
        estado_tiempo = 'transcurridos'
        dias = (today - competencia.fecha_inicio).days + 1
    else:
        estado_tiempo = 'finalizó hace'
        dias = (today - competencia.fecha_fin).days
    
    return {
        'id': competencia.id,
        'nombre': competencia.nombre,
        'estado': competencia.estado,
        'fecha_inicio': competencia.fecha_inicio,
        'fecha_fin': competencia.fecha_fin,
        'dias': dias,
        'estado_tiempo': estado_tiempo,
        'categorias': len(categorias_stats),
        'categorias_stats': categorias_stats,
        'inscripciones': inscripciones_stats,
        'evaluaciones': evaluaciones_stats,
    }

def get_inscripciones_jinete(jinete_id, annotate_evaluaciones=True):
    """
    Obtiene inscripciones de un jinete con información relacionada precargada.
    
    Args:
        jinete_id: ID del jinete
        annotate_evaluaciones: Si se deben incluir anotaciones de evaluaciones
        
    Returns:
        QuerySet: Queryset de inscripciones optimizado
    """
    from competencias.models import Inscripcion
    
    inscripciones = Inscripcion.objects.filter(jinete_id=jinete_id).select_related(
        'competencia',
        'categoria',
        'caballo'
    )
    
    if annotate_evaluaciones:
        inscripciones = inscripciones.annotate(
            total_evaluaciones=Count('evaluaciones'),
            evaluaciones_completas=Count('evaluaciones', filter=Q(evaluaciones__estado='completada')),
            puntaje_promedio=Avg('evaluaciones__puntaje_total', filter=Q(evaluaciones__estado='completada'))
        )
    
    return inscripciones

# Optimizaciones para el módulo de evaluaciones
def get_evaluaciones_juez(juez_id, competencia_id=None, categoria_id=None, estado=None):
    """
    Obtiene evaluaciones de un juez con información relacionada precargada eficientemente.
    
    Args:
        juez_id: ID del juez
        competencia_id: ID de la competencia (opcional)
        categoria_id: ID de la categoría (opcional)
        estado: Estado de la evaluación (opcional)
        
    Returns:
        QuerySet: Queryset de evaluaciones optimizado
    """
    from evaluaciones.models import Evaluacion
    
    filtros = {'juez_id': juez_id}
    
    if competencia_id:
        filtros['inscripcion__competencia_id'] = competencia_id
    
    if categoria_id:
        filtros['inscripcion__categoria_id'] = categoria_id
    
    if estado:
        filtros['estado'] = estado
    
    evaluaciones = Evaluacion.objects.filter(**filtros).select_related(
        'inscripcion__jinete__usuario',
        'inscripcion__caballo',
        'inscripcion__competencia',
        'inscripcion__categoria'
    ).prefetch_related(
        Prefetch(
            'puntuaciones',
            queryset=Puntuacion.objects.select_related('criterio')
        )
    )
    
    return evaluaciones

# Optimizaciones para el módulo de rankings
@cached_queryset('rankings_competencia', timeout=3600)
def get_rankings_competencia(competencia_id, categoria_id=None, tipo=None, publicado=True):
    """
    Obtiene rankings de una competencia con resultados precargados eficientemente.
    
    Args:
        competencia_id: ID de la competencia
        categoria_id: ID de la categoría (opcional)
        tipo: Tipo de ranking (opcional)
        publicado: Si solo se deben incluir rankings publicados (por defecto True)
        
    Returns:
        QuerySet: Queryset de rankings optimizado
    """
    from rankings.models import Ranking, ResultadoRanking
    
    filtros = {'competencia_id': competencia_id}
    
    if categoria_id:
        filtros['categoria_id'] = categoria_id
    
    if tipo:
        filtros['tipo'] = tipo
    
    if publicado is not None:
        filtros['publicado'] = publicado
    
    resultados_queryset = ResultadoRanking.objects.select_related(
        'inscripcion__jinete__usuario',
        'inscripcion__caballo'
    ).prefetch_related(
        'certificado'
    )
    
    rankings = Ranking.objects.filter(**filtros).select_related(
        'competencia',
        'categoria'
    ).prefetch_related(
        Prefetch('resultados', queryset=resultados_queryset)
    )
    
    return rankings

# Función para invalidar caché cuando se actualizan modelos relevantes
def invalidate_model_caches(sender, instance, **kwargs):
    """
    Invalida las cachés relacionadas cuando se actualiza un modelo.
    Se puede conectar a las señales post_save y post_delete de Django.
    
    Args:
        sender: Clase del modelo que envía la señal
        instance: Instancia del modelo que se está guardando/eliminando
        **kwargs: Argumentos adicionales
    """
    from django.apps import apps
    
    # Determinar qué cachés invalidar según el modelo
    if sender.__name__ == 'Competencia':
        invalidate_cache_prefix('competencias')
        invalidate_cache_prefix(f'estadisticas_competencia_{instance.id}')
    
    elif sender.__name__ == 'Categoria':
        invalidate_cache_prefix(f'estadisticas_competencia_{instance.competencia_id}')
    
    elif sender.__name__ == 'Inscripcion':
        invalidate_cache_prefix(f'estadisticas_competencia_{instance.competencia_id}')
        invalidate_cache_prefix(f'inscripciones_jinete_{instance.jinete_id}')
    
    elif sender.__name__ == 'Evaluacion':
        invalidate_cache_prefix(f'estadisticas_competencia_{instance.inscripcion.competencia_id}')
        invalidate_cache_prefix(f'evaluaciones_juez_{instance.juez_id}')
    
    elif sender.__name__ == 'Ranking':
        invalidate_cache_prefix(f'rankings_competencia_{instance.competencia_id}')
    
    elif sender.__name__ == 'ResultadoRanking':
        invalidate_cache_prefix(f'rankings_competencia_{instance.ranking.competencia_id}')