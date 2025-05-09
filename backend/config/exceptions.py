# backend/config/exceptions.py

from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class BaseEcuestreException(APIException):
    """
    Excepción base para todas las excepciones personalizadas del sistema ecuestre.
    Extiende la clase APIException de Django Rest Framework.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('Ha ocurrido un error inesperado.')
    default_code = 'error'
    
    def __init__(self, detail=None, code=None):
        """
        Inicializa la excepción con detalles y código personalizados si se proporcionan.
        """
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
            
        super().__init__(detail, code)


# Excepciones de Permisos

class PermisoDenegadoException(BaseEcuestreException):
    """Excepción para permisos denegados."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('No tienes permisos para realizar esta acción.')
    default_code = 'permiso_denegado'


# Excepciones de Competencias

class CompetenciaNoEncontradaException(BaseEcuestreException):
    """Excepción para cuando no se encuentra una competencia."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('La competencia solicitada no existe.')
    default_code = 'competencia_no_encontrada'


class InscripcionesNoAbiertasException(BaseEcuestreException):
    """Excepción para cuando las inscripciones no están abiertas."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Las inscripciones no están abiertas para esta competencia.')
    default_code = 'inscripciones_no_abiertas'


class CupoCompletoException(BaseEcuestreException):
    """Excepción para cuando no hay cupo disponible en una categoría."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('No hay cupos disponibles en esta categoría.')
    default_code = 'cupo_completo'


class InscripcionDuplicadaException(BaseEcuestreException):
    """Excepción para cuando ya existe una inscripción."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Ya existe una inscripción para este jinete/caballo en esta categoría.')
    default_code = 'inscripcion_duplicada'


class JineteNoCumpleRequisitosCategoriaException(BaseEcuestreException):
    """Excepción para cuando un jinete no cumple con requisitos de edad de una categoría."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('El jinete no cumple con los requisitos de edad para esta categoría.')
    default_code = 'jinete_no_cumple_requisitos'


class CaballoNoPerteneciente(BaseEcuestreException):
    """Excepción para cuando un caballo no pertenece al jinete."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('El caballo seleccionado no pertenece a este jinete.')
    default_code = 'caballo_no_perteneciente'


# Excepciones de Evaluaciones

class EvaluacionNoEncontradaException(BaseEcuestreException):
    """Excepción para cuando no se encuentra una evaluación."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('La evaluación solicitada no existe.')
    default_code = 'evaluacion_no_encontrada'


class EvaluacionNoAsignadaException(BaseEcuestreException):
    """Excepción para cuando un juez intenta evaluar una inscripción que no le fue asignada."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('No tienes asignada esta evaluación.')
    default_code = 'evaluacion_no_asignada'


class EvaluacionYaCompletaException(BaseEcuestreException):
    """Excepción para cuando se intenta modificar una evaluación ya completada."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Esta evaluación ya está completada y no puede ser modificada.')
    default_code = 'evaluacion_ya_completa'


class CriteriosFaltantesException(BaseEcuestreException):
    """Excepción para cuando faltan criterios por evaluar."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Faltan criterios por evaluar para finalizar la evaluación.')
    default_code = 'criterios_faltantes'


class PuntuacionExcedeLimiteException(BaseEcuestreException):
    """Excepción para cuando una puntuación excede el límite permitido."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('La puntuación excede el máximo permitido para este criterio.')
    default_code = 'puntuacion_excede_limite'


# Excepciones de Rankings

class RankingNoEncontradoException(BaseEcuestreException):
    """Excepción para cuando no se encuentra un ranking."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('El ranking solicitado no existe.')
    default_code = 'ranking_no_encontrado'


class RankingYaPublicadoException(BaseEcuestreException):
    """Excepción para cuando se intenta modificar un ranking ya publicado."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Este ranking ya está publicado y no puede ser modificado.')
    default_code = 'ranking_ya_publicado'


class NoHayEvaluacionesCompletasException(BaseEcuestreException):
    """Excepción para cuando no hay evaluaciones completas para generar un ranking."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('No hay evaluaciones completas suficientes para generar el ranking.')
    default_code = 'no_hay_evaluaciones_completas'


class CertificadoNoEncontradoException(BaseEcuestreException):
    """Excepción para cuando no se encuentra un certificado."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('El certificado solicitado no existe.')
    default_code = 'certificado_no_encontrado'


class CertificadoYaExistenteException(BaseEcuestreException):
    """Excepción para cuando ya existe un certificado para un resultado."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Ya existe un certificado para este resultado.')
    default_code = 'certificado_ya_existente'


# Función para manejar excepciones Django a excepciones personalizadas
def handle_exception(exc, context):
    """
    Convierte excepciones de Django/DRF a excepciones personalizadas cuando es posible.
    """
    from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
    from rest_framework.views import exception_handler
    from competencias.models import Competencia, Inscripcion
    from evaluaciones.models import Evaluacion
    from rankings.models import Ranking, Certificado
    
    # Manejar excepciones personalizadas
    if isinstance(exc, BaseEcuestreException):
        return exception_handler(exc, context)
    
    # Convertir excepciones comunes de Django a excepciones personalizadas
    if isinstance(exc, ObjectDoesNotExist):
        # Determinar qué tipo de objeto no se encontró
        if 'Competencia' in str(exc):
            exc = CompetenciaNoEncontradaException()
        elif 'Evaluacion' in str(exc):
            exc = EvaluacionNoEncontradaException()
        elif 'Ranking' in str(exc):
            exc = RankingNoEncontradoException()
        elif 'Certificado' in str(exc):
            exc = CertificadoNoEncontradoException()
    
    elif isinstance(exc, PermissionDenied):
        exc = PermisoDenegadoException()
    
    elif isinstance(exc, ValidationError):
        # Convertir error de validación a excepción personalizada según el contexto
        view = context.get('view')
        if view:
            basename = getattr(view, 'basename', '')
            if 'evaluacion' in basename.lower():
                if 'puntuacion' in str(exc).lower() and 'max' in str(exc).lower():
                    exc = PuntuacionExcedeLimiteException(detail=str(exc))
            
    # Usar el manejador de excepciones por defecto de DRF
    return exception_handler(exc, context)