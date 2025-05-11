"""
Vistas mejoradas para la API de calificación y rankings del Sistema Ecuestre APSAN.
Implementa el sistema FEI de 3 celdas con soporte para evaluación en tiempo real.
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Prefetch, Q, Count, Avg
import logging

# Importaciones de modelos
from .models import (
    EvaluationParameter, CompetitionParameter, Score, ScoreEdit, 
    Ranking, FirebaseSync, OfflineData
)

# Importaciones de serializadores
from .serializers import (
    EvaluationParameterSerializer, CompetitionParameterSerializer,
    ScoreSerializer, ScoreEditSerializer, RankingSerializer,
    JudgeScoreCardSerializer, ScoreCardResponseSerializer,
    ScoreSubmissionSerializer, OfflineDataSerializer
)

# Importaciones de servicios
from .services import (
    calculate_parameter_score, update_participant_rankings, 
    calculate_judge_ranking, calculate_final_ranking,
    calculate_judge_scoring_statistics, compare_judge_scores
)

# Importaciones de integración con Firebase
from .firebase import (
    sync_scores, sync_participant_scores, sync_rankings
)

from competitions.models import Competition, Participant
from competitions.serializers import ParticipantSerializer

logger = logging.getLogger(__name__)

class IsAdminOrJudge(permissions.BasePermission):
    """Permiso para permitir solo a los administradores y jueces"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_judge
        )


class IsAssignedJudgeOrAdmin(permissions.BasePermission):
    """Permiso para permitir solo a los jueces asignados a la competencia y administradores"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'admin':
            return True
        
        competition_id = view.kwargs.get('competition_id')
        if not competition_id:
            return False
        
        # Verificar si el usuario es juez asignado a la competencia
        from competitions.models import CompetitionJudge
        is_assigned = CompetitionJudge.objects.filter(
            competition_id=competition_id,
            judge=request.user
        ).exists()
        
        return request.user.is_judge and is_assigned


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para resultados"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EvaluationParameterViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros de evaluación FEI"""
    
    queryset = EvaluationParameter.objects.all()
    serializer_class = EvaluationParameterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrJudge]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'coefficient', 'max_value', 'created_at']
    ordering = ['name']


class CompetitionParameterViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros en competencias"""
    
    queryset = CompetitionParameter.objects.all()
    serializer_class = CompetitionParameterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrJudge]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'parameter__name']
    ordering = ['order']
    
    def get_queryset(self):
        queryset = CompetitionParameter.objects.all().select_related('parameter', 'competition')
        
        # Filtrar por competencia
        competition_id = self.request.query_params.get('competition')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Crear múltiples parámetros para una competencia en una sola operación"""
        competition_id = request.data.get('competition_id')
        parameters = request.data.get('parameters')
        
        if not competition_id or not parameters:
            return Response(
                {"detail": "Se requiere competition_id y una lista de parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            return Response(
                {"detail": f"Competencia con ID {competition_id} no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_parameters = []
        with transaction.atomic():
            for index, param_data in enumerate(parameters):
                param_id = param_data.get('parameter_id')
                
                try:
                    parameter = EvaluationParameter.objects.get(id=param_id)
                except EvaluationParameter.DoesNotExist:
                    return Response(
                        {"detail": f"Parámetro con ID {param_id} no encontrado"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Crear o actualizar el parámetro de competencia
                competition_param, created = CompetitionParameter.objects.update_or_create(
                    competition=competition,
                    parameter=parameter,
                    defaults={
                        'order': param_data.get('order', index + 1),
                        'custom_coefficient': param_data.get('custom_coefficient'),
                        'custom_max_value': param_data.get('custom_max_value')
                    }
                )
                
                created_parameters.append(competition_param)
        
        serializer = CompetitionParameterSerializer(created_parameters, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet para calificaciones"""
    
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'value']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        queryset = Score.objects.all().select_related(
            'judge', 'participant', 'competition', 'parameter', 'parameter__parameter'
        )
        
        # Filtrar por competencia
        competition_id = self.request.query_params.get('competition')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        # Filtrar por participante
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(participant_id=participant_id)
        
        # Filtrar por juez
        judge_id = self.request.query_params.get('judge')
        if judge_id:
            queryset = queryset.filter(judge_id=judge_id)
        
        # Filtrar por parámetro
        parameter_id = self.request.query_params.get('parameter')
        if parameter_id:
            queryset = queryset.filter(parameter__parameter_id=parameter_id)
        
        # Filtrar solo puntuaciones editadas
        edited = self.request.query_params.get('edited')
        if edited is not None:
            queryset = queryset.filter(is_edited=(edited.lower() == 'true'))
        
        # Si el usuario no es admin, solo mostrar sus propias calificaciones
        if self.request.user.role != 'admin':
            queryset = queryset.filter(judge=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        try:
            # El save() ya calcula el resultado automáticamente
            score = serializer.save(judge=self.request.user)
            
            # Actualizar rankings
            update_participant_rankings(score.competition_id)
            
            # Sincronizar con Firebase
            sync_scores(score.id)
        except Exception as e:
            logger.error(f"Error al crear calificación: {e}")
            raise
    
    def perform_update(self, serializer):
        try:
            # Guardar valores anteriores para auditoría
            instance = self.get_object()
            previous_value = instance.value
            previous_result = instance.calculated_result
            
            # Si hay cambio en el valor, registrar la edición
            new_value = serializer.validated_data.get('value')
            if new_value is not None and new_value != previous_value:
                # Marcar como editado
                serializer.validated_data['is_edited'] = True
                
                # Crear registro de edición
                ScoreEdit.objects.create(
                    score=instance,
                    editor=self.request.user,
                    previous_value=previous_value,
                    previous_result=previous_result,
                    edit_reason=serializer.validated_data.get('edit_reason', 'Edición manual')
                )
            
            # Guardar cambios
            score = serializer.save()
            
            # Actualizar rankings
            update_participant_rankings(score.competition_id)
            
            # Sincronizar con Firebase
            sync_scores(score.id)
        except Exception as e:
            logger.error(f"Error al actualizar calificación: {e}")
            raise

    @action(detail=False, methods=['post'], url_path='bulk-submit')
    def bulk_submit(self, request):
        """Enviar múltiples calificaciones en una sola operación"""
        competition_id = request.data.get('competition_id')
        participant_id = request.data.get('participant_id')
        scores_data = request.data.get('scores')
        edit_reason = request.data.get('edit_reason', '')
        
        if not all([competition_id, participant_id, scores_data]):
            return Response(
                {"detail": "Se requiere competition_id, participant_id y una lista de scores"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            competition = Competition.objects.get(id=competition_id)
            participant = Participant.objects.get(id=participant_id, competition=competition)
        except (Competition.DoesNotExist, Participant.DoesNotExist):
            return Response(
                {"detail": "Competencia o participante no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        if self.request.user.role != 'admin':
            from competitions.models import CompetitionJudge
            is_assigned = CompetitionJudge.objects.filter(
                competition=competition,
                judge=self.request.user
            ).exists()
            
            if not is_assigned:
                return Response(
                    {"detail": "No está asignado como juez a esta competencia"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        created_scores = []
        with transaction.atomic():
            for score_data in scores_data:
                parameter_id = score_data.get('parameter_id')
                value = score_data.get('value')
                comments = score_data.get('comments', '')
                
                if not all([parameter_id, value is not None]):
                    continue
                
                try:
                    parameter = CompetitionParameter.objects.get(
                        competition=competition,
                        parameter_id=parameter_id
                    )
                except CompetitionParameter.DoesNotExist:
                    continue
                
                # Verificar si ya existe una calificación
                try:
                    score = Score.objects.get(
                        competition=competition,
                        participant=participant,
                        judge=self.request.user,
                        parameter=parameter
                    )
                    
                    # Si hay cambio en el valor, registrar la edición
                    if float(score.value) != float(value):
                        previous_value = score.value
                        previous_result = score.calculated_result
                        
                        # Actualizar
                        score.value = value
                        score.comments = comments
                        score.is_edited = True
                        score.edit_reason = edit_reason
                        score.save()
                        
                        # Crear registro de edición
                        ScoreEdit.objects.create(
                            score=score,
                            editor=self.request.user,
                            previous_value=previous_value,
                            previous_result=previous_result,
                            edit_reason=edit_reason
                        )
                    else:
                        # Solo actualizar comentarios
                        score.comments = comments
                        score.save()
                except Score.DoesNotExist:
                    # Crear nueva calificación
                    score = Score.objects.create(
                        competition=competition,
                        participant=participant,
                        judge=self.request.user,
                        parameter=parameter,
                        value=value,
                        comments=comments
                    )
                
                created_scores.append(score)
            
            # Actualizar rankings
            update_participant_rankings(competition.id)
            
            # Sincronizar con Firebase
            sync_participant_scores(competition.id, participant.id, self.request.user.id)
        
        serializer = ScoreSerializer(created_scores, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JudgeScoreCardView(APIView):
    """Vista para obtener y enviar tarjeta de calificación de un juez"""
    
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    
    def get(self, request, competition_id, participant_id):
        """Obtener tarjeta de calificación para un participante"""
        try:
            # Verificar que existan
            competition = get_object_or_404(Competition, pk=competition_id)
            participant = get_object_or_404(Participant, pk=participant_id, competition=competition)
            
            # Obtener parámetros de evaluación para esta competencia
            parameters = CompetitionParameter.objects.filter(
                competition=competition
            ).select_related('parameter').order_by('order')
            
            # Obtener calificaciones existentes para este juez o los jueces solicitados
            scores = {}
            judge_ids = request.GET.getlist('judge_id', [self.request.user.id])
            
            for judge_id in judge_ids:
                judge_scores = Score.objects.filter(
                    competition=competition,
                    participant=participant,
                    judge_id=judge_id
                ).select_related('parameter', 'parameter__parameter')
                
                # Organizar por parámetro
                scores[str(judge_id)] = {}
                for score in judge_scores:
                    scores[str(judge_id)][str(score.parameter.parameter.id)] = {
                        'value': float(score.value),
                        'calculated_result': float(score.calculated_result),
                        'comments': score.comments,
                        'updated_at': score.updated_at.isoformat() if score.updated_at else None,
                        'is_edited': score.is_edited
                    }
            
            # Preparar datos de respuesta
            response_data = {
                'competition': competition.id,
                'competition_name': competition.name,
                'participant': ParticipantSerializer(participant).data,
                'parameters': [
                    {
                        'id': param.parameter.id,
                        'name': param.parameter.name,
                        'description': param.parameter.description,
                        'coefficient': param.effective_coefficient,
                        'max_value': param.effective_max_value,
                        'order': param.order
                    } for param in parameters
                ],
                'scores': scores,
                'last_updated': competition.updated_at.isoformat() if competition.updated_at else None
            }
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error al obtener tarjeta de calificación: {e}")
            return Response(
                {"detail": f"Error al obtener tarjeta de calificación: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def post(self, request, competition_id, participant_id):
        """Enviar calificaciones para un participante"""
        try:
            # Verificar que existan
            competition = get_object_or_404(Competition, pk=competition_id)
            participant = get_object_or_404(Participant, pk=participant_id, competition=competition)
            
            # Validar datos
            serializer = JudgeScoreCardSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Procesar cada calificación
            scores_data = serializer.validated_data['scores']
            edit_reason = serializer.validated_data.get('edit_reason', '')
            
            created_scores = []
            for score_data in scores_data:
                parameter_id = score_data['parameter_id']
                value = score_data['value']
                comments = score_data.get('comments', '')
                
                # Obtener parámetro de competencia
                parameter = get_object_or_404(
                    CompetitionParameter, 
                    competition=competition, 
                    parameter_id=parameter_id
                )
                
                # Verificar si ya existe una calificación
                try:
                    score = Score.objects.get(
                        competition=competition,
                        participant=participant,
                        judge=request.user,
                        parameter=parameter
                    )
                    
                    # Si hay cambio en el valor, registrar la edición
                    if score.value != value:
                        # Guardar valores anteriores
                        previous_value = score.value
                        previous_result = score.calculated_result
                        
                        # Actualizar
                        score.value = value
                        score.comments = comments
                        score.is_edited = True
                        score.edit_reason = edit_reason
                        score.save()
                        
                        # Crear registro de edición
                        ScoreEdit.objects.create(
                            score=score,
                            editor=request.user,
                            previous_value=previous_value,
                            previous_result=previous_result,
                            edit_reason=edit_reason
                        )
                    else:
                        # Solo actualizar comentarios
                        score.comments = comments
                        score.save()
                        
                except Score.DoesNotExist:
                    # Crear nueva calificación
                    score = Score.objects.create(
                        competition=competition,
                        participant=participant,
                        judge=request.user,
                        parameter=parameter,
                        value=value,
                        comments=comments
                    )
                    
                created_scores.append(score)
            
            # Actualizar rankings
            update_participant_rankings(competition.id)
            
            # Sincronizar con Firebase
            sync_participant_scores(competition.id, participant.id, request.user.id)
            
            return Response({
                'detail': 'Calificaciones guardadas correctamente',
                'scores': ScoreSerializer(created_scores, many=True).data
            })
        except Exception as e:
            logger.error(f"Error al enviar calificaciones: {e}")
            return Response(
                {"detail": f"Error al enviar calificaciones: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RankingListView(generics.ListAPIView):
    """Vista para listar rankings de una competencia"""
    
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['position', 'percentage', 'average_score']
    ordering = ['position']
    
    def get_queryset(self):
        competition_id = self.kwargs.get('competition_id')
        return Ranking.objects.filter(
            competition_id=competition_id
        ).select_related(
            'participant', 'participant__rider', 'participant__horse', 'participant__category'
        ).order_by('position')


class RankingDetailView(generics.RetrieveAPIView):
    """Vista para obtener detalle de un ranking específico"""
    
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        competition_id = self.kwargs.get('competition_id')
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(
            Ranking, 
            competition_id=competition_id, 
            participant_id=participant_id
        )


class OfflineDataView(APIView):
    """Vista para sincronizar datos offline"""
    
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    
    def post(self, request):
        """Recibir datos guardados offline"""
        try:
            serializer = OfflineDataSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Guardar datos offline
            offline_data = serializer.save(judge=request.user)
            
            # Intentar sincronizar inmediatamente si la conexión lo permite
            data = offline_data.data
            competition_id = offline_data.competition_id
            participant_id = offline_data.participant_id
            
            # Procesar datos (calificaciones)
            if 'scores' in data:
                with transaction.atomic():
                    for param_id, score_data in data['scores'].items():
                        # Obtener parámetro
                        try:
                            parameter = CompetitionParameter.objects.get(
                                competition_id=competition_id,
                                parameter__id=param_id
                            )
                            
                            # Crear o actualizar calificación
                            Score.objects.update_or_create(
                                competition_id=competition_id,
                                participant_id=participant_id,
                                judge=request.user,
                                parameter=parameter,
                                defaults={
                                    'value': score_data.get('value'),
                                    'comments': score_data.get('comments', ''),
                                    'is_edited': score_data.get('is_edited', False),
                                    'edit_reason': score_data.get('edit_reason', 'Sincronización offline')
                                }
                            )
                        except CompetitionParameter.DoesNotExist:
                            continue
                    
                    # Actualizar rankings
                    update_participant_rankings(competition_id)
                    
                    # Sincronizar con Firebase
                    sync_participant_scores(competition_id, participant_id, request.user.id)
                    
                    # Marcar como sincronizado
                    offline_data.is_synced = True
                    offline_data.save()
                    
                    return Response({
                        'detail': 'Datos sincronizados correctamente',
                        'synced': True
                    })
            
            return Response({
                'detail': 'No hay datos para sincronizar',
                'synced': False
            })
            
        except Exception as e:
            logger.error(f"Error al sincronizar datos offline: {e}")
            
            # Si falla, incrementar contador de intentos si existe el objeto
            if 'offline_data' in locals():
                offline_data.sync_attempts += 1
                offline_data.save()
            
            return Response({
                'detail': f'Error al sincronizar: {str(e)}',
                'synced': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OfflineDataSyncListView(generics.ListCreateAPIView):
    """Vista para listar y crear datos pendientes de sincronización"""
    
    serializer_class = OfflineDataSerializer
    permission_classes = [IsAuthenticated, IsAdminOrJudge]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = OfflineData.objects.all()
        
        # Si no es admin, solo ver sus datos
        if self.request.user.role != 'admin':
            queryset = queryset.filter(judge=self.request.user)
        
        # Filtrar por estado de sincronización
        synced = self.request.query_params.get('synced')
        if synced is not None:
            queryset = queryset.filter(is_synced=(synced.lower() == 'true'))
        
        # Filtrar por competencia
        competition_id = self.request.query_params.get('competition')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        return queryset.select_related('judge', 'competition', 'participant')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competition_parameters(request, competition_id):
    """Obtener parámetros de evaluación para una competencia"""
    try:
        competition = get_object_or_404(Competition, pk=competition_id)
        parameters = CompetitionParameter.objects.filter(
            competition=competition
        ).select_related('parameter').order_by('order')
        
        serializer = CompetitionParameterSerializer(parameters, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error al obtener parámetros de competencia: {e}")
        return Response(
            {"detail": f"Error al obtener parámetros: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competition_rankings(request, competition_id):
    """Obtener rankings de una competencia"""
    try:
        competition = get_object_or_404(Competition, pk=competition_id)
        rankings = Ranking.objects.filter(
            competition=competition
        ).select_related(
            'participant', 'participant__rider', 'participant__horse'
        ).order_by('position')
        
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error al obtener rankings de competencia: {e}")
        return Response(
            {"detail": f"Error al obtener rankings: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrJudge])
def recalculate_rankings(request, competition_id):
    """Recalcular rankings de una competencia"""
    try:
        rankings = update_participant_rankings(competition_id, recalculate_all=True)
        sync_rankings(competition_id)
        
        return Response({
            'detail': 'Rankings recalculados correctamente',
            'count': len(rankings)
        })
    except Exception as e:
        logger.error(f"Error al recalcular rankings: {e}")
        return Response({
            'detail': f'Error al recalcular rankings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrJudge])
def judge_statistics(request, judge_id=None):
    """Obtener estadísticas de calificación de un juez"""
    try:
        # Si no se especifica juez, usar el usuario actual
        if not judge_id and request.user.is_judge:
            judge_id = request.user.id
        elif not judge_id and not request.user.is_judge:
            return Response(
                {"detail": "Debe especificar un ID de juez"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener parámetros de consulta
        competition_id = request.query_params.get('competition')
        
        # Calcular estadísticas
        stats = calculate_judge_scoring_statistics(judge_id, competition_id)
        
        return Response(stats)
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de juez: {e}")
        return Response({
            'detail': f'Error al obtener estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrJudge])
def compare_judges(request, competition_id, participant_id):
    """Comparar calificaciones entre jueces para un participante"""
    try:
        comparison = compare_judge_scores(competition_id, participant_id)
        return Response(comparison)
    except Exception as e:
        logger.error(f"Error al comparar jueces: {e}")
        return Response({
            'detail': f'Error al comparar jueces: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_status(request, competition_id):
    """Obtener estado de sincronización con Firebase"""
    try:
        sync_record = FirebaseSync.objects.filter(competition_id=competition_id).first()
        
        if not sync_record:
            return Response({
                'competition_id': competition_id,
                'is_synced': False,
                'last_sync': None,
                'error_message': None
            })
        
        return Response({
            'competition_id': competition_id,
            'is_synced': sync_record.is_synced,
            'last_sync': sync_record.last_sync.isoformat() if sync_record.last_sync else None,
            'error_message': sync_record.error_message
        })
    except Exception as e:
        logger.error(f"Error al obtener estado de sincronización: {e}")
        return Response({
            'detail': f'Error al obtener estado de sincronización: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrJudge])
def force_sync(request, competition_id):
    """Forzar sincronización con Firebase"""
    try:
        # Recalcular rankings
        rankings = update_participant_rankings(competition_id, recalculate_all=True)
        
        # Sincronizar con Firebase
        sync_success = sync_rankings(competition_id)
        
        # Actualizar registro de sincronización
        FirebaseSync.objects.update_or_create(
            competition_id=competition_id,
            defaults={
                'is_synced': sync_success,
                'error_message': None if sync_success else 'Falló la sincronización'
            }
        )
        
        return Response({
            'detail': 'Sincronización forzada completada',
            'success': sync_success,
            'rankings_count': len(rankings)
        })
    except Exception as e:
        logger.error(f"Error al forzar sincronización: {e}")
        
        # Registrar error
        FirebaseSync.objects.update_or_create(
            competition_id=competition_id,
            defaults={
                'is_synced': False,
                'error_message': str(e)
            }
        )
        
        return Response({
            'detail': f'Error al forzar sincronización: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)