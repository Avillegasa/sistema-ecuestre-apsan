# backend/rankings/views.py

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from usuarios.permissions import IsAdminUser
from competencias.models import Competencia, Categoria, Inscripcion
from .models import Ranking, ResultadoRanking, Certificado
from .serializers import (
    RankingSerializer, RankingDetailSerializer,
    ResultadoRankingSerializer, ResultadoRankingDetailSerializer,
    CertificadoSerializer, CertificadoDetailSerializer
)

class RankingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Ranking.
    """
    queryset = Ranking.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competencia', 'categoria', 'tipo', 'publicado']
    search_fields = ['competencia__nombre', 'categoria__nombre', 'descripcion']
    ordering_fields = ['fecha_generacion', 'fecha_publicacion']
    ordering = ['-fecha_generacion']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'resultados':
            return RankingDetailSerializer
        return RankingSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar rankings
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'generar', 'publicar']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def generar(self, request, pk=None):
        """
        Endpoint para generar los resultados del ranking.
        """
        ranking = self.get_object()
        
        if ranking.publicado:
            return Response(
                {"detail": "No se pueden regenerar resultados de un ranking ya publicado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que haya inscripciones con evaluaciones completas
        inscripciones_evaluadas = Inscripcion.objects.filter(
            competencia=ranking.competencia,
            categoria=ranking.categoria,
            estado='completada',
            evaluaciones__estado='completada'
        ).distinct().count()
        
        if inscripciones_evaluadas == 0:
            return Response(
                {"detail": "No hay inscripciones con evaluaciones completas para generar el ranking."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar resultados
        ranking.generar_resultados()
        
        serializer = RankingDetailSerializer(ranking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        """
        Endpoint para publicar el ranking.
        """
        ranking = self.get_object()
        
        if ranking.publicado:
            return Response(
                {"detail": "El ranking ya está publicado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que tenga resultados generados
        if not ranking.resultados.exists():
            return Response(
                {"detail": "Primero debes generar los resultados del ranking antes de publicarlo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Publicar ranking
        ranking.publicar()
        
        serializer = RankingDetailSerializer(ranking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        """
        Endpoint para obtener los resultados de un ranking específico.
        """
        ranking = self.get_object()
        resultados = ranking.resultados.all().order_by('posicion')
        serializer = ResultadoRankingDetailSerializer(resultados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_competencia(self, request):
        """
        Endpoint para obtener los rankings de una competencia específica.
        """
        competencia_id = request.query_params.get('competencia_id', None)
        if not competencia_id:
            return Response(
                {"detail": "Se requiere el parámetro 'competencia_id'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            competencia = Competencia.objects.get(pk=competencia_id)
        except Competencia.DoesNotExist:
            return Response(
                {"detail": "Competencia no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Por defecto mostrar solo rankings publicados, a menos que sea admin
        if request.user.tipo_usuario == 'admin':
            rankings = Ranking.objects.filter(competencia=competencia)
        else:
            rankings = Ranking.objects.filter(competencia=competencia, publicado=True)
        
        # Filtrar por categoría si se proporciona
        categoria_id = request.query_params.get('categoria_id', None)
        if categoria_id:
            rankings = rankings.filter(categoria_id=categoria_id)
        
        # Filtrar por tipo si se proporciona
        tipo = request.query_params.get('tipo', None)
        if tipo:
            rankings = rankings.filter(tipo=tipo)
        
        serializer = self.get_serializer(rankings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_resultados(self, request):
        """
        Endpoint para que un jinete obtenga sus propios resultados en rankings.
        """
        user = request.user
        if user.tipo_usuario != 'jinete' or not hasattr(user, 'jinete'):
            return Response(
                {"detail": "Solo los jinetes pueden acceder a este endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener resultados donde el jinete ha participado
        resultados = ResultadoRanking.objects.filter(
            inscripcion__jinete=user.jinete,
            ranking__publicado=True
        ).select_related('ranking', 'inscripcion', 'inscripcion__caballo')
        
        # Filtrar por competencia si se proporciona
        competencia_id = request.query_params.get('competencia_id', None)
        if competencia_id:
            resultados = resultados.filter(ranking__competencia_id=competencia_id)
        
        # Filtrar por tipo de ranking si se proporciona
        tipo = request.query_params.get('tipo', None)
        if tipo:
            resultados = resultados.filter(ranking__tipo=tipo)
        
        serializer = ResultadoRankingDetailSerializer(resultados, many=True)
        return Response(serializer.data)

class ResultadoRankingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo ResultadoRanking.
    """
    queryset = ResultadoRanking.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ranking', 'inscripcion', 'ranking__competencia', 'ranking__categoria', 'medalla']
    ordering_fields = ['posicion', 'puntaje']
    ordering = ['posicion']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'certificado':
            return ResultadoRankingDetailSerializer
        return ResultadoRankingSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar resultados
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def certificado(self, request, pk=None):
        """
        Endpoint para obtener el certificado asociado a un resultado específico.
        """
        resultado = self.get_object()
        
        if not hasattr(resultado, 'certificado'):
            return Response(
                {"detail": "No hay certificado generado para este resultado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CertificadoDetailSerializer(resultado.certificado)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generar_certificado(self, request, pk=None):
        """
        Endpoint para generar un certificado para un resultado específico.
        """
        resultado = self.get_object()
        
        # Verificar si ya existe un certificado
        if hasattr(resultado, 'certificado'):
            return Response(
                {"detail": "Ya existe un certificado para este resultado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el ranking esté publicado
        if not resultado.ranking.publicado:
            return Response(
                {"detail": "No se pueden generar certificados para resultados de rankings no publicados."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determinar tipo de certificado basado en la posición
        tipo = 'premiacion' if resultado.posicion <= 3 else 'participacion'
        
        # Crear certificado
        certificado = Certificado.objects.create(
            resultado=resultado,
            tipo=tipo
        )
        
        # Generar archivo PDF
        certificado.generar_pdf()
        
        serializer = CertificadoDetailSerializer(certificado)
        return Response(serializer.data)

class CertificadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Certificado.
    """
    queryset = Certificado.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'resultado__ranking__competencia', 'resultado__ranking__categoria']
    search_fields = ['codigo', 'resultado__inscripcion__jinete__usuario__first_name', 'resultado__inscripcion__jinete__usuario__last_name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'verificar':
            return CertificadoDetailSerializer
        return CertificadoSerializer
    
    def get_permissions(self):
        """
        Permisos basados en la acción:
        - Admin para crear, actualizar o eliminar certificados
        - Permisos específicos para verificar
        - Usuario autenticado para otras operaciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action == 'verificar':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def verificar(self, request):
        """
        Endpoint público para verificar la autenticidad de un certificado mediante su código.
        """
        codigo = request.query_params.get('codigo', None)
        if not codigo:
            return Response(
                {"detail": "Se requiere el parámetro 'codigo'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            certificado = Certificado.objects.get(codigo=codigo)
        except Certificado.DoesNotExist:
            return Response(
                {"verificacion": False, "detail": "Certificado no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CertificadoDetailSerializer(certificado)
        return Response({
            "verificacion": True,
            "mensaje": "Certificado verificado correctamente.",
            "certificado": serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mis_certificados(self, request):
        """
        Endpoint para que un jinete obtenga sus propios certificados.
        """
        user = request.user
        if user.tipo_usuario != 'jinete' or not hasattr(user, 'jinete'):
            return Response(
                {"detail": "Solo los jinetes pueden acceder a este endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        certificados = Certificado.objects.filter(
            resultado__inscripcion__jinete=user.jinete
        ).select_related('resultado', 'resultado__ranking', 'resultado__inscripcion')
        
        # Filtrar por tipo si se proporciona
        tipo = request.query_params.get('tipo', None)
        if tipo:
            certificados = certificados.filter(tipo=tipo)
        
        # Filtrar por competencia si se proporciona
        competencia_id = request.query_params.get('competencia_id', None)
        if competencia_id:
            certificados = certificados.filter(resultado__ranking__competencia_id=competencia_id)
        
        serializer = CertificadoDetailSerializer(certificados, many=True)
        return Response(serializer.data)