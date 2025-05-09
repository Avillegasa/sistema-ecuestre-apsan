# backend/usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Jinete, Juez, Entrenador, Caballo

class UsuarioAdmin(UserAdmin):
    """
    Personalización del admin para el modelo Usuario.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_active')
    list_filter = ('tipo_usuario', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono', 
                                           'direccion', 'fecha_nacimiento', 'foto_perfil')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'tipo_usuario')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class JineteAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Jinete.
    """
    list_display = ('get_nombre_completo', 'documento_identidad', 'experiencia_anios', 
                   'categoria_habitual', 'federado', 'get_entrenador')
    list_filter = ('federado', 'categoria_habitual')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 
                    'documento_identidad')
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del jinete."""
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_entrenador(self, obj):
        """Obtener nombre del entrenador si existe."""
        if obj.entrenador:
            return obj.entrenador.usuario.get_full_name()
        return 'Sin entrenador'
    get_entrenador.short_description = 'Entrenador'

class JuezAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Juez.
    """
    list_display = ('get_nombre_completo', 'licencia', 'especialidad', 
                   'nivel_certificacion', 'anios_experiencia')
    list_filter = ('especialidad', 'nivel_certificacion')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 
                    'licencia')
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del juez."""
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'

class EntrenadorAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Entrenador.
    """
    list_display = ('get_nombre_completo', 'especialidad', 'licencia', 
                   'anios_experiencia', 'get_jinetes_count')
    list_filter = ('especialidad',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 
                    'licencia')
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo del entrenador."""
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_jinetes_count(self, obj):
        """Obtener cantidad de jinetes asignados."""
        return obj.jinetes.count()
    get_jinetes_count.short_description = 'Jinetes Asignados'

class CaballoAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Caballo.
    """
    list_display = ('nombre', 'get_jinete', 'raza', 'fecha_nacimiento', 
                   'get_edad', 'numero_registro', 'genero', 'color')
    list_filter = ('raza', 'genero')
    search_fields = ('nombre', 'numero_registro', 'jinete__usuario__first_name', 
                    'jinete__usuario__last_name')
    
    def get_jinete(self, obj):
        """Obtener nombre del jinete propietario."""
        return obj.jinete.usuario.get_full_name()
    get_jinete.short_description = 'Jinete'
    
    def get_edad(self, obj):
        """Obtener edad del caballo."""
        return obj.edad()
    get_edad.short_description = 'Edad (años)'

# Registrar los modelos en el admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Jinete, JineteAdmin)
admin.site.register(Juez, JuezAdmin)
admin.site.register(Entrenador, EntrenadorAdmin)
admin.site.register(Caballo, CaballoAdmin)