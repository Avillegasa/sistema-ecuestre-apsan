# backend/rankings/serializers.py

from rest_framework import serializers
from competencias.serializers import CompetenciaSerializer, CategoriaSerializer, InscripcionSerializer
from .models import Ranking, ResultadoRanking, Certificado

class ResultadoRankingSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo ResultadoRanking.
    """
    class Meta:
        model = ResultadoRanking
        fields = [
            'id', 'ranking', 'inscripcion', 'posicion',
            'puntaje', 'medalla', 'comentario'
        ]

class ResultadoRankingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo ResultadoRanking con información de inscripción.
    """
    inscripcion_details = serializers.SerializerMethodField()
    certificado_disponible = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultadoRanking
        fields = [
            'id', 'ranking', 'inscripcion', 'inscripcion_details',
            'posicion', 'puntaje', 'medalla', 'comentario',
            'certificado_disponible'
        ]
    
    def get_inscripcion_details(self, obj):
        """
        Obtiene detalles resumidos de la inscripción.
        """
        return {
            'id': obj.inscripcion.id,
            'jinete': {
                'id': obj.inscripcion.jinete.id,
                'nombre': obj.inscripcion.jinete.usuario.get_full_name()
            },
            'caballo': {
                'id': obj.inscripcion.caballo.id,
                'nombre': obj.inscripcion.caballo.nombre,
                'raza': obj.inscripcion.caballo.raza
            },
            'numero_participante': obj.inscripcion.numero_participante
        }
    
    def get_certificado_disponible(self, obj):
        """
        Verifica si el resultado tiene un certificado asociado.
        """
        return hasattr(obj, 'certificado')

class RankingSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Ranking.
    """
    class Meta:
        model = Ranking
        fields = [
            'id', 'competencia', 'categoria', 'tipo',
            'fecha_generacion', 'fecha_publicacion', 'publicado',
            'descripcion'
        ]
        read_only_fields = ['fecha_generacion', 'fecha_publicacion']

class RankingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Ranking con competencia, categoría y resultados.
    """
    competencia_details = serializers.SerializerMethodField()
    categoria_details = serializers.SerializerMethodField()
    resultados = ResultadoRankingDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ranking
        fields = [
            'id', 'competencia', 'competencia_details',
            'categoria', 'categoria_details', 'tipo',
            'fecha_generacion', 'fecha_publicacion', 'publicado',
            'descripcion', 'resultados'
        ]
        read_only_fields = ['fecha_generacion', 'fecha_publicacion']
    
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

class CertificadoSerializer(serializers.ModelSerializer):
    """
    Serializer básico para el modelo Certificado.
    """
    class Meta:
        model = Certificado
        fields = [
            'id', 'resultado', 'tipo', 'codigo',
            'fecha_generacion', 'archivo'
        ]
        read_only_fields = ['codigo', 'fecha_generacion']

class CertificadoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para el modelo Certificado con información del resultado.
    """
    participante = serializers.SerializerMethodField()
    competencia = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    resultado_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificado
        fields = [
            'id', 'resultado', 'resultado_details',
            'participante', 'competencia', 'categoria',
            'tipo', 'codigo', 'fecha_generacion', 'archivo'
        ]
        read_only_fields = ['codigo', 'fecha_generacion']
    
    def get_participante(self, obj):
        """
        Obtiene información del participante.
        """
        return {
            'jinete': obj.resultado.inscripcion.jinete.usuario.get_full_name(),
            'caballo': obj.resultado.inscripcion.caballo.nombre
        }
    
    def get_competencia(self, obj):
        """
        Obtiene información de la competencia.
        """
        return {
            'id': obj.resultado.ranking.competencia.id,
            'nombre': obj.resultado.ranking.competencia.nombre
        }
    
    def get_categoria(self, obj):
        """
        Obtiene información de la categoría.
        """
        return {
            'id': obj.resultado.ranking.categoria.id,
            'nombre': obj.resultado.ranking.categoria.nombre
        }
    
    def get_resultado_details(self, obj):
        """
        Obtiene detalles del resultado.
        """
        return {
            'posicion': obj.resultado.posicion,
            'puntaje': obj.resultado.puntaje,
            'medalla': obj.resultado.medalla
        }