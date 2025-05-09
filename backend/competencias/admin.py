# backend/competencias/admin.py

from django.contrib import admin
from .models import Competencia, Categoria, CriterioEvaluacion, Inscripcion, AsignacionJuez

class CategoriaInline(admin.TabularInline):
    """
    Inline para mostrar categorías dentro de competencia.
    """
    model = Categoria
    extra = 1
    fields = ('nombre', 'nivel', 'edad_minima', 'edad_maxima', 'cupo_maximo', 'precio_inscripcion')

class CriterioEvaluacionInline(admin.TabularInline):
    """
    Inline para mostrar criterios de evaluación dentro de categoría.
    """
    model = CriterioEvaluacion
    extra = 1
    fields = ('nombre', 'puntaje_maximo', 'peso', 'orden')

class AsignacionJuezInline(admin.TabularInline):
    """
    Inline para mostrar jueces asignados dentro de categoría.
    """
    model = AsignacionJuez
    extra = 1
    fields = ('juez', 'rol', 'activo')

class CompetenciaAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Competencia.
    """
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'ubicacion', 'organizador')
    list_filter = ('estado', 'fecha_inicio')
    search_fields = ('nombre', 'ubicacion', 'organizador')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'estado', 'imagen')
        }),
        ('Fechas', {
            'fields': (('fecha_inicio', 'fecha_fin'), ('fecha_inicio_inscripciones', 'fecha_fin_inscripciones'))
        }),
        ('Ubicación y Contacto', {
            'fields': ('ubicacion', 'organizador', 'contacto_email', 'contacto_telefono')
        }),
        ('Información Adicional', {
            'fields': ('reglamento', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    inlines = [CategoriaInline]

class CategoriaAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Categoría.
    """
    list_display = ('nombre', 'competencia', 'nivel', 'edad_minima', 'edad_maxima', 'cupo_maximo', 'precio_inscripcion')
    list_filter = ('competencia', 'nivel')
    search_fields = ('nombre', 'competencia__nombre')
    inlines = [CriterioEvaluacionInline, AsignacionJuezInline]

class CriterioEvaluacionAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo CriterioEvaluacion.
    """
    list_display = ('nombre', 'categoria', 'puntaje_maximo', 'peso', 'orden')
    list_filter = ('categoria__competencia', 'categoria')
    search_fields = ('nombre', 'categoria__nombre', 'categoria__competencia__nombre')

class InscripcionAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Inscripcion.
    """
    list_display = ('get_jinete', 'get_caballo', 'competencia', 'categoria', 'numero_participante', 'estado', 'fecha_inscripcion')
    list_filter = ('competencia', 'categoria', 'estado')
    search_fields = ('jinete__usuario__first_name', 'jinete__usuario__last_name', 'caballo__nombre', 'competencia__nombre')
    readonly_fields = ('fecha_inscripcion', 'fecha_actualizacion')
    
    def get_jinete(self, obj):
        """Obtener nombre del jinete."""
        return obj.jinete.usuario.get_full_name()
    get_jinete.short_description = 'Jinete'
    
    def get_caballo(self, obj):
        """Obtener nombre del caballo."""
        return obj.caballo.nombre
    get_caballo.short_description = 'Caballo'

class AsignacionJuezAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo AsignacionJuez.
    """
    list_display = ('get_juez', 'get_categoria', 'get_competencia', 'rol', 'activo', 'fecha_asignacion')
    list_filter = ('categoria__competencia', 'categoria', 'activo')
    search_fields = ('juez__usuario__first_name', 'juez__usuario__last_name', 'categoria__nombre', 'categoria__competencia__nombre')
    
    def get_juez(self, obj):
        """Obtener nombre del juez."""
        return obj.juez.usuario.get_full_name()
    get_juez.short_description = 'Juez'
    
    def get_categoria(self, obj):
        """Obtener nombre de la categoría."""
        return obj.categoria.nombre
    get_categoria.short_description = 'Categoría'
    
    def get_competencia(self, obj):
        """Obtener nombre de la competencia."""
        return obj.categoria.competencia.nombre
    get_competencia.short_description = 'Competencia'

# Registrar los modelos en el admin
admin.site.register(Competencia, CompetenciaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(CriterioEvaluacion, CriterioEvaluacionAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(AsignacionJuez, AsignacionJuezAdmin)