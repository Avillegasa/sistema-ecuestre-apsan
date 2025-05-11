from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction

from .models import (
    Competition, Category, CompetitionCategory, 
    CompetitionJudge, Rider, Horse, Participant
)
from .serializers import (
    CompetitionListSerializer, CompetitionDetailSerializer, CompetitionCreateSerializer,
    CategorySerializer, CompetitionCategorySerializer, CompetitionJudgeSerializer,
    RiderSerializer, HorseSerializer, ParticipantSerializer,
    ParticipantAssignmentSerializer
)

from users.models import User


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permiso para permitir solo a los administradores realizar escritura"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrJudge(permissions.BasePermission):
    """Permiso para permitir solo a los administradores y jueces"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_judge
        )


class CompetitionViewSet(viewsets.ModelViewSet):
    """ViewSet para competencias"""
    
    queryset = Competition.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompetitionListSerializer
        elif self.action == 'create':
            return CompetitionCreateSerializer
        return CompetitionDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    def get_queryset(self):
        queryset = Competition.objects.all()
        
        # Filtrar por estado si se especifica
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Si no es admin, solo ver competencias públicas o creadas por el usuario
        if self.request.user.role != 'admin':
            queryset = queryset.filter(
                is_public=True
            ) | queryset.filter(
                creator=self.request.user
            )
            
            # Si es juez, también ver competencias donde es juez
            if self.request.user.is_judge:
                judge_competitions = CompetitionJudge.objects.filter(
                    judge=self.request.user
                ).values_list('competition_id', flat=True)
                
                queryset = queryset | Competition.objects.filter(id__in=judge_competitions)
        
        return queryset.distinct()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def assign_judges(self, request, pk=None):
        """Asignar jueces a una competencia"""
        competition = self.get_object()
        
        # Validar datos
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Se esperaba una lista de jueces"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Eliminar asignaciones existentes
            CompetitionJudge.objects.filter(competition=competition).delete()
            
            # Crear nuevas asignaciones
            for judge_data in request.data:
                judge_id = judge_data.get('judge_id')
                is_head = judge_data.get('is_head_judge', False)
                
                try:
                    judge = User.objects.get(pk=judge_id, is_judge=True)
                except User.DoesNotExist:
                    return Response(
                        {"detail": f"Juez con ID {judge_id} no encontrado"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                CompetitionJudge.objects.create(
                    competition=competition,
                    judge=judge,
                    is_head_judge=is_head
                )
        
        # Devolver competencia actualizada
        serializer = self.get_serializer(competition)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def assign_participant(self, request, pk=None):
        """Asignar un participante a una competencia"""
        competition = self.get_object()
        
        serializer = ParticipantAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rider_id = serializer.validated_data['rider_id']
        horse_id = serializer.validated_data['horse_id']
        category_id = serializer.validated_data['category_id']
        
        rider = Rider.objects.get(pk=rider_id)
        horse = Horse.objects.get(pk=horse_id)
        category = Category.objects.get(pk=category_id)
        
        # Generar número de participante automáticamente si no se proporciona
        number = serializer.validated_data.get('number')
        if not number:
            last_number = Participant.objects.filter(competition=competition).order_by('-number').first()
            number = (last_number.number + 1) if last_number else 1
        
        # Generar orden de salida automáticamente si no se proporciona
        order = serializer.validated_data.get('order')
        if not order:
            last_order = Participant.objects.filter(competition=competition).order_by('-order').first()
            order = (last_order.order + 1) if last_order else 1
        
        # Crear participante
        participant = Participant.objects.create(
            competition=competition,
            rider=rider,
            horse=horse,
            category=category,
            number=number,
            order=order
        )
        
        return Response(
            ParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RiderViewSet(viewsets.ModelViewSet):
    """ViewSet para jinetes"""
    
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Rider.objects.all()
        
        # Búsqueda por nombre
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        
        return queryset


class HorseViewSet(viewsets.ModelViewSet):
    """ViewSet para caballos"""
    
    queryset = Horse.objects.all()
    serializer_class = HorseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Horse.objects.all()
        
        # Búsqueda por nombre
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class ParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet para participantes"""
    
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = Participant.objects.all()
        
        # Filtrar por competencia
        competition_id = self.request.query_params.get('competition')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        # Filtrar por categoría
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Incluir o excluir retirados
        withdrawn = self.request.query_params.get('withdrawn')
        if withdrawn is not None:
            queryset = queryset.filter(is_withdrawn=(withdrawn.lower() == 'true'))
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def competition_participants(request, competition_id):
    """Obtener participantes de una competencia"""
    competition = get_object_or_404(Competition, pk=competition_id)
    participants = Participant.objects.filter(competition=competition)
    serializer = ParticipantSerializer(participants, many=True)
    return Response(serializer.data)