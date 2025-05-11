from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import User, JudgeProfile
from .serializers import (
    UserSerializer, JudgeProfileSerializer, JudgeDetailSerializer,
    LoginSerializer, RegistrationSerializer, ChangePasswordSerializer
)


class LoginView(APIView):
    """Vista para iniciar sesión"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """Vista para cerrar sesión"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Eliminar token
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        # Cerrar sesión de Django
        logout(request)
        
        return Response({"detail": "Sesión cerrada correctamente"})


class RegistrationView(APIView):
    """Vista para registrar nuevos usuarios"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Solo admins pueden registrar otros admins o jueces
        if request.data.get('role') in ['admin', 'judge']:
            if not request.user.is_authenticated or request.user.role != 'admin':
                return Response(
                    {"error": "No tiene permisos para registrar administradores o jueces"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = RegistrationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Crear token para el nuevo usuario
        token = Token.objects.create(user=user)
        
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Vista para ver y actualizar los detalles del usuario actual"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """Vista para listar usuarios (solo admin)"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        # Filtrar por rol si se especifica
        role = self.request.query_params.get('role')
        queryset = User.objects.all()
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset


class JudgeListView(generics.ListAPIView):
    """Vista para listar jueces"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(is_judge=True)


class JudgeDetailView(generics.RetrieveAPIView):
    """Vista para ver los detalles de un juez"""
    
    queryset = User.objects.filter(is_judge=True)
    serializer_class = JudgeDetailSerializer
    permission_classes = [IsAuthenticated]


class ChangePasswordView(APIView):
    """Vista para cambiar la contraseña"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verificar contraseña actual
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Contraseña actual incorrecta"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar contraseña
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Actualizar token
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                "detail": "Contraseña cambiada correctamente",
                "token": token.key
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Obtener perfil del usuario actual"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)