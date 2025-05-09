# backend/rankings/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Ranking, ResultadoRanking, Certificado

class ResultadoRankingInline(admin.TabularInline):
    """
    Inline para mostrar resultados dentro de un ranking.
    """
    model = ResultadoRanking
    extra = 1
    fields = ('posicion', 'inscripcion', 'puntaje', 'medalla')
    readonly_fields = ('inscripcion',)
    ordering = ('posicion',)
    max_num = 20  # Limitar para mejorar el rendimiento

class RankingAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Ranking.
    """
    list_display = ('get_categoria_competencia', 'tipo', 'publicado', 'fecha_generacion', 'fecha_publicacion')
    list_filter = ('tipo', 'publicado', 'competencia', 'categoria')
    search_fields = ('competencia__nombre', 'categoria__nombre')
    readonly_fields = ('fecha_generacion',)
    actions = ['generar_resultados', 'publicar_rankings']
    inlines = [ResultadoRankingInline]
    
    def get_categoria_competencia(self, obj):
        """Obtener información combinada de categoría y competencia."""
        return f"{obj.categoria.nombre} - {obj.competencia.nombre}"
    get_categoria_competencia.short_description = 'Categoría / Competencia'
    
    def generar_resultados(self, request, queryset):
        """Acción para generar los resultados de los rankings seleccionados."""
        for ranking in queryset:
            ranking.generar_resultados()
        self.message_user(request, f"{queryset.count()} rankings generados correctamente.")
    generar_resultados.short_description = "Generar resultados de los rankings seleccionados"
    
    def publicar_rankings(self, request, queryset):
        """Acción para publicar los rankings seleccionados."""
        for ranking in queryset:
            ranking.publicar()
        self.message_user(request, f"{queryset.count()} rankings publicados correctamente.")
    publicar_rankings.short_description = "Publicar los rankings seleccionados"

class ResultadoRankingAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo ResultadoRanking.
    """
    list_display = ('posicion', 'get_jinete_caballo', 'get_ranking_info', 'puntaje', 'medalla', 'get_certificado')
    list_filter = ('ranking__competencia', 'ranking__categoria', 'ranking__tipo', 'medalla')
    search_fields = (
        'inscripcion__jinete__usuario__first_name', 'inscripcion__jinete__usuario__last_name',
        'inscripcion__caballo__nombre', 'ranking__competencia__nombre', 'ranking__categoria__nombre'
    )
    readonly_fields = ('ranking', 'inscripcion', 'posicion', 'puntaje')
    
    def get_jinete_caballo(self, obj):
        """Obtener información del jinete y caballo."""
        return f"{obj.inscripcion.jinete.usuario.get_full_name()} con {obj.inscripcion.caballo.nombre}"
    get_jinete_caballo.short_description = 'Jinete / Caballo'
    
    def get_ranking_info(self, obj):
        """Obtener información del ranking."""
        return f"{obj.ranking.get_tipo_display()} - {obj.ranking.categoria.nombre} - {obj.ranking.competencia.nombre}"
    get_ranking_info.short_description = 'Ranking'
    
    def get_certificado(self, obj):
        """Mostrar si tiene certificado y enlace si existe."""
        if hasattr(obj, 'certificado'):
            if obj.certificado.archivo:
                return format_html(
                    '<a href="{}" target="_blank">Ver Certificado</a>',
                    obj.certificado.archivo.url
                )
            return "Sin archivo"
        return "No generado"
    get_certificado.short_description = 'Certificado'

class CertificadoAdmin(admin.ModelAdmin):
    """
    Personalización del admin para el modelo Certificado.
    """
    list_display = ('get_participante', 'tipo', 'codigo', 'fecha_generacion', 'get_archivo')
    list_filter = ('tipo', 'resultado__ranking__competencia', 'resultado__ranking__categoria')
    search_fields = (
        'codigo', 
        'resultado__inscripcion__jinete__usuario__first_name',
        'resultado__inscripcion__jinete__usuario__last_name',
        'resultado__inscripcion__caballo__nombre'
    )
    readonly_fields = ('codigo', 'fecha_generacion')
    actions = ['generar_pdf_certificados']
    
    def get_participante(self, obj):
        """Obtener información del participante."""
        return f"{obj.resultado.inscripcion.jinete.usuario.get_full_name()} - {obj.resultado.posicion}° lugar"
    get_participante.short_description = 'Participante'
    
    def get_archivo(self, obj):
        """Mostrar enlace al archivo si existe."""
        if obj.archivo:
            return format_html(
                '<a href="{}" target="_blank">Descargar PDF</a>',
                obj.archivo.url
            )
        return "No generado"
    get_archivo.short_description = 'Archivo'
    
    def generar_pdf_certificados(self, request, queryset):
        """Acción para generar los archivos PDF de los certificados seleccionados."""
        for certificado in queryset:
            certificado.generar_pdf()
        self.message_user(request, f"Proceso de generación de {queryset.count()} certificados iniciado.")
    generar_pdf_certificados.short_description = "Generar archivos PDF de certificados seleccionados"

# Registrar los modelos en el admin
admin.site.register(Ranking, RankingAdmin)
admin.site.register(ResultadoRanking, ResultadoRankingAdmin)
admin.site.register(Certificado, CertificadoAdmin)