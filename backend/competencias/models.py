# backend/competencias/models.py

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from usuarios.models import Jinete, Juez, Caballo

class Competencia(models.Model):
    """
    Modelo para almacenar información de las competencias ecuestres.
    """
    ESTADO_CHOICES = [
        ('planificada', 'Planificada'),
        ('inscripciones_abiertas', 'Inscripciones Abiertas'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Finalización")
    fecha_inicio_inscripciones = models.DateField(verbose_name="Inicio de Inscripciones")
    fecha_fin_inscripciones = models.DateField(verbose_name="Fin de Inscripciones")
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación")
    estado = models.CharField(
        max_length=30, 
        choices=ESTADO_CHOICES, 
        default='planificada',
        verbose_name="Estado"
    )
    imagen = models.ImageField(
        upload_to='competencias/', 
        blank=True, 
        null=True,
        verbose_name="Imagen"
    )
    organizador = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Organizador"
    )
    contacto_email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Email de Contacto"
    )
    contacto_telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Teléfono de Contacto"
    )
    reglamento = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Reglamento"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Competencia"
        verbose_name_plural = "Competencias"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"
    
    def inscripciones_activas(self):
        """Determina si las inscripciones están activas."""
        today = timezone.now().date()
        return (self.fecha_inicio_inscripciones <= today <= self.fecha_fin_inscripciones and
                self.estado == 'inscripciones_abiertas')

class Categoria(models.Model):
    """
    Modelo para las categorías de una competencia.
    """
    competencia = models.ForeignKey(
        Competencia, 
        on_delete=models.CASCADE, 
        related_name='categorias',
        verbose_name="Competencia"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    edad_minima = models.PositiveIntegerField(
        default=0,
        verbose_name="Edad Mínima del Jinete"
    )
    edad_maxima = models.PositiveIntegerField(
        default=99,
        verbose_name="Edad Máxima del Jinete"
    )
    nivel = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Nivel"
    )
    cupo_maximo = models.PositiveIntegerField(
        default=0,
        verbose_name="Cupo Máximo (0 = ilimitado)"
    )
    precio_inscripcion = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name="Precio de Inscripción"
    )
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
        unique_together = ['competencia', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.competencia.nombre}"
    
    def plazas_disponibles(self):
        """Calcula las plazas disponibles en la categoría."""
        if self.cupo_maximo == 0:  # Ilimitado
            return None
        
        inscritos = self.inscripciones.filter(estado__in=['pendiente', 'aprobada', 'completada']).count()
        return self.cupo_maximo - inscritos

class CriterioEvaluacion(models.Model):
    """
    Modelo para los criterios de evaluación de una categoría.
    """
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='criterios',
        verbose_name="Categoría"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    puntaje_maximo = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Puntaje Máximo"
    )
    peso = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.00,
        validators=[MinValueValidator(0)],
        verbose_name="Peso (Multiplicador)"
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de Presentación"
    )
    
    class Meta:
        verbose_name = "Criterio de Evaluación"
        verbose_name_plural = "Criterios de Evaluación"
        ordering = ['categoria', 'orden', 'nombre']
        unique_together = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"

class Inscripcion(models.Model):
    """
    Modelo para las inscripciones de jinetes a competencias.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    competencia = models.ForeignKey(
        Competencia, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        verbose_name="Competencia"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        verbose_name="Categoría"
    )
    jinete = models.ForeignKey(
        Jinete, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        verbose_name="Jinete"
    )
    caballo = models.ForeignKey(
        Caballo, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        verbose_name="Caballo"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    numero_participante = models.PositiveIntegerField(
        blank=True, 
        null=True,
        verbose_name="Número de Participante"
    )
    comentarios = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Comentarios"
    )
    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Inscripción"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    comprobante_pago = models.FileField(
        upload_to='comprobantes/', 
        blank=True, 
        null=True,
        verbose_name="Comprobante de Pago"
    )
    
    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        ordering = ['competencia', 'categoria', 'numero_participante']
        unique_together = ['competencia', 'categoria', 'jinete', 'caballo']
    
    def __str__(self):
        return f"{self.jinete.usuario.get_full_name()} - {self.caballo.nombre} - {self.categoria.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para asignar número de participante si no existe.
        """
        if not self.numero_participante and self.estado == 'aprobada':
            ultimo_numero = Inscripcion.objects.filter(
                competencia=self.competencia,
                categoria=self.categoria,
                estado='aprobada'
            ).exclude(numero_participante=None).order_by('-numero_participante').first()
            
            self.numero_participante = 1 if not ultimo_numero else ultimo_numero.numero_participante + 1
            
        super().save(*args, **kwargs)

class AsignacionJuez(models.Model):
    """
    Modelo para asignar jueces a categorías de competencias.
    """
    juez = models.ForeignKey(
        Juez, 
        on_delete=models.CASCADE, 
        related_name='asignaciones',
        verbose_name="Juez"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='jueces_asignados',
        verbose_name="Categoría"
    )
    rol = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Rol en la Evaluación"
    )
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Asignación"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = "Asignación de Juez"
        verbose_name_plural = "Asignaciones de Jueces"
        ordering = ['categoria', 'juez']
        unique_together = ['juez', 'categoria']
    
    def __str__(self):
        return f"{self.juez.usuario.get_full_name()} - {self.categoria.nombre}"