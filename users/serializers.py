from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, JudgeProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializador para el modelo User"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_judge', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class JudgeProfileSerializer(serializers.ModelSerializer):
    """Serializador para el modelo JudgeProfile"""
    
    class Meta:
        model = JudgeProfile
        fields = ['id', 'user', 'specialty', 'bio', 'contact_phone']
        read_only_fields = ['id', 'user']


class JudgeDetailSerializer(serializers.ModelSerializer):
    """Serializador para detalles de un juez incluyendo su perfil"""
    
    profile = JudgeProfileSerializer(source='judge_profile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 
                  'is_judge', 'judge_level', 'judge_license', 'profile']
        read_only_fields = ['id', 'email', 'role', 'is_judge']


class LoginSerializer(serializers.Serializer):
    """Serializador para el login de usuarios"""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                               username=email, password=password)
            
            if not user:
                msg = 'No se pudo iniciar sesión con las credenciales proporcionadas.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = 'Esta cuenta ha sido desactivada.'
                raise serializers.ValidationError(msg, code='authorization')
            
        else:
            msg = 'Debe incluir "email" y "password".'
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializador para el registro de nuevos usuarios"""
    
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'role']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden"})
        
        # Si role es 'admin', verificar si el usuario tiene permisos
        if attrs.get('role') == 'admin':
            request = self.context.get('request')
            if not request or not request.user.is_authenticated or not request.user.role == 'admin':
                raise serializers.ValidationError({"role": "No tiene permisos para crear administradores"})
        
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # Si el usuario es juez, crear perfil de juez
        if user.role == 'judge':
            JudgeProfile.objects.create(user=user)
            
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializador para cambio de contraseña"""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, min_length=8, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "Las nuevas contraseñas no coinciden"})
        return attrs