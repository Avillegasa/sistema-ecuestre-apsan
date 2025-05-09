# backend/usuarios/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Jinete, Juez, Entrenador, Caballo

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario con campos básicos.
    """
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'tipo_usuario', 'telefono', 'direccion', 'fecha_nacimiento', 
                 'foto_perfil', 'is_active']
        read_only_fields = ['is_active']

class UsuarioDetailSerializer(UsuarioSerializer):
    """
    Serializer detallado para el modelo Usuario que incluye el perfil específico.
    """
    perfil = serializers.SerializerMethodField()
    
    class Meta(UsuarioSerializer.Meta):
        fields = UsuarioSerializer.Meta.fields + ['perfil']
    
    def get_perfil(self, obj):
        """
        Obtiene el perfil específico según el tipo de usuario.
        """
        if obj.tipo_usuario == 'jinete' and hasattr(obj, 'jinete'):
            return JineteSerializer(obj.jinete).data
        elif obj.tipo_usuario == 'juez' and hasattr(obj, 'juez'):
            return JuezSerializer(obj.juez).data
        elif obj.tipo_usuario == 'entrenador' and hasattr(obj, 'entrenador'):
            return EntrenadorSerializer(obj.entrenador).data
        return None

class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios con validación de contraseña.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'password2', 'first_name', 
                 'last_name', 'tipo_usuario', 'telefono', 'direccion', 
                 'fecha_nacimiento', 'foto_perfil']
    
    def validate(self, data):
        """
        Validar que las contraseñas coincidan.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data
    
    def create(self, validated_data):
        """
        Crear un nuevo usuario con la contraseña encriptada.
        """
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = Usuario.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class JineteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Jinete.
    """
    class Meta:
        model = Jinete
        fields = ['id', 'documento_identidad', 'experiencia_anios', 
                 'categoria_habitual', 'federado', 'numero_licencia', 
                 'entrenador']

class JineteDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Jinete que incluye información del usuario.
    """
    usuario = UsuarioSerializer(read_only=True)
    entrenador_details = serializers.SerializerMethodField()
    caballos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Jinete
        fields = ['id', 'usuario', 'documento_identidad', 'experiencia_anios', 
                 'categoria_habitual', 'federado', 'numero_licencia', 
                 'entrenador', 'entrenador_details', 'caballos_count']
    
    def get_entrenador_details(self, obj):
        """
        Obtiene detalles del entrenador si existe.
        """
        if obj.entrenador:
            return {
                'id': obj.entrenador.id,
                'nombre': obj.entrenador.usuario.get_full_name(),
                'especialidad': obj.entrenador.especialidad
            }
        return None
    
    def get_caballos_count(self, obj):
        """
        Obtiene la cantidad de caballos asociados al jinete.
        """
        return obj.caballos.count()

class JuezSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Juez.
    """
    class Meta:
        model = Juez
        fields = ['id', 'licencia', 'especialidad', 'nivel_certificacion', 
                 'anios_experiencia', 'federacion']

class JuezDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Juez que incluye información del usuario.
    """
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Juez
        fields = ['id', 'usuario', 'licencia', 'especialidad', 'nivel_certificacion', 
                 'anios_experiencia', 'federacion']

class EntrenadorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Entrenador.
    """
    class Meta:
        model = Entrenador
        fields = ['id', 'especialidad', 'licencia', 'anios_experiencia', 
                 'certificaciones']

class EntrenadorDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Entrenador que incluye información del usuario
    y los jinetes asignados.
    """
    usuario = UsuarioSerializer(read_only=True)
    jinetes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Entrenador
        fields = ['id', 'usuario', 'especialidad', 'licencia', 'anios_experiencia', 
                 'certificaciones', 'jinetes_count']
    
    def get_jinetes_count(self, obj):
        """
        Obtiene la cantidad de jinetes asignados al entrenador.
        """
        return obj.jinetes.count()

class CaballoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Caballo.
    """
    class Meta:
        model = Caballo
        fields = ['id', 'jinete', 'nombre', 'raza', 'fecha_nacimiento', 
                 'numero_registro', 'genero', 'color', 'altura', 'peso', 
                 'estado_salud', 'historial_competencias', 'foto', 
                 'fecha_registro']
        read_only_fields = ['fecha_registro']

class CaballoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Caballo que incluye información del jinete.
    """
    jinete_details = serializers.SerializerMethodField()
    edad = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Caballo
        fields = ['id', 'jinete', 'jinete_details', 'nombre', 'raza', 
                 'fecha_nacimiento', 'edad', 'numero_registro', 'genero', 
                 'color', 'altura', 'peso', 'estado_salud', 
                 'historial_competencias', 'foto', 'fecha_registro']
        read_only_fields = ['fecha_registro', 'edad']
    
    def get_jinete_details(self, obj):
        """
        Obtiene detalles básicos del jinete.
        """
        return {
            'id': obj.jinete.id,
            'nombre': obj.jinete.usuario.get_full_name(),
            'categoria': obj.jinete.categoria_habitual
        }