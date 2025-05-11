from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Prefetch

from .models import (
    EvaluationParameter, CompetitionParameter, Score, ScoreEdit, 
    Ranking, OfflineData
)
from .serializers import (
    EvaluationParameterSerializer, CompetitionParameterSerializer,
    ScoreSerializer, ScoreEditSerializer, RankingSerializer,
    JudgeScoreCardSerializer, ScoreCardResponseSerializer,
    ScoreSubmissionSerializer, OfflineDataSerializer
)
from .services import (
    calculate_parameter_score, update_participant_rankings, 
    calculate_judge_ranking, calculate_final_ranking
)
from .firebase import (
    sync_scores, sync_participant_scores, sync_rankings
)

from competitions.models import Competition, Participant
from competitions.serializers import ParticipantSerializer


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


class EvaluationParameterViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros de evaluación"""
    
    queryset = EvaluationParameter.objects.all()
    serializer_class = EvaluationParameterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrJudge]


class CompetitionParameterViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros en competencias"""
    
    queryset = CompetitionParameter.objects.all()
    serializer_class = CompetitionParameterSerializer
    permission_classes = [IsAuthenticated, IsAdminOrJudge]
    
    def get_queryset(self):
        queryset = CompetitionParameter.objects.all()
        
        # Filtrar por competencia
        competition_id = self.request.query_params.get('competition')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        return queryset


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet para calificaciones"""
    
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    
    def get_queryset(self):
        queryset = Score.objects.all()
        
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
        
        # Si el usuario no es admin, solo mostrar sus propias calificaciones
        if self.request.user.role != 'admin':
            queryset = queryset.filter(judge=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        # El save() ya calcula el resultado automáticamente
        score = serializer.save(judge=self.request.user)
        
        # Actualizar rankings
        update_participant_rankings(score.competition_id)
        
        # Sincronizar con Firebase
        sync_scores(score.id)
    
    def perform_update(self, serializer):
        # Guardar valores anteriores para auditoría
        instance = self.get_object()
        previous_value = instance.value
        previous_result = instance.calculated_result
        
        # Si hay cambio en el valor, registrar la edición
        new_value = serializer.validated_data.get('value')
        if new_value and new_value != previous_value:
            # Marcar como editado
            serializer.validated_data['is_edited'] = True
            
            # Crear registro de edición
            ScoreEdit.objects.create(
                score=instance,
                editor=self.request.user,
                previous_value=previous_value,
                previous_result=previous_result,
                edit_reason=serializer.validated_data.get('edit_reason', '')
            )
        
        # Guardar cambios
        score = serializer.save()
        
        # Actualizar rankings
        update_participant_rankings(score.competition_id)
        
        # Sincronizar con Firebase
        sync_scores(score.id)


class JudgeScoreCardView(APIView):
    """Vista para obtener y enviar tarjeta de calificación de un juez"""
    
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    
    def get(self, request, competition_id, participant_id):
        """Obtener tarjeta de calificación para un participante"""
        # Verificar que existan
        competition = get_object_or_404(Competition, pk=competition_id)
        participant = get_object_or_404(Participant, pk=participant_id, competition=competition)
        
        # Obtener parámetros de evaluación para esta competencia
        parameters = CompetitionParameter.objects.filter(
            competition=competition
        ).select_related('parameter').order_by('order')
        
        # Obtener calificaciones existentes para este juez
        scores = {}
        for judge_id in request.GET.getlist('judge_id', [self.request.user.id]):
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
                    'comments': score.comments
                }
        
        # Preparar datos de respuesta
        response_data = {
            'competition': competition.id,
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
            'scores': scores
        }
        
        return Response(response_data)
    
    @transaction.atomic
    def post(self, request, competition_id, participant_id):
        """Enviar calificaciones para un participante"""
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


class RankingListView(generics.ListAPIView):
    """Vista para listar rankings de una competencia"""
    
    serializer_class = RankingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        competition_id = self.kwargs.get('competition_id')
        return Ranking.objects.filter(
            competition_id=competition_id
        ).select_related(
            'participant', 'participant__rider', 'participant__horse'
        ).order_by('position')


class OfflineDataView(APIView):
    """Vista para sincronizar datos offline"""
    
    permission_classes = [IsAuthenticated, IsAssignedJudgeOrAdmin]
    
    def post(self, request):
        """Recibir datos guardados offline"""
        serializer = OfflineDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Guardar datos offline
        offline_data = serializer.save(judge=request.user)
        
        # Intentar sincronizar inmediatamente si la conexión lo permite
        try:
            data = offline_data.data
            competition_id = offline_data.competition_id
            participant_id = offline_data.participant_id
            
            # Procesar datos (calificaciones)
            if 'scores' in data:
                for param_id, score_data in data['scores'].items():
                    # Obtener parámetro
                    try:
                        parameter = CompetitionParameter.objects.get(
                            competition_id=competition_id,
                            parameter_id=param_id
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
                                'edit_reason': score_data.get('edit_reason', '')
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
            # Si falla, incrementar contador de intentos
            offline_data.sync_attempts += 1
            offline_data.save()
            
            return Response({
                'detail': f'Error al sincronizar: {str(e)}',
                'synced': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competition_parameters(request, competition_id):
    """Obtener parámetros de evaluación para una competencia"""
    competition = get_object_or_404(Competition, pk=competition_id)
    parameters = CompetitionParameter.objects.filter(
        competition=competition
    ).select_related('parameter').order_by('order')
    
    serializer = CompetitionParameterSerializer(parameters, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competition_rankings(request, competition_id):
    """Obtener rankings de una competencia"""
    competition = get_object_or_404(Competition, pk=competition_id)
    rankings = Ranking.objects.filter(
        competition=competition
    ).select_related(
        'participant', 'participant__rider', 'participant__horse'
    ).order_by('position')
    
    serializer = RankingSerializer(rankings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrJudge])
def recalculate_rankings(request, competition_id):
    """Recalcular rankings de una competencia"""
    try:
        rankings = update_participant_rankings(competition_id)
        sync_rankings(competition_id)
        
        return Response({
            'detail': 'Rankings recalculados correctamente',
            'count': len(rankings)
        })
    except Exception as e:
        return Response({
            'detail': f'Error al recalcular rankings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)