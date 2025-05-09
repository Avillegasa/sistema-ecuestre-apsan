# backend/evaluaciones/tests.py

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from django.db.models import Max

from usuarios.models import Usuario, Jinete, Juez, Caballo
from competencias.models import Competencia, Categoria, CriterioEvaluacion, Inscripcion
from .models import Evaluacion, Puntuacion
from .utils import calcular_puntaje_evaluacion, verificar_criterios_evaluados

class EvaluacionModelTests(TestCase):
    """
    Pruebas para el modelo Evaluacion.
    """
    
    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios de prueba
        self.usuario_jinete = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete"
        )
        
        self.usuario_juez = Usuario.objects.create_user(
            username="juez_test",
            email="juez@test.com",
            password="password",
            tipo_usuario="juez"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.usuario_jinete,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear juez
        self.juez = Juez.objects.create(
            usuario=self.usuario_juez,
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
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date() + timedelta(days=2),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=10),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=1),
            ubicacion="Ubicación Test",
            estado="en_curso",
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
        
        # Crear inscripción
        self.inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="aprobada",
            numero_participante=1
        )
        
        # Crear evaluación
        self.evaluacion = Evaluacion.objects.create(
            inscripcion=self.inscripcion,
            juez=self.juez,
            estado="pendiente"
        )
    
    def test_calcular_puntaje_total_sin_puntuaciones(self):
        """Probar cálculo de puntaje total sin puntuaciones."""
        puntaje = self.evaluacion.calcular_puntaje_total()
        self.assertIsNone(puntaje)
    
    def test_calcular_puntaje_total_con_puntuaciones(self):
        """Probar cálculo de puntaje total con puntuaciones."""
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
        
        # Calcular puntaje total usando el método del modelo
        puntaje = self.evaluacion.calcular_puntaje_total()
        
        # Cálculo manual para verificar
        puntaje_esperado = (Decimal("8.50") * Decimal("1.5")) + (Decimal("9.00") * Decimal("1.0"))
        puntaje_esperado = puntaje_esperado.quantize(Decimal('0.01'))
        
        self.assertEqual(puntaje, puntaje_esperado)
        self.assertEqual(puntaje, Decimal("21.75"))
    
    def test_actualizar_puntaje_total(self):
        """Probar actualización del puntaje total."""
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
        
        # Actualizar el puntaje total
        self.evaluacion.actualizar_puntaje_total()
        
        # Verificar que se actualizó el campo en la base de datos
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.puntaje_total, Decimal("21.75"))
    
    def test_verificar_completitud(self):
        """Probar verificación de completitud de criterios evaluados."""
        # Inicialmente no hay puntuaciones, por lo que no está completa
        self.assertFalse(self.evaluacion.verificar_completitud())
        
        # Añadir solo una puntuación de los dos criterios
        Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio1,
            valor=Decimal("8.50")
        )
        
        # Todavía no está completa
        self.assertFalse(self.evaluacion.verificar_completitud())
        
        # Añadir la segunda puntuación
        Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio2,
            valor=Decimal("9.00")
        )
        
        # Ahora sí debe estar completa
        self.assertTrue(self.evaluacion.verificar_completitud())

class PuntuacionModelTests(TestCase):
    """
    Pruebas para el modelo Puntuacion.
    """
    
    def setUp(self):
        """Configurar datos de prueba similar a EvaluacionModelTests."""
        # Crear usuarios de prueba
        self.usuario_jinete = Usuario.objects.create_user(
            username="jinete_test",
            email="jinete@test.com",
            password="password",
            tipo_usuario="jinete"
        )
        
        self.usuario_juez = Usuario.objects.create_user(
            username="juez_test",
            email="juez@test.com",
            password="password",
            tipo_usuario="juez"
        )
        
        # Crear jinete
        self.jinete = Jinete.objects.create(
            usuario=self.usuario_jinete,
            documento_identidad="12345678",
            experiencia_anios=5
        )
        
        # Crear juez
        self.juez = Juez.objects.create(
            usuario=self.usuario_juez,
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
            nombre="Competencia Test",
            descripcion="Competencia para pruebas",
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date() + timedelta(days=2),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=10),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=1),
            ubicacion="Ubicación Test",
            estado="en_curso",
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
        
        # Crear criterio de evaluación
        self.criterio = CriterioEvaluacion.objects.create(
            categoria=self.categoria,
            nombre="Técnica",
            descripcion="Evaluación de la técnica",
            puntaje_maximo=Decimal("10.00"),
            peso=Decimal("1.5"),
            orden=1
        )
        
        # Crear inscripción
        self.inscripcion = Inscripcion.objects.create(
            competencia=self.competencia,
            categoria=self.categoria,
            jinete=self.jinete,
            caballo=self.caballo,
            estado="aprobada",
            numero_participante=1
        )
        
        # Crear evaluación
        self.evaluacion = Evaluacion.objects.create(
            inscripcion=self.inscripcion,
            juez=self.juez,
            estado="pendiente"
        )
    
    def test_validacion_puntuacion_maxima(self):
        """Probar validación de que la puntuación no exceda el máximo del criterio."""
        # Crear puntuación con valor mayor al máximo permitido
        with self.assertRaises(Exception):
            Puntuacion.objects.create(
                evaluacion=self.evaluacion,
                criterio=self.criterio,
                valor=Decimal("12.00")  # Mayor que el puntaje_maximo del criterio (10.00)
            )
        
        # Crear puntuación con valor igual al máximo permitido (debe funcionar)
        puntuacion = Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio,
            valor=Decimal("10.00")
        )
        self.assertEqual(puntuacion.valor, Decimal("10.00"))
    
    def test_actualizacion_puntaje_evaluacion(self):
        """Probar que al crear o actualizar una puntuación se actualice el puntaje total de la evaluación."""
        # Verificar que inicialmente la evaluación no tenga puntaje total
        self.assertIsNone(self.evaluacion.puntaje_total)
        
        # Crear puntuación
        puntuacion = Puntuacion.objects.create(
            evaluacion=self.evaluacion,
            criterio=self.criterio,
            valor=Decimal("8.50")
        )
        
        # Verificar que se haya actualizado el puntaje total de la evaluación
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.puntaje_total, Decimal("12.75"))  # 8.50 * 1.5 = 12.75
        
        # Actualizar la puntuación
        puntuacion.valor = Decimal("9.00")
        puntuacion.save()
        
        # Verificar que se haya actualizado nuevamente el puntaje total
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.puntaje_total, Decimal("13.50"))  # 9.00 * 1.5 = 13.50

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
            tipo_usuario="jinete"
        )
        
        self.juez_user = Usuario.objects.create_user(
            username="juez_test",
            email="juez@test.com",
            password="password",
            tipo_usuario="juez"
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
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date() + timedelta(days=2),
            fecha_inicio_inscripciones=timezone.now().date() - timedelta(days=10),
            fecha_fin_inscripciones=timezone.now().date() - timedelta(days=1),
            ubicacion="Ubicación Test",
            estado="en_curso",
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
            estado="aprobada",
            numero_participante=1
        )
        
        # Crear evaluación
        self.evaluacion = Evaluacion.objects.create(
            inscripcion=self.inscripcion,
            juez=self.juez,
            estado="pendiente"
        )
    
    def test_listar_evaluaciones_sin_autenticar(self):
        """Probar que no se pueden ver evaluaciones sin autenticación."""
        url = reverse('evaluacion-list')
        response = self.client.get(url)
        
        # Debe requerir autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_evaluaciones_como_juez(self):
        """Probar listar evaluaciones como juez."""
        url = reverse('evaluacion-list')
        self.client.force_authenticate(user=self.juez_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y la evaluación creada
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_endpoint_mis_evaluaciones(self):
        """Probar el endpoint personalizado para obtener evaluaciones propias de un juez."""
        url = reverse('evaluacion-mis-evaluaciones')
        self.client.force_authenticate(user=self.juez_user)
        response = self.client.get(url)
        
        # Debe devolver éxito y la evaluación asignada
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['juez_nombre'], self.juez.usuario.get_full_name())
    
    def test_crear_puntuacion_como_juez(self):
        """Probar crear puntuación como juez."""
        url = reverse('puntuacion-list')
        self.client.force_authenticate(user=self.juez_user)
        
        data = {
            'evaluacion': self.evaluacion.id,
            'criterio': self.criterio1.id,
            'valor': "8.50",
            'comentario': "Puntuación de prueba"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe crear exitosamente
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Puntuacion.objects.count(), 1)
        
        # Verificar que se haya actualizado el estado de la evaluación
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, "en_progreso")
    
    def test_crear_puntuacion_como_jinete(self):
        """Probar que un jinete no puede crear puntuaciones."""
        url = reverse('puntuacion-list')
        self.client.force_authenticate(user=self.jinete_user)
        
        data = {
            'evaluacion': self.evaluacion.id,
            'criterio': self.criterio1.id,
            'valor': "8.50",
            'comentario': "Puntuación de prueba"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe denegar permiso
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Puntuacion.objects.count(), 0)
    
    def test_endpoint_finalizar_evaluacion(self):
        """Probar el endpoint para finalizar una evaluación."""
        # Crear puntuaciones para los criterios
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
        
        # Actualizar el estado de la evaluación a "en_progreso"
        self.evaluacion.estado = "en_progreso"
        self.evaluacion.save()
        
        # Llamar al endpoint para finalizar la evaluación
        url = reverse('evaluacion-finalizar', args=[self.evaluacion.id])
        self.client.force_authenticate(user=self.juez_user)
        response = self.client.post(url)
        
        # Debe finalizar exitosamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se haya actualizado el estado y la fecha de finalización
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, "completada")
        self.assertIsNotNone(self.evaluacion.fecha_finalizacion)
        self.assertEqual(self.evaluacion.puntaje_total, Decimal("21.75"))
    
    def test_endpoint_puntuar_multiple(self):
        """Probar el endpoint para puntuar múltiples criterios de una vez."""
        url = reverse('puntuacion-puntuar-multiple')
        self.client.force_authenticate(user=self.juez_user)
        
        data = {
            'evaluacion_id': self.evaluacion.id,
            'puntuaciones': [
                {
                    'criterio_id': self.criterio1.id,
                    'valor': 8.50,
                    'comentario': "Puntuación 1"
                },
                {
                    'criterio_id': self.criterio2.id,
                    'valor': 9.00,
                    'comentario': "Puntuación 2"
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debe puntuar exitosamente
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Puntuacion.objects.count(), 2)
        
        # Verificar que se haya calculado el puntaje total correctamente
        self.assertEqual(float(response.data['puntaje_total']), 21.75)
        
        # Verificar que la completitud sea verdadera
        self.assertTrue(response.data['completitud'])
        
        # Verificar que el estado de la evaluación haya cambiado a "en_progreso"
        self.evaluacion.refresh_from_db()
        self.assertEqual(self.evaluacion.estado, "en_progreso")
    
    def test_evaluaciones_por_inscripcion(self):
        """Probar el endpoint para obtener evaluaciones por inscripción."""
        url = f"{reverse('evaluacion-evaluaciones-por-inscripcion')}?inscripcion={self.inscripcion.id}"
        
        # Probar como jinete propietario (debe poder ver)
        self.client.force_authenticate(user=self.jinete_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Probar como juez evaluador (debe poder ver)
        self.client.force_authenticate(user=self.juez_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Crear otro usuario juez que no está asignado a la evaluación
        otro_juez_user = Usuario.objects.create_user(
            username="otro_juez",
            email="otro_juez@test.com",
            password="password",
            tipo_usuario="juez"
        )
        
        otro_juez = Juez.objects.create(
            usuario=otro_juez_user,
            licencia="LIC456",
            especialidad="Salto",
            nivel_certificacion="Regional",
            anios_experiencia=5
        )
        
        # Probar como juez no asignado (no debe poder ver)
        self.client.force_authenticate(user=otro_juez_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)