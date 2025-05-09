# backend/evaluaciones/admin.py

from django.contrib import admin
from .models import Evaluacion, Puntuacion

class PuntuacionInline(admin.TabularInline):
    """
    Inline para mostrar puntuaciones dentro de una evaluación.
    """
    model = Puntuacion
    extra = 1
    fields = ('criterio', 'valor', 'comentario')
    readonly_fields = ('fecha_creacion',)

class EvaluacionAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Evaluacion.
    """
    list_display = ('get_competencia', 'get_categoria', 'get_jinete', 'get_caballo', 'get_juez', 'estado', 'puntaje_total', 'fecha_finalizacion')
    list_filter = ('estado', 'inscripcion__competencia', 'inscripcion__categoria', 'juez')
    search_fields = (
        'inscripcion__jinete__usuario__first_name', 'inscripcion__jinete__usuario__last_name',
        'inscripcion__caballo__nombre', 'juez__usuario__first_name', 'juez__usuario__last_name',
        'inscripcion__competencia__nombre', 'inscripcion__categoria__nombre'
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'puntaje_total')
    fieldsets = (
        (None, {
            'fields': ('inscripcion', 'juez', 'estado', 'puntaje_total')
        }),
        ('Fechas', {
            'fields': (('fecha_inicio', 'fecha_finalizacion'), ('fecha_creacion', 'fecha_actualizacion'))
        }),
        ('Comentarios', {
            'fields': ('comentario_general',)
        }),
    )
    inlines = [PuntuacionInline]
    
    def get_competencia(self, obj):
        """Obtener nombre de la competencia."""
        return obj.inscripcion.competencia.nombre
    get_competencia.short_description = 'Competencia'
    
    def get_categoria(self, obj):
        """Obtener nombre de la categoría."""
        return obj.inscripcion.categoria.nombre
    get_categoria.short_description = 'Categoría'
    
    def get_jinete(self, obj):
        """Obtener nombre del jinete."""
        return obj.inscripcion.jinete.usuario.get_full_name()
    get_jinete.short_description = 'Jinete'
    
    def get_caballo(self, obj):
        """Obtener nombre del caballo."""
        return obj.inscripcion.caballo.nombre
    get_caballo.short_description = 'Caballo'
    
    def get_juez(self, obj):
        """Obtener nombre del juez."""
        return obj.juez.usuario.get_full_name()
    get_juez.short_description = 'Juez'

class PuntuacionAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Puntuacion.
    """
    list_display = ('get_evaluacion', 'criterio', 'valor', 'fecha_actualizacion')
    list_filter = ('evaluacion__estado', 'criterio')
    search_fields = (
        'evaluacion__inscripcion__jinete__usuario__first_name',
        'evaluacion__inscripcion__jinete__usuario__last_name',
        'evaluacion__juez__usuario__first_name',
        'evaluacion__juez__usuario__last_name',
        'criterio__nombre'
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_evaluacion(self, obj):
        """Obtener información resumida de la evaluación."""
        return f"{obj.evaluacion.juez.usuario.get_full_name()} → {obj.evaluacion.inscripcion.jinete.usuario.get_full_name()}"
    get_evaluacion.short_description = 'Evaluación'

# Registrar los modelos en el admin
admin.site.register(Evaluacion, EvaluacionAdmin)
admin.site.register(Puntuacion, PuntuacionAdmin)