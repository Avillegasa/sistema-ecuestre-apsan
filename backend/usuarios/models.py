# backend/usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende el modelo AbstractUser de Django
    para incluir campos adicionales específicos del sistema ecuestre.
    """
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'), 
        ('juez', 'Juez'),
        ('jinete', 'Jinete'), 
        ('entrenador', 'Entrenador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        verbose_name="Tipo de Usuario"
    )
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name="Foto de Perfil")
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_usuario_display()})"
    
    def get_profile_model(self):
        """
        Retorna el modelo de perfil específico según el tipo de usuario (Jinete, Juez, etc.)
        """
        if self.tipo_usuario == 'jinete':
            return hasattr(self, 'jinete') and self.jinete or None
        elif self.tipo_usuario == 'juez':
            return hasattr(self, 'juez') and self.juez or None
        elif self.tipo_usuario == 'entrenador':
            return hasattr(self, 'entrenador') and self.entrenador or None
        return None


class Jinete(models.Model):
    """
    Modelo para almacenar información específica de los jinetes.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='jinete',
        verbose_name="Usuario"
    )
    documento_identidad = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Documento de Identidad"
    )
    experiencia_anios = models.PositiveIntegerField(
        default=0, 
        verbose_name="Años de Experiencia"
    )
    categoria_habitual = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Categoría Habitual"
    )
    federado = models.BooleanField(default=False, verbose_name="¿Está federado?")
    numero_licencia = models.CharField(
        max_length=30, 
        blank=True, 
        null=True,
        verbose_name="Número de Licencia"
    )
    entrenador = models.ForeignKey(
        'Entrenador', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='jinetes',
        verbose_name="Entrenador"
    )
    
    class Meta:
        verbose_name = "Jinete"
        verbose_name_plural = "Jinetes"
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()}"


class Juez(models.Model):
    """
    Modelo para almacenar información específica de los jueces.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='juez',
        verbose_name="Usuario"
    )
    licencia = models.CharField(
        max_length=30, 
        blank=True, 
        null=True,
        verbose_name="Número de Licencia"
    )
    especialidad = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Especialidad"
    )
    nivel_certificacion = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Nivel de Certificación"
    )
    anios_experiencia = models.PositiveIntegerField(
        default=0, 
        verbose_name="Años de Experiencia"
    )
    federacion = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Federación"
    )
    
    class Meta:
        verbose_name = "Juez"
        verbose_name_plural = "Jueces"
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.especialidad or 'Sin especialidad'}"


class Entrenador(models.Model):
    """
    Modelo para almacenar información específica de los entrenadores.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='entrenador',
        verbose_name="Usuario"
    )
    especialidad = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Especialidad"
    )
    licencia = models.CharField(
        max_length=30, 
        blank=True, 
        null=True,
        verbose_name="Número de Licencia"
    )
    anios_experiencia = models.PositiveIntegerField(
        default=0, 
        verbose_name="Años de Experiencia"
    )
    certificaciones = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Certificaciones"
    )
    
    class Meta:
        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.especialidad or 'Sin especialidad'}"


class Caballo(models.Model):
    """
    Modelo para gestionar la información de los caballos registrados en el sistema.
    """
    GENERO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    
    jinete = models.ForeignKey(
        Jinete, 
        on_delete=models.CASCADE, 
        related_name='caballos',
        verbose_name="Jinete"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    raza = models.CharField(max_length=100, verbose_name="Raza")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    numero_registro = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número de Registro"
    )
    genero = models.CharField(
        max_length=1, 
        choices=GENERO_CHOICES, 
        verbose_name="Género"
    )
    color = models.CharField(max_length=50, verbose_name="Color")
    altura = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        verbose_name="Altura (m)"
    )
    peso = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Peso (kg)"
    )
    estado_salud = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Estado de Salud"
    )
    historial_competencias = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Historial de Competencias"
    )
    foto = models.ImageField(
        upload_to='caballos/', 
        blank=True, 
        null=True, 
        verbose_name="Fotografía"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )
    
    class Meta:
        verbose_name = "Caballo"
        verbose_name_plural = "Caballos"
        ordering = ['nombre']
        
    def __str__(self):
        return f"{self.nombre} - {self.jinete}"
    
    def edad(self):
        """
        Calcula la edad del caballo en años.
        """
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )