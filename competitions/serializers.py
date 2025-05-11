from rest_framework import serializers
from .models import (
    Competition, Category, CompetitionCategory, 
    CompetitionJudge, Rider, Horse, Participant
)
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'code', 'min_age', 'max_age']


class CompetitionCategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías en competencias"""
    
    category_details = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = CompetitionCategory
        fields = ['id', 'competition', 'category', 'category_details', 'start_time', 'end_time']
        read_only_fields = ['id']


class CompetitionJudgeSerializer(serializers.ModelSerializer):
    """Serializador para jueces en competencias"""
    
    judge_details = UserSerializer(source='judge', read_only=True)
    
    class Meta:
        model = CompetitionJudge
        fields = ['id', 'competition', 'judge', 'judge_details', 'is_head_judge']
        read_only_fields = ['id']


class RiderSerializer(serializers.ModelSerializer):
    """Serializador para jinetes"""
    
    class Meta:
        model = Rider
        fields = [
            'id', 'first_name', 'last_name', 'birth_date', 
            'nationality', 'gender', 'email', 'phone'
        ]
        read_only_fields = ['id']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['full_name'] = f"{instance.first_name} {instance.last_name}"
        return representation


class HorseSerializer(serializers.ModelSerializer):
    """Serializador para caballos"""
    
    class Meta:
        model = Horse
        fields = [
            'id', 'name', 'breed', 'birth_year', 'gender', 
            'height', 'color', 'registration_number', 'microchip'
        ]
        read_only_fields = ['id']


class ParticipantSerializer(serializers.ModelSerializer):
    """Serializador para participantes"""
    
    rider_details = RiderSerializer(source='rider', read_only=True)
    horse_details = HorseSerializer(source='horse', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Participant
        fields = [
            'id', 'competition', 'rider', 'horse', 'category', 
            'rider_details', 'horse_details', 'category_details',
            'number', 'order', 'is_withdrawn', 'withdrawal_reason'
        ]
        read_only_fields = ['id']


class CompetitionListSerializer(serializers.ModelSerializer):
    """Serializador para listado de competencias"""
    
    creator_details = UserSerializer(source='creator', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'location', 'start_date', 'end_date', 
            'status', 'status_display', 'is_public', 
            'creator', 'creator_details', 'participant_count'
        ]
        read_only_fields = ['id', 'creator', 'creator_details', 'participant_count']
        
    def get_participant_count(self, obj):
        return obj.participants.count()


class CompetitionDetailSerializer(serializers.ModelSerializer):
    """Serializador para detalle de competencia"""
    
    creator_details = UserSerializer(source='creator', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    categories = CompetitionCategorySerializer(source='competition_categories', many=True, read_only=True)
    judges = CompetitionJudgeSerializer(source='competitionjudge_set', many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'description', 'location', 'start_date', 'end_date', 
            'status', 'status_display', 'is_public', 
            'creator', 'creator_details', 'categories', 'judges', 'participants',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'creator_details', 'created_at', 'updated_at']


class CompetitionCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear competencias"""
    
    class Meta:
        model = Competition
        fields = [
            'name', 'description', 'location', 'start_date', 'end_date', 
            'status', 'is_public'
        ]
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['creator'] = user
        return super().create(validated_data)


class ParticipantAssignmentSerializer(serializers.Serializer):
    """Serializador para asignación de participantes a una competencia"""
    
    rider_id = serializers.IntegerField()
    horse_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    number = serializers.IntegerField(required=False)
    order = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        rider_id = attrs.get('rider_id')
        horse_id = attrs.get('horse_id')
        category_id = attrs.get('category_id')
        
        # Verificar que existan
        from .models import Rider, Horse, Category
        
        try:
            Rider.objects.get(pk=rider_id)
        except Rider.DoesNotExist:
            raise serializers.ValidationError({"rider_id": "Jinete no encontrado"})
            
        try:
            Horse.objects.get(pk=horse_id)
        except Horse.DoesNotExist:
            raise serializers.ValidationError({"horse_id": "Caballo no encontrado"})
            
        try:
            Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"category_id": "Categoría no encontrada"})
            
        return attrs