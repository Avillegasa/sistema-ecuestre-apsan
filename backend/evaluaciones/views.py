# backend/evaluaciones/views.py

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from usuarios.permissions import IsAdminUser, IsJuezOrReadOnly
from competencias.models import CriterioEvaluacion, Inscripcion
from .models import Evaluacion, Puntuacion
from .serializers import (
    EvaluacionSerializer, EvaluacionDetailSerializer, EvaluacionResumenSerializer,
    PuntuacionSerializer, PuntuacionDetailSerializer
)

class EvaluacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Evaluacion.
    """
    queryset = Evaluacion.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inscripcion__competencia', 'inscripcion__categoria', 'juez', 'estado']
    search_fields = [
        'inscripcion__jinete__usuario__first_name', 'inscripcion__jinete__usuario__last_name',
        'inscripcion__caballo__nombre', 'juez__usuario__first_name', 'juez__usuario__last_name'
    ]
    ordering_fields = ['fecha_creacion', 'fecha_finalizacion', 'puntaje_total']
    ordering = ['-fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            return EvaluacionDetailSerializer
        elif self.action == 'list' or self.action == 'mis_evaluaciones' or self.action == 'evaluaciones_por_inscripcion':
            return EvaluacionResumenSerializer
        return EvaluacionSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Solo jueces asignados pueden modificar evaluaciones
        - Admin puede hacer cualquier operación
        - Usuario autenticado para ver
        """
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsJuezOrReadOnly | IsAdminUser]
        elif self.action == 'create' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Establecer la fecha de inicio al crear una evaluación.
        """
        serializer.save(fecha_inicio=timezone.now())
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        """
        Endpoint para finalizar una evaluación.
        """
        evaluacion = self.get_object()
        
        # Verificar si el usuario es el juez asignado o admin
        user = request.user
        if not (user.tipo_usuario == 'admin' or (user.tipo_usuario == 'juez' and hasattr(user, 'juez') and user.juez == evaluacion.juez)):
            return Response(
                {"detail": "No tienes permiso para finalizar esta evaluación."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si la evaluación ya está finalizada
        if evaluacion.estado == 'completada':
            return Response(
                {"detail": "Esta evaluación ya está finalizada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si todos los criterios han sido evaluados
        if not evaluacion.verificar_completitud():
            return Response(
                {"detail": "No se han evaluado todos los criterios requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Finalizar la evaluación
        evaluacion.estado = 'completada'
        evaluacion.fecha_finalizacion = timezone.now()
        evaluacion.actualizar_puntaje_total()
        evaluacion.save()
        
        # Actualizar estado de la inscripción si todas las evaluaciones están completas
        inscripcion = evaluacion.inscripcion
        todas_evaluaciones_completas = inscripcion.evaluaciones.exclude(id=evaluacion.id).filter(estado='completada').exists()
        
        if todas_evaluaciones_completas:
            inscripcion.estado = 'completada'
            inscripcion.save()
        
        serializer = EvaluacionDetailSerializer(evaluacion)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_evaluaciones(self, request):
        """
        Endpoint para que un juez obtenga sus propias evaluaciones.
        """
        user = request.user
        if user.tipo_usuario != 'juez' or not hasattr(user, 'juez'):
            return Response(
                {"detail": "Solo los jueces pueden acceder a este endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        evaluaciones = Evaluacion.objects.filter(juez=user.juez)
        
        # Filtros adicionales
        estado = request.query_params.get('estado', None)
        competencia = request.query_params.get('competencia', None)
        categoria = request.query_params.get('categoria', None)
        
        if estado:
            evaluaciones = evaluaciones.filter(estado=estado)
        
        if competencia:
            evaluaciones = evaluaciones.filter(inscripcion__competencia_id=competencia)
        
        if categoria:
            evaluaciones = evaluaciones.filter(inscripcion__categoria_id=categoria)
        
        serializer = EvaluacionResumenSerializer(evaluaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def evaluaciones_por_inscripcion(self, request):
        """
        Endpoint para obtener evaluaciones por inscripción.
        """
        inscripcion_id = request.query_params.get('inscripcion', None)
        if not inscripcion_id:
            return Response(
                {"detail": "Se requiere el parámetro 'inscripcion'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            inscripcion = Inscripcion.objects.get(pk=inscripcion_id)
        except Inscripcion.DoesNotExist:
            return Response(
                {"detail": "Inscripción no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        if not (user.tipo_usuario == 'admin' or 
                (user.tipo_usuario == 'jinete' and hasattr(user, 'jinete') and user.jinete == inscripcion.jinete) or
                (user.tipo_usuario == 'juez' and hasattr(user, 'juez') and 
                 Evaluacion.objects.filter(inscripcion=inscripcion, juez=user.juez).exists())):
            return Response(
                {"detail": "No tienes permiso para ver estas evaluaciones."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        evaluaciones = Evaluacion.objects.filter(inscripcion=inscripcion)
        serializer = EvaluacionResumenSerializer(evaluaciones, many=True)
        return Response(serializer.data)

class PuntuacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Puntuacion.
    """
    queryset = Puntuacion.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['evaluacion', 'criterio', 'evaluacion__inscripcion', 'evaluacion__juez']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PuntuacionDetailSerializer
        return PuntuacionSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Solo jueces asignados pueden crear o modificar puntuaciones
        - Admin puede hacer cualquier operación
        - Usuario autenticado para ver
        """
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsJuezOrReadOnly | IsAdminUser]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Validar que el juez sea el asignado a la evaluación.
        """
        evaluacion = serializer.validated_data['evaluacion']
        user = self.request.user
        
        # Verificar si el usuario es el juez asignado o admin
        if not (user.tipo_usuario == 'admin' or 
                (user.tipo_usuario == 'juez' and hasattr(user, 'juez') and user.juez == evaluacion.juez)):
            raise permissions.PermissionDenied("No tienes permiso para crear puntuaciones en esta evaluación.")
        
        # Verificar que la evaluación no esté completada
        if evaluacion.estado == 'completada':
            raise serializers.ValidationError("No se pueden agregar puntuaciones a una evaluación completada.")
        
        # Si la evaluación está pendiente, cambiarla a en_progreso
        if evaluacion.estado == 'pendiente':
            evaluacion.estado = 'en_progreso'
            evaluacion.save(update_fields=['estado'])
        
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Validar que el juez sea el asignado a la evaluación.
        """
        evaluacion = serializer.instance.evaluacion
        user = self.request.user
        
        # Verificar si el usuario es el juez asignado o admin
        if not (user.tipo_usuario == 'admin' or 
                (user.tipo_usuario == 'juez' and hasattr(user, 'juez') and user.juez == evaluacion.juez)):
            raise permissions.PermissionDenied("No tienes permiso para modificar puntuaciones en esta evaluación.")
        
        # Verificar que la evaluación no esté completada
        if evaluacion.estado == 'completada':
            raise serializers.ValidationError("No se pueden modificar puntuaciones de una evaluación completada.")
        
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def puntuar_multiple(self, request):
        """
        Endpoint para crear o actualizar múltiples puntuaciones de una vez.
        """
        data = request.data
        evaluacion_id = data.get('evaluacion_id')
        puntuaciones = data.get('puntuaciones', [])
        
        if not evaluacion_id or not puntuaciones:
            return Response(
                {"detail": "Se requiere evaluacion_id y al menos una puntuación."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            evaluacion = Evaluacion.objects.get(pk=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {"detail": "Evaluación no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        if not (user.tipo_usuario == 'admin' or 
                (user.tipo_usuario == 'juez' and hasattr(user, 'juez') and user.juez == evaluacion.juez)):
            return Response(
                {"detail": "No tienes permiso para puntuar esta evaluación."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que la evaluación no esté completada
        if evaluacion.estado == 'completada':
            return Response(
                {"detail": "No se pueden modificar puntuaciones de una evaluación completada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si la evaluación está pendiente, cambiarla a en_progreso
        if evaluacion.estado == 'pendiente':
            evaluacion.estado = 'en_progreso'
            evaluacion.save(update_fields=['estado'])
        
        resultados = []
        for item in puntuaciones:
            criterio_id = item.get('criterio_id')
            valor = item.get('valor')
            comentario = item.get('comentario', '')
            
            if not criterio_id or valor is None:
                return Response(
                    {"detail": "Cada puntuación debe tener criterio_id y valor."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                criterio = CriterioEvaluacion.objects.get(pk=criterio_id)
            except CriterioEvaluacion.DoesNotExist:
                return Response(
                    {"detail": f"Criterio de evaluación {criterio_id} no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Buscar si ya existe una puntuación para este criterio en esta evaluación
            try:
                puntuacion = Puntuacion.objects.get(evaluacion=evaluacion, criterio=criterio)
                puntuacion.valor = valor
                puntuacion.comentario = comentario
                puntuacion.save()
            except Puntuacion.DoesNotExist:
                puntuacion = Puntuacion.objects.create(
                    evaluacion=evaluacion, 
                    criterio=criterio, 
                    valor=valor, 
                    comentario=comentario
                )
            
            resultados.append({
                'id': puntuacion.id,
                'criterio_id': criterio.id,
                'criterio_nombre': criterio.nombre,
                'valor': puntuacion.valor,
                'comentario': puntuacion.comentario
            })
        
        # Actualizar el puntaje total de la evaluación
        evaluacion.actualizar_puntaje_total()
        
        return Response({
            'evaluacion_id': evaluacion.id,
            'puntuaciones': resultados,
            'puntaje_total': evaluacion.puntaje_total,
            'completitud': evaluacion.verificar_completitud()
        })