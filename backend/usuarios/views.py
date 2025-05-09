# backend/usuarios/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Jinete, Juez, Entrenador, Caballo
from .serializers import (
    UsuarioSerializer, UsuarioDetailSerializer, UsuarioCreateSerializer,
    JineteSerializer, JineteDetailSerializer,
    JuezSerializer, JuezDetailSerializer,
    EntrenadorSerializer, EntrenadorDetailSerializer,
    CaballoSerializer, CaballoDetailSerializer
)
from .permissions import IsAdminUser, IsOwnerOrReadOnly, IsJineteOwner

Usuario = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Usuario.
    """
    queryset = Usuario.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action == 'retrieve':
            return UsuarioDetailSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar usuarios
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener información del usuario autenticado.
        """
        serializer = UsuarioDetailSerializer(request.user)
        return Response(serializer.data)

class JineteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Jinete.
    """
    queryset = Jinete.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JineteDetailSerializer
        return JineteSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar jinetes
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def caballos(self, request, pk=None):
        """
        Endpoint para obtener los caballos de un jinete específico.
        """
        jinete = self.get_object()
        caballos = jinete.caballos.all()
        serializer = CaballoSerializer(caballos, many=True)
        return Response(serializer.data)

class JuezViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Juez.
    """
    queryset = Juez.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JuezDetailSerializer
        return JuezSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar jueces
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class EntrenadorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Entrenador.
    """
    queryset = Entrenador.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EntrenadorDetailSerializer
        return EntrenadorSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar entrenadores
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def jinetes(self, request, pk=None):
        """
        Endpoint para obtener los jinetes asignados a un entrenador específico.
        """
        entrenador = self.get_object()
        jinetes = entrenador.jinetes.all()
        serializer = JineteSerializer(jinetes, many=True)
        return Response(serializer.data)

class CaballoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Caballo.
    """
    queryset = Caballo.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CaballoDetailSerializer
        return CaballoSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Solo el jinete propietario o admin pueden modificar el caballo
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsJineteOwner | IsAdminUser]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Asignar el jinete al crear un caballo.
        Si el usuario es un jinete, se asigna automáticamente.
        """
        user = self.request.user
        if user.tipo_usuario == 'jinete' and hasattr(user, 'jinete'):
            serializer.save(jinete=user.jinete)
        else:
            # Si no es jinete, el campo jinete debe venir en los datos
            serializer.save()