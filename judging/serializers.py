from rest_framework import serializers
from .models import (
    EvaluationParameter, CompetitionParameter, Score, ScoreEdit, 
    Ranking, FirebaseSync, OfflineData
)
from competitions.serializers import ParticipantSerializer
from users.serializers import UserSerializer


class EvaluationParameterSerializer(serializers.ModelSerializer):
    """Serializador para parámetros de evaluación"""
    
    class Meta:
        model = EvaluationParameter
        fields = ['id', 'name', 'description', 'coefficient', 'max_value']
        read_only_fields = ['id']


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


class ScoreSubmissionSerializer(serializers.Serializer):
    """Serializador para envío de calificaciones"""
    
    parameter_id = serializers.IntegerField()
    value = serializers.DecimalField(max_digits=4, decimal_places=1, min_value=0, max_value=10)
    comments = serializers.CharField(required=False, allow_blank=True)


class JudgeScoreCardSerializer(serializers.Serializer):
    """Serializador para tarjeta de calificación de un juez"""
    
    scores = ScoreSubmissionSerializer(many=True)
    edit_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_scores(self, scores):
        if not scores:
            raise serializers.ValidationError("Debe proporcionar al menos una calificación")
        return scores


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
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScoreCardParameterSerializer(serializers.Serializer):
    """Serializador para parámetros en tarjeta de calificación"""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    coefficient = serializers.IntegerField()
    max_value = serializers.IntegerField(default=10)
    order = serializers.IntegerField()


class ScoreCardResponseSerializer(serializers.Serializer):
    """Serializador para respuesta de tarjeta de calificación"""
    
    competition = serializers.IntegerField()
    participant = ParticipantSerializer()
    parameters = ScoreCardParameterSerializer(many=True)
    scores = serializers.DictField(child=serializers.DictField())