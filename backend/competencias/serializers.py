# backend/competencias/serializers.py

from rest_framework import serializers
from usuarios.serializers import JineteSerializer, JuezSerializer, CaballoSerializer
from .models import Competencia, Categoria, CriterioEvaluacion, Inscripcion, AsignacionJuez

class CompetenciaSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Competencia.
    """
    class Meta:
        model = Competencia
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin',
            'fecha_inicio_inscripciones', 'fecha_fin_inscripciones',
            'ubicacion', 'estado', 'imagen', 'organizador',
            'contacto_email', 'contacto_telefono', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

class CriterioEvaluacionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CriterioEvaluacion.
    """
    class Meta:
        model = CriterioEvaluacion
        fields = [
            'id', 'categoria', 'nombre', 'descripcion',
            'puntaje_maximo', 'peso', 'orden'
        ]

class AsignacionJuezSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo AsignacionJuez.
    """
    juez_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AsignacionJuez
        fields = [
            'id', 'juez', 'juez_details', 'categoria',
            'rol', 'fecha_asignacion', 'activo'
        ]
        read_only_fields = ['fecha_asignacion']
    
    def get_juez_details(self, obj):
        """
        Obtiene detalles básicos del juez.
        """
        return {
            'id': obj.juez.id,
            'nombre': obj.juez.usuario.get_full_name(),
            'especialidad': obj.juez.especialidad
        }

class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Categoria.
    """
    class Meta:
        model = Categoria
        fields = [
            'id', 'competencia', 'nombre', 'descripcion',
            'edad_minima', 'edad_maxima', 'nivel',
            'cupo_maximo', 'precio_inscripcion'
        ]

class CategoriaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Categoria que incluye criterios y jueces.
    """
    criterios = CriterioEvaluacionSerializer(many=True, read_only=True)
    jueces_asignados = AsignacionJuezSerializer(many=True, read_only=True)
    plazas_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = [
            'id', 'competencia', 'nombre', 'descripcion',
            'edad_minima', 'edad_maxima', 'nivel',
            'cupo_maximo', 'precio_inscripcion',
            'criterios', 'jueces_asignados', 'plazas_disponibles'
        ]
    
    def get_plazas_disponibles(self, obj):
        """
        Obtiene las plazas disponibles en la categoría.
        """
        return obj.plazas_disponibles()

class CompetenciaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Competencia que incluye categorías.
    """
    categorias = CategoriaSerializer(many=True, read_only=True)
    inscripciones_activas = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Competencia
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin',
            'fecha_inicio_inscripciones', 'fecha_fin_inscripciones',
            'ubicacion', 'estado', 'imagen', 'organizador',
            'contacto_email', 'contacto_telefono', 'reglamento',
            'fecha_creacion', 'fecha_actualizacion',
            'categorias', 'inscripciones_activas'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

class InscripcionSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Inscripcion.
    """
    class Meta:
        model = Inscripcion
        fields = [
            'id', 'competencia', 'categoria', 'jinete', 'caballo',
            'estado', 'numero_participante', 'comentarios',
            'fecha_inscripcion', 'comprobante_pago'
        ]
        read_only_fields = ['fecha_inscripcion', 'fecha_actualizacion']

class InscripcionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Inscripcion con información de jinete y caballo.
    """
    jinete_details = serializers.SerializerMethodField()
    caballo_details = serializers.SerializerMethodField()
    competencia_details = serializers.SerializerMethodField()
    categoria_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscripcion
        fields = [
            'id', 'competencia', 'competencia_details',
            'categoria', 'categoria_details',
            'jinete', 'jinete_details',
            'caballo', 'caballo_details',
            'estado', 'numero_participante', 'comentarios',
            'fecha_inscripcion', 'fecha_actualizacion',
            'comprobante_pago'
        ]
        read_only_fields = ['fecha_inscripcion', 'fecha_actualizacion']
    
    def get_jinete_details(self, obj):
        """
        Obtiene detalles básicos del jinete.
        """
        return {
            'id': obj.jinete.id,
            'nombre': obj.jinete.usuario.get_full_name(),
            'categoria_habitual': obj.jinete.categoria_habitual
        }
    
    def get_caballo_details(self, obj):
        """
        Obtiene detalles básicos del caballo.
        """
        return {
            'id': obj.caballo.id,
            'nombre': obj.caballo.nombre,
            'raza': obj.caballo.raza,
            'edad': obj.caballo.edad()
        }
    
    def get_competencia_details(self, obj):
        """
        Obtiene detalles básicos de la competencia.
        """
        return {
            'id': obj.competencia.id,
            'nombre': obj.competencia.nombre,
            'fecha_inicio': obj.competencia.fecha_inicio,
            'fecha_fin': obj.competencia.fecha_fin,
            'estado': obj.competencia.estado
        }
    
    def get_categoria_details(self, obj):
        """
        Obtiene detalles básicos de la categoría.
        """
        return {
            'id': obj.categoria.id,
            'nombre': obj.categoria.nombre,
            'nivel': obj.categoria.nivel
        }