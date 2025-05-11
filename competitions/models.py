from django.db import models
from django.conf import settings

class Competition(models.Model):
    """Modelo para competencias ecuestres"""
    
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('active', 'Activa'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    )
    
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True, null=True)
    location = models.CharField('Ubicación', max_length=100)
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin')
    
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField('Pública', default=True)
    
    # Relaciones
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='created_competitions'
    )
    judges = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='CompetitionJudge',
        related_name='judging_competitions'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'
        ordering = ['-start_date']
        
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class Category(models.Model):
    """Modelo para categorías de competencia"""
    
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True, null=True)
    code = models.CharField('Código', max_length=20, unique=True)
    
    # Atributos específicos de la categoría
    min_age = models.PositiveSmallIntegerField('Edad Mínima', null=True, blank=True)
    max_age = models.PositiveSmallIntegerField('Edad Máxima', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class CompetitionCategory(models.Model):
    """Relación entre Competencia y Categoría"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='competition_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_competitions')
    
    start_time = models.DateTimeField('Hora de Inicio', null=True, blank=True)
    end_time = models.DateTimeField('Hora de Fin', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría de Competencia'
        verbose_name_plural = 'Categorías de Competencia'
        unique_together = ('competition', 'category')
        
    def __str__(self):
        return f"{self.competition.name} - {self.category.name}"


class CompetitionJudge(models.Model):
    """Relación entre Competencia y Jueces"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_head_judge = models.BooleanField('Juez Principal', default=False)
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Juez de Competencia'
        verbose_name_plural = 'Jueces de Competencia'
        unique_together = ('competition', 'judge')
        
    def __str__(self):
        return f"{self.judge.get_full_name()} - {self.competition.name}"
    
    def save(self, *args, **kwargs):
        # Verificar que el usuario tenga rol de juez
        if not self.judge.is_judge:
            raise ValueError("El usuario debe tener rol de juez")
        super(CompetitionJudge, self).save(*args, **kwargs)


class Rider(models.Model):
    """Modelo para jinetes"""
    
    first_name = models.CharField('Nombre', max_length=100)
    last_name = models.CharField('Apellido', max_length=100)
    
    # Información personal
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    nationality = models.CharField('Nacionalidad', max_length=50, blank=True, null=True)
    gender = models.CharField('Género', max_length=10, blank=True, null=True)
    
    # Información de contacto
    email = models.EmailField('Correo Electrónico', blank=True, null=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Jinete'
        verbose_name_plural = 'Jinetes'
        ordering = ['last_name', 'first_name']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Horse(models.Model):
    """Modelo para caballos"""
    
    name = models.CharField('Nombre', max_length=100)
    
    # Información básica
    breed = models.CharField('Raza', max_length=50, blank=True, null=True)
    birth_year = models.PositiveSmallIntegerField('Año de Nacimiento', blank=True, null=True)
    gender = models.CharField('Género', max_length=20, blank=True, null=True)
    height = models.DecimalField('Altura (cm)', max_digits=5, decimal_places=2, blank=True, null=True)
    color = models.CharField('Color', max_length=50, blank=True, null=True)
    
    # Información de registro
    registration_number = models.CharField('Número de Registro', max_length=50, blank=True, null=True)
    microchip = models.CharField('Microchip', max_length=50, blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Caballo'
        verbose_name_plural = 'Caballos'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Participant(models.Model):
    """Modelo para participantes (combinación de jinete y caballo) en una competencia"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='participants')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='participations')
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, related_name='participations')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='participants')
    
    # Información de participación
    number = models.PositiveSmallIntegerField('Número de Participante')
    order = models.PositiveSmallIntegerField('Orden de Salida')
    
    # Estado
    is_withdrawn = models.BooleanField('Retirado', default=False)
    withdrawal_reason = models.CharField('Razón de Retiro', max_length=200, blank=True, null=True)
    
    # Metadatos
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'
        unique_together = ('competition', 'number')
        ordering = ['competition', 'order']
        
    def __str__(self):
        return f"{self.rider.full_name} - {self.horse.name} ({self.competition.name})"