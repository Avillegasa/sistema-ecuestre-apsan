# backend/usuarios/permissions.py

from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permiso que permite acceso solo a usuarios administradores.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.tipo_usuario == 'admin'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite modificar solo a propietarios o permite lectura.
    Para usuarios regulares (no administradores), los usuarios solo pueden
    modificar sus propios datos.
    """
    def has_object_permission(self, request, view, obj):
        # Permitir solicitudes de lectura (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Si es administrador, permitir todo
        if request.user.tipo_usuario == 'admin':
            return True
        
        # Para modelos con usuario (OneToOne)
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        # Para el modelo Usuario
        return obj == request.user

class IsJineteOwner(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el jinete propietario de un caballo.
    """
    def has_object_permission(self, request, view, obj):
        # Verificar si es un caballo y el usuario es el jinete propietario
        if hasattr(obj, 'jinete'):
            return (
                request.user.is_authenticated and 
                request.user.tipo_usuario == 'jinete' and 
                hasattr(request.user, 'jinete') and 
                request.user.jinete == obj.jinete
            )
        return False

class IsEntrenadorOfJinete(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es entrenador del jinete.
    """
    def has_object_permission(self, request, view, obj):
        # Si el objeto es un jinete, verificar si el usuario es su entrenador
        if hasattr(obj, 'entrenador'):
            return (
                request.user.is_authenticated and 
                request.user.tipo_usuario == 'entrenador' and 
                hasattr(request.user, 'entrenador') and 
                request.user.entrenador == obj.entrenador
            )
        
        # Si el objeto es un caballo, verificar si el usuario es entrenador del jinete
        if hasattr(obj, 'jinete') and hasattr(obj.jinete, 'entrenador'):
            return (
                request.user.is_authenticated and 
                request.user.tipo_usuario == 'entrenador' and 
                hasattr(request.user, 'entrenador') and 
                request.user.entrenador == obj.jinete.entrenador
            )
        
        return False

class IsJuezOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite a los jueces modificar evaluaciones asignadas.
    """
    def has_permission(self, request, view):
        # Permitir solicitudes de lectura a usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Permitir modificación solo a jueces
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.tipo_usuario == 'juez'
        )
    
    def has_object_permission(self, request, view, obj):
        # Permitir solicitudes de lectura a usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Para evaluaciones, verificar si el juez está asignado
        if hasattr(obj, 'juez'):
            return (
                request.user.tipo_usuario == 'juez' and 
                hasattr(request.user, 'juez') and 
                request.user.juez == obj.juez
            )
        
        return False