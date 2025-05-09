# backend/competencias/utils.py

from django.db.models import Avg, Count, Sum, F, Q, Prefetch
from django.utils import timezone
from datetime import timedelta

def get_competencias_activas():
    """
    Obtiene competencias activas optimizando consultas con select_related y prefetch_related.
    """
    from .models import Competencia
    
    today = timezone.now().date()
    competencias = Competencia.objects.filter(
        Q(estado='en_curso') | 
        (Q(estado='inscripciones_abiertas') & 
         Q(fecha_inicio_inscripciones__lte=today) & 
         Q(fecha_fin_inscripciones__gte=today))
    ).select_related().prefetch_related(
        'categorias',
        Prefetch(
            'inscripciones',
            queryset=Inscripcion.objects.select_related('jinete__usuario', 'caballo')
        )
    )
    
    return competencias

def verificar_cupo_categoria(categoria):
    """
    Verifica si hay cupo disponible en una categoría.
    
    Args:
        categoria: Instancia del modelo Categoria
        
    Returns:
        bool: True si hay cupo disponible, False en caso contrario
    """
    if categoria.cupo_maximo == 0:  # Cupo ilimitado
        return True
        
    inscritos = categoria.inscripciones.filter(
        estado__in=['pendiente', 'aprobada', 'completada']
    ).count()
    
    return inscritos < categoria.cupo_maximo

def get_estadisticas_competencia(competencia_id):
    """
    Obtiene estadísticas para una competencia específica.
    
    Args:
        competencia_id: ID de la competencia
        
    Returns:
        dict: Diccionario con estadísticas
    """
    from .models import Competencia, Inscripcion
    
    try:
        competencia = Competencia.objects.get(id=competencia_id)
    except Competencia.DoesNotExist:
        return {'error': 'Competencia no encontrada'}
    
    # Estadísticas por categoría
    categorias_stats = []
    for categoria in competencia.categorias.all():
        inscripciones = categoria.inscripciones.all()
        stats = {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'total_inscripciones': inscripciones.count(),
            'inscripciones_aprobadas': inscripciones.filter(estado='aprobada').count(),
            'inscripciones_completadas': inscripciones.filter(estado='completada').count(),
            'plazas_disponibles': categoria.plazas_disponibles()
        }
        categorias_stats.append(stats)
    
    # Estadísticas generales
    inscripciones_totales = Inscripcion.objects.filter(competencia=competencia).count()
    jinetes_unicos = Inscripcion.objects.filter(competencia=competencia).values('jinete').distinct().count()
    caballos_unicos = Inscripcion.objects.filter(competencia=competencia).values('caballo').distinct().count()
    
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
        'inscripciones_totales': inscripciones_totales,
        'jinetes_unicos': jinetes_unicos,
        'caballos_unicos': caballos_unicos
    }