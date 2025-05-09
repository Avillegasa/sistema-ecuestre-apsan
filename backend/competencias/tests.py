# backend/competencias/tests.py

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from usuarios.models import Usuario, Jinete, Caballo
from .models import Competencia, Categoria, CriterioEvaluacion, Inscripcion

class CompetenciaModelTests(TestCase):
    """
    Pruebas para el modelo Competencia.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear una competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() + timedelta(days=10),
            fecha_fin=timezone.now().date() + timedelta(days=12),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=5),
            fecha_fin_inscripciones=timezone.now().date() + timedelta(days=5),
            ubicacion="Ubicación Test",
            estado="inscripciones_abiertas",
            organizador="Organizador Test"
        )
        
    def test_inscripciones_activas(self):
        """Probar que la función inscripciones_activas devuelve True cuando las inscripciones están abiertas."""
        self.assertTrue(self.competencia.inscripciones_activas())
        
        # Cambiar a estado planificada
        self.competencia.estado = "planificada"
        self.competencia.save()
        self.assertFalse(self.competencia.inscripciones_activas())
        
        # Cambiar a estado en_curso
        self.competencia.estado = "en_curso"
        self.competencia.save()
        self.assertFalse(self.competencia.inscripciones_activas())
        
    def test_str_representation(self):
        """Probar la representación en cadena del modelo."""
        self.assertEqual(
            str(self.competencia), 
            "Competencia Test (Inscripciones Abiertas)"
        )

class CategoriaModelTests(TestCase):
    """
    Pruebas para el modelo Categoria.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear una competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() + timedelta(days=10),
            fecha_fin=timezone.now().date() + timedelta(days=12),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=5),
            fecha_fin_inscripciones=timezone.now().date() + timedelta(days=5),
            ubicacion="Ubicación Test",
            estado="inscripciones_abiertas",
            organizador="Organizador Test"
        )
        
        # Crear una categoría con cupo limitado
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Test",
            descripcion="Categoría para pruebas",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=3,
            precio_inscripcion=Decimal("150.00")
        )
        
        # Crear una categoría con cupo ilimitado
        self.categoria_ilimitada = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Ilimitada",
            descripcion="Categoría sin límite de cupos",
            edad_minima=15,
            edad_maxima=99,
            nivel="Abierto",
            cupo_maximo=0,  # 0 significa ilimitado
            precio_inscripcion=Decimal("100.00")
        )
    
    def test_plazas_disponibles_categoria_limitada(self):
        """Probar plazas disponibles en categoría con cupo limitado."""
        # Inicialmente todas las plazas están disponibles
        self.assertEqual(self.categoria.plazas_disponibles(), 3)
        
        # Crear usuario de prueba (jinete)
        usuario = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete"
        )
        
        # Crear jinete
        jinete = Jinete.objects.create(
            usuario=usuario,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear caballo
        caballo = Caballo.objects.create(
            jinete=jinete,
            nombre="Caballo Test",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),  # ~10 años
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
        
        # Crear una inscripción
        Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=jinete,
            caballo=caballo,
            estado="aprobada"
        )
        
        # Ahora debe haber una plaza menos
        self.assertEqual(self.categoria.plazas_disponibles(), 2)
    
    def test_plazas_disponibles_categoria_ilimitada(self):
        """Probar plazas disponibles en categoría con cupo ilimitado."""
        # En una categoría ilimitada, plazas_disponibles debe devolver None
        self.assertIsNone(self.categoria_ilimitada.plazas_disponibles())

class InscripcionModelTests(TestCase):
    """
    Pruebas para el modelo Inscripcion.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear una competencia
        self.competencia = Competencia.objects.create(
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date() + timedelta(days=10),
            fecha_fin=timezone.now().date() + timedelta(days=12),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=5),
            fecha_fin_inscripciones=timezone.now().date() + timedelta(days=5),
            ubicacion="Ubicación Test",
            estado="inscripciones_abiertas",
            organizador="Organizador Test"
        )
        
        # Crear una categoría
        self.categoria = Categoria.objects.create(
            competencia=self.competencia,
            nombre="Categoría Test",
            descripcion="Categoría para pruebas",
            edad_minima=18,
            edad_maxima=30,
            nivel="Intermedio",
            cupo_maximo=10,
            precio_inscripcion=Decimal("150.00")
        )
        
        # Crear usuario de prueba (jinete)
        self.usuario = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete",
            first_name="Nombre",
            last_name="Apellido"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.usuario,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear caballo
        self.caballo = Caballo.objects.create(
            jinete=self.jinete,
            nombre="Caballo Test",
            raza="Raza Test",
            fecha_nacimiento=timezone.now().date() - timedelta(days=3650),  # ~10 años
            numero_registro="REG123",
            genero="M",
            color="Negro",
            altura=Decimal("1.60")
        )
    
    def test_asignacion_numero_participante(self):
        """Probar que al aprobar una inscripción se asigne un número de participante."""
        # Crear inscripción pendiente
        inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="pendiente"
        )
        
        # Verificar que no tenga número de participante
        self.assertIsNone(inscripcion.numero_participante)
        
        # Aprobar la inscripción
        inscripcion.estado = "aprobada"
        inscripcion.save()
        
        # Verificar que ahora tenga número de participante
        self.assertIsNotNone(inscripcion.numero_participante)
        self.assertEqual(inscripcion.numero_participante, 1)  # Debería ser el primero
        
        # Crear otra inscripción aprobada
        inscripcion2 = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="aprobada"
        )
        
        # Verificar que tenga el siguiente número
        self.assertEqual(inscripcion2.numero_participante, 2)
    
    def test_str_representation(self):
        """Probar la representación en cadena del modelo."""
        inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="pendiente"
        )
        
        self.assertEqual(
            str(inscripcion), 
            "Nombre Apellido - Caballo Test - Categoría Test"
        )

class APITests(TestCase):
    """
    Pruebas para los endpoints de la API.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
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
            tipo_usuario="jinete"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.jinete_user,
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
            nombre="Competencia API Test",
            descripcion="Competencia para pruebas API",
            fecha_inicio=timezone.now().date() + timedelta(days=10),
            fecha_fin=timezone.now().date() + timedelta(days=12),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=5),
            fecha_fin_inscripciones=timezone.now().date() + timedelta(days=5),
            ubicacion="Ubicación Test",
            estado="inscripciones_abiertas",
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
            cupo_maximo=10,
            precio_inscripcion=Decimal("150.00")
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
    
    def test_listar_competencias_sin_autenticar(self):
        """Probar que no se pueden ver competencias sin autenticación."""
        url = reverse('competencia-list')
        response = self.client.get(url)
        
        # Debe requerir autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_competencias_autenticado(self):
        """Probar listar competencias estando autenticado."""
        url = reverse('competencia-list')
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y la competencia creada
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombre'], "Competencia API Test")
    
    def test_crear_competencia_como_admin(self):
        """Probar crear competencia como administrador."""
        url = reverse('competencia-list')
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'nombre': "Nueva Competencia",
            'descripcion': "Descripción de la nueva competencia",
            'fecha_inicio': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'fecha_fin': (timezone.now().date() + timedelta(days=32)).isoformat(),
            'fecha_inicio_inscripciones': (timezone.now().date() + timedelta(days=15)).isoformat(),
            'fecha_fin_inscripciones': (timezone.now().date() + timedelta(days=25)).isoformat(),
            'ubicacion': "Nueva Ubicación",
            'estado': "planificada",
            'organizador': "Nuevo Organizador"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe crear exitosamente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Competencia.objects.count(), 2)
    
    def test_crear_competencia_como_jinete(self):
        """Probar que un jinete no puede crear competencias."""
        url = reverse('competencia-list')
        self.client.force_authenticate(user=self.jinete_user)
        
        data = {
            'nombre': "Nueva Competencia",
            'descripcion': "Descripción de la nueva competencia",
            'fecha_inicio': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'fecha_fin': (timezone.now().date() + timedelta(days=32)).isoformat(),
            'fecha_inicio_inscripciones': (timezone.now().date() + timedelta(days=15)).isoformat(),
            'fecha_fin_inscripciones': (timezone.now().date() + timedelta(days=25)).isoformat(),
            'ubicacion': "Nueva Ubicación",
            'estado': "planificada",
            'organizador': "Nuevo Organizador"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe denegar permiso
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_inscribirse_como_jinete(self):
        """Probar que un jinete puede crear una inscripción."""
        url = reverse('inscripcion-list')
        self.client.force_authenticate(user=self.jinete_user)
        
        data = {
            'competencia': self.competencia.id,
            'categoria': self.categoria.id,
            'caballo': self.caballo.id,
            'comentarios': "Inscripción de prueba"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe crear exitosamente y asignar automáticamente el jinete
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscripcion.objects.count(), 1)
        inscripcion = Inscripcion.objects.first()
        self.assertEqual(inscripcion.jinete, self.jinete)
    
    def test_endpoint_mis_inscripciones(self):
        """Probar el endpoint personalizado para obtener inscripciones propias."""
        # Crear una inscripción para el jinete
        inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="pendiente"
        )
        
        url = reverse('inscripcion-mis-inscripciones')
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y la inscripción creada
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], inscripcion.id)