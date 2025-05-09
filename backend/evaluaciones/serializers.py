# backend/evaluaciones/serializers.py

from rest_framework import serializers
from competencias.serializers import InscripcionSerializer, CriterioEvaluacionSerializer
from usuarios.serializers import JuezSerializer
from .models import Evaluacion, Puntuacion

class PuntuacionSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Puntuacion.
    """
    class Meta:
        model = Puntuacion
        fields = [
            'id', 'evaluacion', 'criterio', 'valor',
            'comentario', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

class PuntuacionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Puntuacion que incluye detalles del criterio.
    """
    criterio_details = CriterioEvaluacionSerializer(source='criterio', read_only=True)
    
    class Meta:
        model = Puntuacion
        fields = [
            'id', 'evaluacion', 'criterio', 'criterio_details',
            'valor', 'comentario', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

class EvaluacionSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Evaluacion.
    """
    class Meta:
        model = Evaluacion
        fields = [
            'id', 'inscripcion', 'juez', 'estado',
            'comentario_general', 'fecha_inicio', 'fecha_finalizacion',
            'puntaje_total', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = [
            'fecha_creacion', 'fecha_actualizacion', 'puntaje_total'
        ]

class EvaluacionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Evaluacion con inscripción, juez y puntuaciones.
    """
    inscripcion_details = serializers.SerializerMethodField()
    juez_details = serializers.SerializerMethodField()
    puntuaciones = PuntuacionDetailSerializer(many=True, read_only=True)
    completitud = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluacion
        fields = [
            'id', 'inscripcion', 'inscripcion_details',
            'juez', 'juez_details', 'estado',
            'comentario_general', 'fecha_inicio', 'fecha_finalizacion',
            'puntaje_total', 'fecha_creacion', 'fecha_actualizacion',
            'puntuaciones', 'completitud'
        ]
        read_only_fields = [
            'fecha_creacion', 'fecha_actualizacion', 'puntaje_total'
        ]
    
    def get_inscripcion_details(self, obj):
        """
        Obtiene detalles resumidos de la inscripción evaluada.
        """
        return {
            'id': obj.inscripcion.id,
            'competencia': {
                'id': obj.inscripcion.competencia.id,
                'nombre': obj.inscripcion.competencia.nombre
            },
            'categoria': {
                'id': obj.inscripcion.categoria.id,
                'nombre': obj.inscripcion.categoria.nombre
            },
            'jinete': {
                'id': obj.inscripcion.jinete.id,
                'nombre': obj.inscripcion.jinete.usuario.get_full_name()
            },
            'caballo': {
                'id': obj.inscripcion.caballo.id,
                'nombre': obj.inscripcion.caballo.nombre
            },
            'numero_participante': obj.inscripcion.numero_participante
        }
    
    def get_juez_details(self, obj):
        """
        Obtiene detalles resumidos del juez.
        """
        return {
            'id': obj.juez.id,
            'nombre': obj.juez.usuario.get_full_name(),
            'especialidad': obj.juez.especialidad
        }
    
    def get_completitud(self, obj):
        """
        Indica si la evaluación está completa (todos los criterios evaluados).
        """
        return obj.verificar_completitud()

class EvaluacionResumenSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para el modelo Evaluacion con información básica.
    """
    jinete = serializers.SerializerMethodField()
    caballo = serializers.SerializerMethodField()
    juez_nombre = serializers.SerializerMethodField()
    competencia = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluacion
        fields = [
            'id', 'jinete', 'caballo', 'juez_nombre',
            'competencia', 'categoria', 'estado',
            'puntaje_total', 'fecha_finalizacion'
        ]
    
    def get_jinete(self, obj):
        """Obtener nombre del jinete."""
        return obj.inscripcion.jinete.usuario.get_full_name()
    
    def get_caballo(self, obj):
        """Obtener nombre del caballo."""
        return obj.inscripcion.caballo.nombre
    
    def get_juez_nombre(self, obj):
        """Obtener nombre del juez."""
        return obj.juez.usuario.get_full_name()
    
    def get_competencia(self, obj):
        """Obtener nombre de la competencia."""
        return obj.inscripcion.competencia.nombre
    
    def get_categoria(self, obj):
        """Obtener nombre de la categoría."""
        return obj.inscripcion.categoria.nombre