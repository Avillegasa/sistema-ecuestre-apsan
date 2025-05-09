# backend/rankings/permissions.py

from rest_framework import permissions

class IsJineteParticipante(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el jinete que participó en el resultado.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_authenticated and 
                    request.user.tipo_usuario == 'jinete' and 
                    hasattr(request.user, 'jinete') and 
                    request.user.jinete == obj.inscripcion.jinete)
        
        return False  # No permitir modificaciones

class IsEntrenadorDeJineteParticipante(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el entrenador del jinete que participó.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_authenticated and 
                    request.user.tipo_usuario == 'entrenador' and 
                    hasattr(request.user, 'entrenador') and 
                    obj.inscripcion.jinete.entrenador == request.user.entrenador)
        
        return False  # No permitir modificaciones

class IsRankingPublicado(permissions.BasePermission):
    """
    Permiso que verifica si el ranking está publicado para permitir acceso.
    """
    def has_object_permission(self, request, view, obj):
        # Si es admin, permitir siempre
        if request.user.is_authenticated and request.user.tipo_usuario == 'admin':
            return True
        
        # Para resultado de ranking
        if hasattr(obj, 'ranking'):
            return obj.ranking.publicado
        
        # Para el ranking mismo
        return obj.publicado