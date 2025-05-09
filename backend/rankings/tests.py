# backend/rankings/tests.py

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
import uuid

from usuarios.models import Usuario, Jinete, Juez, Caballo
from competencias.models import Competencia, Categoria, CriterioEvaluacion, Inscripcion
from evaluaciones.models import Evaluacion, Puntuacion
from .models import Ranking, ResultadoRanking, Certificado

class RankingModelTests(TestCase):
    """
    Pruebas para el modelo Ranking.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios de prueba
        self.usuario_jinete1 = Usuario.objects.create_user(
            username="jinete1",
            email="jinete1@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Jinete",
            last_name="Uno"
        )
        
        self.usuario_jinete2 = Usuario.objects.create_user(
            username="jinete2",
            email="jinete2@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Jinete",
            last_name="Dos"
        )
        
        self.usuario_juez = Usuario.objects.create_user(
            username="juez_test",
            email="juez@test.com",
            password="password",
            tipo_usuario="juez",
            first_name="Juez",
            last_name="Test"
        )
        
        # Crear perfiles
        self.jinete1 = Jinete.objects.create(
            usuario=self.usuario_jinete1,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        self.jinete2 = Jinete.objects.create(
            usuario=self.usuario_jinete2,
            documento_identidad="87654321",
            experiencia_anios=3
        )
        
        self.juez = Juez.objects.create(
            usuario=self.usuario_juez,
            licencia="LIC123",
            especialidad="Doma Clásica",
            nivel_certificacion="Nacional",
            anios_experiencia=10
        )
        
        # Crear caballos
        self.caballo1 = Caballo.objects.create(
            jinete=self.jinete1,
            nombre="Caballo Uno",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
        
        self.caballo2 = Caballo.objects.create(
            jinete=self.jinete2,
            nombre="Caballo Dos",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=2920),
            numero_registro="REG456",
            genero="H",
            color="Blanco",
            altura=Decimal("1.55")
        )
        
        # Crear competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() - timedelta(days=5),
            fecha_fin=timezone.now().date() - timedelta(days=3),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=20),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=10),
            ubicacion="Ubicación Test",
            estado="finalizada",
            organizador="Organizador Test"
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Test",
            descripcion="Categoría para pruebas",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=10
        )
        
        # Crear criterios de evaluación
        self.criterio1 = CriterioEvaluacion.objects.create(
            categoria=self.categoria,
            nombre="Técnica",
            descripcion="Evaluación de la técnica",
            puntaje_maximo=Decimal("10.00"),
            peso=Decimal("1.5"),
            orden=1
        )
        
        self.criterio2 = CriterioEvaluacion.objects.create(
            categoria=self.categoria,
            nombre="Estilo",
            descripcion="Evaluación del estilo",
            puntaje_maximo=Decimal("10.00"),
            peso=Decimal("1.0"),
            orden=2
        )
        
        # Crear inscripciones
        self.inscripcion1 = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete1,
            caballo=self.caballo1,
            estado="completada",
            numero_participante=1
        )
        
        self.inscripcion2 = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete2,
            caballo=self.caballo2,
            estado="completada",
            numero_participante=2
        )
        
        # Crear evaluaciones
        self.evaluacion1 = Evaluacion.objects.create(
            inscripcion=self.inscripcion1,
            juez=self.juez,
            estado="completada",
            fecha_inicio=timezone.now() - timedelta(days=4),
            fecha_finalizacion=timezone.now() - timedelta(days=4),
            puntaje_total=Decimal("21.75")
        )
        
        self.evaluacion2 = Evaluacion.objects.create(
            inscripcion=self.inscripcion2,
            juez=self.juez,
            estado="completada",
            fecha_inicio=timezone.now() - timedelta(days=4),
            fecha_finalizacion=timezone.now() - timedelta(days=4),
            puntaje_total=Decimal("19.50")
        )
        
        # Crear puntuaciones para evaluación 1
        Puntuacion.objects.create(
            evaluacion=self.evaluacion1,
            criterio=self.criterio1,
            valor=Decimal("8.50")
        )
        
        Puntuacion.objects.create(
            evaluacion=self.evaluacion1,
            criterio=self.criterio2,
            valor=Decimal("9.00")
        )
        
        # Crear puntuaciones para evaluación 2
        Puntuacion.objects.create(
            evaluacion=self.evaluacion2,
            criterio=self.criterio1,
            valor=Decimal("7.00")
        )
        
        Puntuacion.objects.create(
            evaluacion=self.evaluacion2,
            criterio=self.criterio2,
            valor=Decimal("9.00")
        )
        
        # Crear ranking
        self.ranking = Ranking.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            tipo="preliminar",
            descripcion="Ranking preliminar para pruebas"
        )
    
    def test_generar_resultados(self):
        """Probar la generación de resultados del ranking."""
        # Inicialmente no hay resultados
        self.assertEqual(self.ranking.resultados.count(), 0)
        
        # Generar resultados
        self.ranking.generar_resultados()
        
        # Verificar que se hayan generado resultados
        self.assertEqual(self.ranking.resultados.count(), 2)
        
        # Verificar que los resultados estén ordenados por puntaje (descendente)
        resultados = self.ranking.resultados.all().order_by('posicion')
        
        # El primer resultado debe corresponder a la inscripción 1 (mayor puntaje)
        self.assertEqual(resultados[0].inscripcion.id, self.inscripcion1.id)
        self.assertEqual(resultados[0].posicion, 1)
        self.assertEqual(resultados[0].puntaje, Decimal("21.75"))
        
        # El segundo resultado debe corresponder a la inscripción 2 (menor puntaje)
        self.assertEqual(resultados[1].inscripcion.id, self.inscripcion2.id)
        self.assertEqual(resultados[1].posicion, 2)
        self.assertEqual(resultados[1].puntaje, Decimal("19.50"))
    
    def test_publicar_ranking(self):
        """Probar la publicación de un ranking."""
        # Inicialmente el ranking no está publicado
        self.assertFalse(self.ranking.publicado)
        self.assertIsNone(self.ranking.fecha_publicacion)
        
        # Generar resultados primero
        self.ranking.generar_resultados()
        
        # Publicar el ranking
        self.ranking.publicar()
        
        # Verificar que el ranking ahora esté publicado
        self.assertTrue(self.ranking.publicado)
        self.assertIsNotNone(self.ranking.fecha_publicacion)

class ResultadoRankingModelTests(TestCase):
    """
    Pruebas para el modelo ResultadoRanking.
    """
    
    def setUp(self):
        """Configurar datos de prueba similar a RankingModelTests."""
        # Crear usuario jinete
        self.usuario_jinete = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Jinete",
            last_name="Test"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.usuario_jinete,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear caballo
        self.caballo = Caballo.objects.create(
            jinete=self.jinete,
            nombre="Caballo Test",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
        
        # Crear competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() - timedelta(days=5),
            fecha_fin=timezone.now().date() - timedelta(days=3),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=20),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=10),
            ubicacion="Ubicación Test",
            estado="finalizada",
            organizador="Organizador Test"
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Test",
            descripcion="Categoría para pruebas",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=10
        )
        
        # Crear inscripción
        self.inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="completada",
            numero_participante=1
        )
        
        # Crear ranking
        self.ranking = Ranking.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            tipo="final",
            publicado=True,
            fecha_publicacion=timezone.now()
        )
        
        # Crear resultado
        self.resultado = ResultadoRanking.objects.create(
            ranking=self.ranking,
            inscripcion=self.inscripcion,
            posicion=1,
            puntaje=Decimal("21.75"),
            medalla="oro",
            comentario="Excelente presentación"
        )
    
    def test_str_representation(self):
        """Probar la representación en cadena del modelo."""
        expected_str = f"1° lugar - {self.jinete.usuario.get_full_name()} con {self.caballo.nombre}"
        self.assertEqual(str(self.resultado), expected_str)

class CertificadoModelTests(TestCase):
    """
    Pruebas para el modelo Certificado.
    """
    
    def setUp(self):
        """Configurar datos de prueba similar a ResultadoRankingModelTests."""
        # Crear usuario jinete
        self.usuario_jinete = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Jinete",
            last_name="Test"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.usuario_jinete,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear caballo
        self.caballo = Caballo.objects.create(
            jinete=self.jinete,
            nombre="Caballo Test",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
        
        # Crear competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() - timedelta(days=5),
            fecha_fin=timezone.now().date() - timedelta(days=3),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=20),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=10),
            ubicacion="Ubicación Test",
            estado="finalizada",
            organizador="Organizador Test"
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Test",
            descripcion="Categoría para pruebas",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=10
        )
        
        # Crear inscripción
        self.inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="completada",
            numero_participante=1
        )
        
        # Crear ranking
        self.ranking = Ranking.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            tipo="final",
            publicado=True,
            fecha_publicacion=timezone.now()
        )
        
        # Crear resultado
        self.resultado = ResultadoRanking.objects.create(
            ranking=self.ranking,
            inscripcion=self.inscripcion,
            posicion=1,
            puntaje=Decimal("21.75"),
            medalla="oro"
        )
        
        # Crear certificado
        self.certificado = Certificado.objects.create(
            resultado=self.resultado,
            tipo="premiacion",
            codigo="ABCDEF1234"
        )
    
    def test_generacion_codigo_automatico(self):
        """Probar la generación automática de código si no se proporciona uno."""
        # Crear otro certificado sin especificar código
        certificado = Certificado.objects.create(
            resultado=self.resultado,
            tipo="participacion"
        )
        
        # Verificar que se haya generado un código automáticamente
        self.assertIsNotNone(certificado.codigo)
        self.assertEqual(len(certificado.codigo), 10)  # UUID hex[:10]
        self.assertNotEqual(certificado.codigo, self.certificado.codigo)  # Debe ser diferente
    
    def test_str_representation(self):
        """Probar la representación en cadena del modelo."""
        expected_str = f"Certificado de Premiación - {self.jinete.usuario.get_full_name()}"
        self.assertEqual(str(self.certificado), expected_str)

class APITests(TestCase):
    """
    Pruebas para los endpoints de la API.
    """
    
    def setUp(self):
        """Configurar datos de prueba y cliente API."""
        # Crear cliente API
        self.client = APIClient()
        
        # Crear usuarios
        self.admin_user = Usuario.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="password",
            tipo_usuario="admin",
            is_staff=True,
            is_superuser=True
        )
        
        self.jinete_user = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Jinete",
            last_name="Test"
        )
        
        self.juez_user = Usuario.objects.create_user(
            username="juez_test",
            email="juez@test.com",
            password="password",
            tipo_usuario="juez",
            first_name="Juez",
            last_name="Test"
        )
        
        # Crear perfiles
        self.jinete = Jinete.objects.create(
            usuario=self.jinete_user,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        self.juez = Juez.objects.create(
            usuario=self.juez_user,
            licencia="LIC123",
            especialidad="Doma Clásica",
            nivel_certificacion="Nacional",
            anios_experiencia=10
        )
        
        # Crear caballo
        self.caballo = Caballo.objects.create(
            jinete=self.jinete,
            nombre="Caballo Test",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
        
        # Crear competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia API Test",
            descripcion="Competencia para pruebas API",
            fecha_inicio=timezone.now().date() - timedelta(days=5),
            fecha_fin=timezone.now().date() - timedelta(days=3),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=20),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=10),
            ubicacion="Ubicación Test",
            estado="finalizada",
            organizador="Organizador Test"
        )
        
        # Crear categoría
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría API Test",
            descripcion="Categoría para pruebas API",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=10
        )
        
        # Crear criterios de evaluación
        self.criterio1 = CriterioEvaluacion.objects.create(
            categoria=self.categoria,
            nombre="Técnica",
            descripcion="Evaluación de la técnica",
            puntaje_maximo=Decimal("10.00"),
            peso=Decimal("1.5"),
            orden=1
        )
        
        self.criterio2 = CriterioEvaluacion.objects.create(
            categoria=self.categoria,
            nombre="Estilo",
            descripcion="Evaluación del estilo",
            puntaje_maximo=Decimal("10.00"),
            peso=Decimal("1.0"),
            orden=2
        )
        
        # Crear inscripción
        self.inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="completada",
            numero_participante=1
        )
        
        # Crear evaluación
        self.evaluacion = Evaluacion.objects.create(
            inscripcion=self.inscripcion,
            juez=self.juez,
            estado="completada",
            fecha_inicio=timezone.now() - timedelta(days=4),
            fecha_finalizacion=timezone.now() - timedelta(days=4),
            puntaje_total=Decimal("21.75")
        )
        
        # Crear puntuaciones
        Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio1,
            valor=Decimal("8.50")
        )
        
        Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio2,
            valor=Decimal("9.00")
        )
        
        # Crear ranking
        self.ranking = Ranking.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            tipo="preliminar",
            descripcion="Ranking preliminar para pruebas API"
        )
    
    def test_listar_rankings_sin_autenticar(self):
        """Probar que no se pueden ver rankings sin autenticación."""
        url = reverse('ranking-list')
        response = self.client.get(url)
        
        # Debe requerir autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_rankings_como_jinete(self):
        """Probar listar rankings como jinete."""
        url = reverse('ranking-list')
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y el ranking creado
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['tipo'], 'preliminar')
    
    def test_endpoint_generar_resultados(self):
        """Probar el endpoint para generar resultados de un ranking."""
        url = reverse('ranking-generar', args=[self.ranking.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url)
        
        # Debe generar exitosamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se hayan generado resultados
        self.ranking.refresh_from_db()
        self.assertEqual(self.ranking.resultados.count(), 1)
        
        # Verificar que el resultado corresponda a la inscripción
        resultado = self.ranking.resultados.first()
        self.assertEqual(resultado.inscripcion.id, self.inscripcion.id)
        self.assertEqual(resultado.posicion, 1)
        self.assertEqual(resultado.puntaje, Decimal("21.75"))
    
    def test_endpoint_publicar_ranking(self):
        """Probar el endpoint para publicar un ranking."""
        # Primero generar resultados
        self.ranking.generar_resultados()
        
        url = reverse('ranking-publicar', args=[self.ranking.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url)
        
        # Debe publicar exitosamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el ranking ahora esté publicado
        self.ranking.refresh_from_db()
        self.assertTrue(self.ranking.publicado)
        self.assertIsNotNone(self.ranking.fecha_publicacion)
    
    def test_endpoint_resultados(self):
        """Probar el endpoint para obtener los resultados de un ranking."""
        # Generar resultados primero
        self.ranking.generar_resultados()
        
        url = reverse('ranking-resultados', args=[self.ranking.id])
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y el resultado generado
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['inscripcion'], self.inscripcion.id)
        self.assertEqual(response.data[0]['posicion'], 1)
    
    def test_endpoint_mis_resultados(self):
        """Probar el endpoint para obtener resultados propios de un jinete."""
        # Generar resultados y publicar el ranking
        self.ranking.generar_resultados()
        self.ranking.publicar()
        
        url = reverse('ranking-mis-resultados')
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y el resultado del jinete
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Verificar que el resultado corresponda a la inscripción del jinete
        self.assertEqual(response.data[0]['inscripcion_details']['jinete']['nombre'], self.jinete.usuario.get_full_name())
    
    def test_endpoint_generar_certificado(self):
        """Probar el endpoint para generar un certificado para un resultado."""
        # Generar resultados y publicar el ranking
        self.ranking.generar_resultados()
        self.ranking.publicar()
        
        # Obtener el resultado generado
        resultado = self.ranking.resultados.first()
        
        url = reverse('resultado-ranking-generar-certificado', args=[resultado.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url)
        
        # Debe generar exitosamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se haya creado el certificado
        self.assertTrue(hasattr(resultado, 'certificado'))
        
        # Verificar que el certificado tenga los datos correctos
        certificado = resultado.certificado
        self.assertEqual(certificado.tipo, 'premiacion')  # Premiación por ser primer lugar
        self.assertIsNotNone(certificado.codigo)
    
    def test_endpoint_verificar_certificado(self):
        """Probar el endpoint para verificar un certificado mediante su código."""
        # Generar resultados y publicar el ranking
        self.ranking.generar_resultados()
        self.ranking.publicar()
        
        # Obtener el resultado generado
        resultado = self.ranking.resultados.first()
        
        # Crear certificado
        certificado = Certificado.objects.create(
            resultado=resultado,
            tipo="premiacion",
            codigo="TESTCODE123"
        )
        
        url = f"{reverse('certificado-verificar')}?codigo=TESTCODE123"
        response = self.client.get(url)  # Sin autenticación
        
        # Debe verificar exitosamente (es un endpoint público)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['verificacion'])
        
        # Verificar que los datos del certificado sean correctos
        self.assertEqual(response.data['certificado']['codigo'], "TESTCODE123")
        
        # Probar con un código inexistente
        url = f"{reverse('certificado-verificar')}?codigo=NOEXISTE"
        response = self.client.get(url)
        
        # Debe devolver que el certificado no existe
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['verificacion'])