"""
Serializadores optimizados para el sistema de calificación FEI de 3 celdas.
Implementa validaciones avanzadas y soporte para operaciones por lotes.
"""
from rest_framework import serializers
from django.db.models import Avg, Max, Min
from decimal import Decimal
import logging

from .models import (
    EvaluationParameter, CompetitionParameter, Score, ScoreEdit, 
    Ranking, FirebaseSync, OfflineData
)
from competitions.serializers import ParticipantSerializer
from users.serializers import UserSerializer

logger = logging.getLogger(__name__)

class EvaluationParameterSerializer(serializers.ModelSerializer):
    """Serializador para parámetros de evaluación FEI"""
    
    class Meta:
        model = EvaluationParameter
        fields = [
            'id', 'name', 'description', 'coefficient', 'max_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_coefficient(self, value):
        """Validar que el coeficiente esté dentro de los valores habituales FEI (1-3)"""
        if value <= 0:
            raise serializers.ValidationError("El coeficiente debe ser mayor que cero")
        if value > 3:
            raise serializers.ValidationError("El coeficiente es inusualmente alto para FEI")
        return value
    
    def validate_max_value(self, value):
        """Validar que el valor máximo sea positivo y típicamente 10 para FEI"""
        if value <= 0:
            raise serializers.ValidationError("El valor máximo debe ser mayor que cero")
        if value != 10:
            # Solo advertencia, no error, ya que pueden existir excepciones
            logger.warning(f"Valor máximo inusual para FEI: {value} (normalmente es 10)")
        return value


class CompetitionParameterSerializer(serializers.ModelSerializer):
    """Serializador para parámetros en competencias"""
    
    parameter_details = EvaluationParameterSerializer(source='parameter', read_only=True)
    effective_coefficient = serializers.IntegerField(read_only=True)
    effective_max_value = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CompetitionParameter
        fields = [
            'id', 'competition', 'parameter', 'parameter_details', 
            'order', 'custom_coefficient', 'custom_max_value',
            'effective_coefficient', 'effective_max_value'
        ]
        read_only_fields = ['id', 'effective_coefficient', 'effective_max_value']
    
    def validate(self, data):
        """Validar que los valores personalizados sean válidos según FEI"""
        custom_coefficient = data.get('custom_coefficient')
        if custom_coefficient is not None and custom_coefficient <= 0:
            raise serializers.ValidationError(
                {"custom_coefficient": "El coeficiente personalizado debe ser mayor que cero"}
            )
        
        custom_max_value = data.get('custom_max_value')
        if custom_max_value is not None and custom_max_value <= 0:
            raise serializers.ValidationError(
                {"custom_max_value": "El valor máximo personalizado debe ser mayor que cero"}
            )
        
        return data


class CompetitionParameterBulkSerializer(serializers.Serializer):
    """Serializador para crear/actualizar múltiples parámetros de competencia a la vez"""
    
    competition_id = serializers.IntegerField(required=True)
    parameters = serializers.ListField(
        child=serializers.DictField(
            child=serializers.Field(),
            allow_empty=False
        ),
        required=True,
        allow_empty=False
    )
    
    def validate_parameters(self, parameters):
        """Validar los parámetros en la lista"""
        for param in parameters:
            if 'parameter_id' not in param:
                raise serializers.ValidationError("Cada parámetro debe tener un parameter_id")
            
            if 'order' in param and not isinstance(param['order'], int):
                raise serializers.ValidationError("El orden debe ser un número entero")
                
            if 'custom_coefficient' in param:
                custom_coef = param['custom_coefficient']
                if custom_coef is not None and custom_coef <= 0:
                    raise serializers.ValidationError(
                        "El coeficiente personalizado debe ser mayor que cero"
                    )
            
            if 'custom_max_value' in param:
                custom_max = param['custom_max_value']
                if custom_max is not None and custom_max <= 0:
                    raise serializers.ValidationError(
                        "El valor máximo personalizado debe ser mayor que cero"
                    )
        
        return parameters


class ScoreEditSerializer(serializers.ModelSerializer):
    """Serializador para ediciones de calificaciones"""
    
    editor_details = UserSerializer(source='editor', read_only=True)
    
    class Meta:
        model = ScoreEdit
        fields = [
            'id', 'score', 'editor', 'editor_details', 
            'previous_value', 'previous_result', 'edit_reason', 'created_at'
        ]
        read_only_fields = [
            'id', 'score', 'editor', 'editor_details', 
            'previous_value', 'previous_result', 'created_at'
        ]


class ScoreSerializer(serializers.ModelSerializer):
    """Serializador para calificaciones"""
    
    judge_details = UserSerializer(source='judge', read_only=True)
    parameter_details = CompetitionParameterSerializer(source='parameter', read_only=True)
    edits = ScoreEditSerializer(source='edits', many=True, read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'id', 'competition', 'participant', 'judge', 'parameter',
            'judge_details', 'parameter_details',
            'value', 'calculated_result', 'comments',
            'is_edited', 'edit_reason', 'edits',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'calculated_result', 'is_edited', 'created_at', 'updated_at'
        ]
    
    def validate_value(self, value):
        """Validar que la calificación esté en el rango FEI (0-10)"""
        if value < 0 or value > 10:
            raise serializers.ValidationError("La calificación debe estar entre 0 y 10")
        return value
    
    def validate(self, data):
        """Validaciones adicionales para el modelo Score"""
        # Verificar coherencia entre competition y parameter
        parameter = data.get('parameter')
        competition = data.get('competition')
        
        if parameter and competition and parameter.competition_id != competition.id:
            raise serializers.ValidationError(
                "El parámetro debe pertenecer a la competencia especificada"
            )
        
        return data


class ScoreSubmissionSerializer(serializers.Serializer):
    """Serializador para envío de calificaciones individuales"""
    
    parameter_id = serializers.IntegerField()
    value = serializers.DecimalField(max_digits=4, decimal_places=1, min_value=0, max_value=10)
    comments = serializers.CharField(required=False, allow_blank=True)


class ScoreBulkSubmissionSerializer(serializers.Serializer):
    """Serializador para envío de múltiples calificaciones en una sola operación"""
    
    competition_id = serializers.IntegerField(required=True)
    participant_id = serializers.IntegerField(required=True)
    scores = serializers.ListField(
        child=ScoreSubmissionSerializer(),
        required=True,
        allow_empty=False
    )
    edit_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validar que la competencia y el participante existan"""
        from competitions.models import Competition, Participant
        
        competition_id = data.get('competition_id')
        participant_id = data.get('participant_id')
        
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            raise serializers.ValidationError(
                {"competition_id": f"No existe una competencia con ID {competition_id}"}
            )
        
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            raise serializers.ValidationError(
                {"participant_id": f"No existe un participante con ID {participant_id}"}
            )
        
        if participant.competition_id != competition.id:
            raise serializers.ValidationError(
                "El participante no pertenece a la competencia especificada"
            )
        
        return data


class JudgeScoreCardSerializer(serializers.Serializer):
    """Serializador para tarjeta de calificación de un juez"""
    
    scores = ScoreSubmissionSerializer(many=True)
    edit_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_scores(self, scores):
        if not scores:
            raise serializers.ValidationError("Debe proporcionar al menos una calificación")
        
        # Verificar que no haya parámetros duplicados
        parameter_ids = [score['parameter_id'] for score in scores]
        if len(parameter_ids) != len(set(parameter_ids)):
            raise serializers.ValidationError("No puede calificar el mismo parámetro más de una vez")
        
        return scores


class ScoreCardResponseSerializer(serializers.Serializer):
    """Serializador para respuesta de tarjeta de calificación"""
    
    competition = serializers.IntegerField()
    competition_name = serializers.CharField()
    participant = ParticipantSerializer()
    parameters = serializers.ListField(
        child=serializers.DictField()
    )
    scores = serializers.DictField(
        child=serializers.DictField()
    )
    last_updated = serializers.DateTimeField(allow_null=True)


class ScoreStatisticsSerializer(serializers.Serializer):
    """Serializador para estadísticas de calificaciones"""
    
    avg_score = serializers.FloatField()
    min_score = serializers.FloatField()
    max_score = serializers.FloatField()
    count = serializers.IntegerField()
    avg_result = serializers.FloatField()
    distribution = serializers.DictField(
        child=serializers.IntegerField()
    )


class JudgeComparisonSerializer(serializers.Serializer):
    """Serializador para comparación de calificaciones entre jueces"""
    
    judges = serializers.ListField(
        child=serializers.DictField()
    )
    parameters = serializers.ListField(
        child=serializers.DictField()
    )
    judges_count = serializers.IntegerField()
    parameters_count = serializers.IntegerField()


class RankingSerializer(serializers.ModelSerializer):
    """Serializador para rankings"""
    
    participant_details = ParticipantSerializer(source='participant', read_only=True)
    
    class Meta:
        model = Ranking
        fields = [
            'id', 'competition', 'participant', 'participant_details',
            'average_score', 'percentage', 'position',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Formatear valores numéricos para mejor presentación
        if instance.average_score is not None:
            representation['average_score'] = float(instance.average_score)
        
        if instance.percentage is not None:
            representation['percentage'] = float(instance.percentage)
        
        # Agregar posición anterior si está disponible para animaciones
        representation['previous_position'] = getattr(instance, 'previous_position', None)
        
        return representation


class FirebaseSyncSerializer(serializers.ModelSerializer):
    """Serializador para estado de sincronización con Firebase"""
    
    class Meta:
        model = FirebaseSync
        fields = [
            'id', 'competition', 'last_sync', 'is_synced', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'last_sync', 'created_at']


class OfflineDataSerializer(serializers.ModelSerializer):
    """Serializador para datos offline"""
    
    judge_details = UserSerializer(source='judge', read_only=True)
    
    class Meta:
        model = OfflineData
        fields = [
            'id', 'judge', 'judge_details', 'competition', 'participant', 
            'data', 'is_synced', 'sync_attempts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_synced', 'sync_attempts']
    
    def validate_data(self, data):
        """Validar estructura de datos para almacenamiento offline"""
        if not isinstance(data, dict):
            raise serializers.ValidationError("El campo 'data' debe ser un objeto JSON")
        
        # Validar estructura de calificaciones si están presentes
        if 'scores' in data:
            scores = data['scores']
            if not isinstance(scores, dict):
                raise serializers.ValidationError("El campo 'scores' debe ser un objeto JSON")
            
            for param_id, score_data in scores.items():
                if not isinstance(score_data, dict):
                    raise serializers.ValidationError(f"Los datos para el parámetro {param_id} deben ser un objeto JSON")
                
                if 'value' not in score_data:
                    raise serializers.ValidationError(f"Falta el campo 'value' para el parámetro {param_id}")
                
                # Validar el valor según normas FEI
                value = score_data.get('value')
                if value is not None:
                    try:
                        float_value = float(value)
                        if float_value < 0 or float_value > 10:
                            raise serializers.ValidationError(
                                f"El valor {value} para el parámetro {param_id} debe estar entre 0 y 10"
                            )
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(
                            f"El valor {value} para el parámetro {param_id} debe ser un número"
                        )
        
        return data


class SyncStatusSerializer(serializers.Serializer):
    """Serializador para estado de sincronización"""
    
    competition_id = serializers.IntegerField()
    is_synced = serializers.BooleanField()
    last_sync = serializers.DateTimeField(allow_null=True)
    error_message = serializers.CharField(allow_null=True, required=False)


class ScoreCardParameterSerializer(serializers.Serializer):
    """Serializador para parámetros en tarjeta de calificación"""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    coefficient = serializers.IntegerField()
    max_value = serializers.IntegerField(default=10)
    order = serializers.IntegerField()