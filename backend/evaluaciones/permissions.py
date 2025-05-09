# backend/evaluaciones/permissions.py

from rest_framework import permissions

class IsJuezAsignado(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el juez asignado a la evaluación.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (request.user.is_authenticated and 
                request.user.tipo_usuario == 'juez' and 
                hasattr(request.user, 'juez') and 
                request.user.juez == obj.juez)

class IsJineteEvaluado(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el jinete que está siendo evaluado.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_authenticated and 
                    request.user.tipo_usuario == 'jinete' and 
                    hasattr(request.user, 'jinete') and 
                    request.user.jinete == obj.inscripcion.jinete)
        
        return False  # No permitir modificaciones

class IsEntrenadorDeJineteEvaluado(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el entrenador del jinete que está siendo evaluado.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_authenticated and 
                    request.user.tipo_usuario == 'entrenador' and 
                    hasattr(request.user, 'entrenador') and 
                    obj.inscripcion.jinete.entrenador == request.user.entrenador)
        
        return False  # No permitir modificaciones