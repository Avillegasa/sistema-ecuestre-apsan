# backend/competencias/validators.py

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def validate_inscripcion_abierta(competencia):
    """
    Valida que la competencia tenga inscripciones abiertas.
    
    Args:
        competencia: Instancia del modelo Competencia
        
    Raises:
        ValidationError: Si las inscripciones no están abiertas
    """
    today = timezone.now().date()
    
    if competencia.estado != 'inscripciones_abiertas':
        raise ValidationError(
            _('Las inscripciones no están abiertas para esta competencia.')
        )
    
    if today < competencia.fecha_inicio_inscripciones:
        raise ValidationError(
            _('Las inscripciones para esta competencia aún no han comenzado.')
        )
    
    if today > competencia.fecha_fin_inscripciones:
        raise ValidationError(
            _('El período de inscripciones para esta competencia ha finalizado.')
        )

def validate_inscripcion_jinete_categoria(jinete, categoria):
    """
    Valida que el jinete cumpla con los requisitos de edad para la categoría.
    
    Args:
        jinete: Instancia del modelo Jinete
        categoria: Instancia del modelo Categoria
        
    Raises:
        ValidationError: Si el jinete no cumple con los requisitos
    """
    # Solo validar si el jinete tiene fecha de nacimiento registrada y la categoría tiene restricciones
    if jinete.usuario.fecha_nacimiento and (categoria.edad_minima > 0 or categoria.edad_maxima < 99):
        today = timezone.now().date()
        edad = today.year - jinete.usuario.fecha_nacimiento.year
        
        # Ajustar la edad si aún no ha cumplido años este año
        if today.month < jinete.usuario.fecha_nacimiento.month or (
                today.month == jinete.usuario.fecha_nacimiento.month and 
                today.day < jinete.usuario.fecha_nacimiento.day
            ):
            edad -= 1
            
        if edad < categoria.edad_minima:
            raise ValidationError(
                _('El jinete no cumple con la edad mínima para esta categoría.')
            )
            
        if edad > categoria.edad_maxima:
            raise ValidationError(
                _('El jinete excede la edad máxima para esta categoría.')
            )

def validate_caballo_jinete(caballo, jinete):
    """
    Valida que el caballo pertenezca al jinete.
    
    Args:
        caballo: Instancia del modelo Caballo
        jinete: Instancia del modelo Jinete
        
    Raises:
        ValidationError: Si el caballo no pertenece al jinete
    """
    if caballo.jinete != jinete:
        raise ValidationError(
            _('El caballo seleccionado no pertenece a este jinete.')
        )

def validate_jinete_multiple_inscripcion(jinete, competencia, categoria):
    """
    Valida que un jinete no se inscriba múltiples veces en la misma categoría
    con diferentes caballos, si las reglas de la competencia no lo permiten.
    
    Args:
        jinete: Instancia del modelo Jinete
        competencia: Instancia del modelo Competencia
        categoria: Instancia del modelo Categoria
        
    Raises:
        ValidationError: Si el jinete ya está inscrito en esta categoría
    """
    from .models import Inscripcion
    
    # Esta validación depende de las reglas específicas de cada competencia
    # Por ahora, asumimos que no se permite que un jinete se inscriba más de una vez
    # en la misma categoría
    
    # Buscar inscripciones activas del jinete en esta categoría
    inscripciones_existentes = Inscripcion.objects.filter(
        jinete=jinete,
        competencia=competencia,
        categoria=categoria,
        estado__in=['pendiente', 'aprobada', 'completada']
    ).exists()
    
    if inscripciones_existentes:
        raise ValidationError(
            _('El jinete ya está inscrito en esta categoría.')
        )