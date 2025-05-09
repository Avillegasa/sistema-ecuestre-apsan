# backend/competencias/views.py

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from usuarios.permissions import IsAdminUser, IsOwnerOrReadOnly, IsJineteOwner
from .models import Competencia, Categoria, CriterioEvaluacion, Inscripcion, AsignacionJuez
from .serializers import (
    CompetenciaSerializer, CompetenciaDetailSerializer,
    CategoriaSerializer, CategoriaDetailSerializer,
    CriterioEvaluacionSerializer,
    InscripcionSerializer, InscripcionDetailSerializer,
    AsignacionJuezSerializer
)

class CompetenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Competencia.
    """
    queryset = Competencia.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'fecha_inicio', 'organizador']
    search_fields = ['nombre', 'descripcion', 'ubicacion']
    ordering_fields = ['fecha_inicio', 'nombre', 'fecha_creacion']
    ordering = ['-fecha_inicio']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'categorias':
            return CompetenciaDetailSerializer
        return CompetenciaSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar competencias
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def categorias(self, request, pk=None):
        """
        Endpoint para obtener las categorías de una competencia específica.
        """
        competencia = self.get_object()
        categorias = competencia.categorias.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Endpoint para obtener competencias activas (en curso o con inscripciones abiertas).
        """
        today = timezone.now().date()
        competencias = Competencia.objects.filter(
            Q(estado='en_curso') | 
            (Q(estado='inscripciones_abiertas') & 
             Q(fecha_inicio_inscripciones__lte=today) & 
             Q(fecha_fin_inscripciones__gte=today))
        ).order_by('fecha_inicio')
        
        serializer = self.get_serializer(competencias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximas(self, request):
        """
        Endpoint para obtener competencias próximas (planificadas y futuras).
        """
        today = timezone.now().date()
        competencias = Competencia.objects.filter(
            fecha_inicio__gt=today,
            estado__in=['planificada', 'inscripciones_abiertas']
        ).order_by('fecha_inicio')
        
        serializer = self.get_serializer(competencias, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def finalizadas(self, request):
        """
        Endpoint para obtener competencias finalizadas.
        """
        competencias = Competencia.objects.filter(
            estado='finalizada'
        ).order_by('-fecha_fin')
        
        page = self.paginate_queryset(competencias)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(competencias, many=True)
        return Response(serializer.data)

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Categoria.
    """
    queryset = Categoria.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competencia', 'nivel']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'nivel']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'criterios':
            return CategoriaDetailSerializer
        return CategoriaSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar categorías
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def criterios(self, request, pk=None):
        """
        Endpoint para obtener los criterios de evaluación de una categoría específica.
        """
        categoria = self.get_object()
        criterios = categoria.criterios.all().order_by('orden', 'nombre')
        serializer = CriterioEvaluacionSerializer(criterios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def jueces(self, request, pk=None):
        """
        Endpoint para obtener los jueces asignados a una categoría específica.
        """
        categoria = self.get_object()
        asignaciones = categoria.jueces_asignados.filter(activo=True)
        serializer = AsignacionJuezSerializer(asignaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def inscripciones(self, request, pk=None):
        """
        Endpoint para obtener las inscripciones de una categoría específica.
        """
        categoria = self.get_object()
        inscripciones = categoria.inscripciones.all()
        serializer = InscripcionSerializer(inscripciones, many=True)
        return Response(serializer.data)

class CriterioEvaluacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo CriterioEvaluacion.
    """
    queryset = CriterioEvaluacion.objects.all()
    serializer_class = CriterioEvaluacionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria', 'categoria__competencia']
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar criterios
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class InscripcionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Inscripcion.
    """
    queryset = Inscripcion.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['competencia', 'categoria', 'estado', 'jinete', 'caballo']
    search_fields = ['jinete__usuario__first_name', 'jinete__usuario__last_name', 'caballo__nombre']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InscripcionDetailSerializer
        return InscripcionSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin o propietario (jinete) para actualizar o eliminar inscripciones
        - Usuario autenticado para crear y otras operaciones
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsJineteOwner | IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Asignar el jinete automáticamente si el usuario es un jinete.
        """
        user = self.request.user
        if user.tipo_usuario == 'jinete' and hasattr(user, 'jinete'):
            serializer.save(jinete=user.jinete)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def mis_inscripciones(self, request):
        """
        Endpoint para que un jinete obtenga sus propias inscripciones.
        """
        user = request.user
        if user.tipo_usuario != 'jinete' or not hasattr(user, 'jinete'):
            return Response(
                {"detail": "Solo los jinetes pueden acceder a este endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        inscripciones = Inscripcion.objects.filter(jinete=user.jinete)
        
        # Filtrar por competencia si se proporciona
        competencia_id = request.query_params.get('competencia', None)
        if competencia_id:
            inscripciones = inscripciones.filter(competencia_id=competencia_id)
        
        # Filtrar por estado si se proporciona
        estado = request.query_params.get('estado', None)
        if estado:
            inscripciones = inscripciones.filter(estado=estado)
        
        serializer = InscripcionDetailSerializer(inscripciones, many=True)
        return Response(serializer.data)

class AsignacionJuezViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo AsignacionJuez.
    """
    queryset = AsignacionJuez.objects.all()
    serializer_class = AsignacionJuezSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['juez', 'categoria', 'categoria__competencia', 'activo']
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para todas las operaciones
        - Juez solo para ver sus asignaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def mis_asignaciones(self, request):
        """
        Endpoint para que un juez obtenga sus propias asignaciones.
        """
        user = request.user
        if user.tipo_usuario != 'juez' or not hasattr(user, 'juez'):
            return Response(
                {"detail": "Solo los jueces pueden acceder a este endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        asignaciones = AsignacionJuez.objects.filter(juez=user.juez, activo=True)
        
        # Filtrar por competencia si se proporciona
        competencia_id = request.query_params.get('competencia', None)
        if competencia_id:
            asignaciones = asignaciones.filter(categoria__competencia_id=competencia_id)
        
        serializer = self.get_serializer(asignaciones, many=True)
        return Response(serializer.data)