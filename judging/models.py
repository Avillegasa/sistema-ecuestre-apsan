from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from competitions.models import Competition, Participant
from .models_extension import ScoreExtensionMixin, RankingExtensionMixin

class EvaluationParameter(models.Model):
    """Modelo para parámetros de evaluación FEI"""
    
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True, null=True)
    
    # Valores según el sistema FEI de 3 celdas
    coefficient = models.PositiveSmallIntegerField('Coeficiente', default=1, 
                                                 validators=[MinValueValidator(1)])
    max_value = models.PositiveSmallIntegerField('Valor Máximo', default=10)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Parámetro de Evaluación'
        verbose_name_plural = 'Parámetros de Evaluación'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} (Coef: {self.coefficient})"


class CompetitionParameter(models.Model):
    """Relación entre Competencia y Parámetros de Evaluación"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, 
                                   related_name='evaluation_parameters')
    parameter = models.ForeignKey(EvaluationParameter, on_delete=models.CASCADE,
                                 related_name='competitions')
    order = models.PositiveSmallIntegerField('Orden', default=1)
    
    # Permite sobrescribir valores específicos para esta competencia
    custom_coefficient = models.PositiveSmallIntegerField(
        'Coeficiente Personalizado', 
        blank=True, 
        null=True,
        validators=[MinValueValidator(1)]
    )
    custom_max_value = models.PositiveSmallIntegerField(
        'Valor Máximo Personalizado', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = 'Parámetro de Competencia'
        verbose_name_plural = 'Parámetros de Competencia'
        unique_together = ('competition', 'parameter')
        ordering = ['competition', 'order']
        
    def __str__(self):
        return f"{self.competition.name} - {self.parameter.name}"
    
    @property
    def effective_coefficient(self):
        """Devuelve el coeficiente efectivo (personalizado o por defecto)"""
        return self.custom_coefficient if self.custom_coefficient is not None else self.parameter.coefficient
    
    @property
    def effective_max_value(self):
        """Devuelve el valor máximo efectivo (personalizado o por defecto)"""
        return self.custom_max_value if self.custom_max_value is not None else self.parameter.max_value


class Score(models.Model, ScoreExtensionMixin):
    """Modelo para calificaciones de un juez a un participante"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='scores')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='scores')
    judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scores')
    parameter = models.ForeignKey(CompetitionParameter, on_delete=models.CASCADE, related_name='scores')
    
    # Calificación del juez (celda 3 en el sistema FEI)
    value = models.DecimalField(
        'Calificación', 
        max_digits=4, 
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    # Resultado calculado (value * coefficient, no debe exceder max_value)
    calculated_result = models.DecimalField(
        'Resultado calculado',
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    # Comentarios (opcional)
    comments = models.TextField('Comentarios', blank=True, null=True)
    
    # Historial de edición
    is_edited = models.BooleanField('Editada', default=False)
    edit_reason = models.CharField('Razón de edición', max_length=200, blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ('competition', 'participant', 'judge', 'parameter')
        
    def __str__(self):
        return f"Calificación: {self.judge.get_full_name()} - {self.participant} - {self.parameter.parameter.name}"
    
    def save(self, *args, **kwargs):
        # Calcular el resultado según la fórmula FEI
        self.calculated_result = self.calculate_result()
        
        super(Score, self).save(*args, **kwargs)
    
    def clean(self):
        """Validar calificación según normas FEI"""
        super().clean()
        self.validate_fei_rules()


class ScoreEdit(models.Model):
    """Modelo para auditoría de ediciones de calificaciones"""
    
    score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='edits')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='score_edits')
    
    # Valores anteriores
    previous_value = models.DecimalField('Valor anterior', max_digits=4, decimal_places=1)
    previous_result = models.DecimalField('Resultado anterior', max_digits=4, decimal_places=1)
    
    # Información de la edición
    edit_reason = models.CharField('Razón de edición', max_length=200)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Edición de Calificación'
        verbose_name_plural = 'Ediciones de Calificaciones'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Edición de {self.score} por {self.editor.get_full_name()}"


class Ranking(models.Model, RankingExtensionMixin):
    """Modelo para rankings calculados"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='rankings')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='rankings')
    
    # Resultados del ranking
    average_score = models.DecimalField('Promedio', max_digits=5, decimal_places=2)
    percentage = models.DecimalField('Porcentaje', max_digits=5, decimal_places=2)
    position = models.PositiveSmallIntegerField('Posición')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ranking'
        verbose_name_plural = 'Rankings'
        unique_together = ('competition', 'participant')
        ordering = ['competition', 'position']
        
    def __str__(self):
        return f"Ranking: {self.participant} - Pos: {self.position} ({self.percentage}%)"


class FirebaseSync(models.Model):
    """Modelo para seguimiento de sincronización con Firebase"""
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='firebase_syncs')
    last_sync = models.DateTimeField('Última sincronización', auto_now=True)
    is_synced = models.BooleanField('Sincronizado', default=False)
    error_message = models.TextField('Mensaje de error', blank=True, null=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sincronización Firebase'
        verbose_name_plural = 'Sincronizaciones Firebase'
        
    def __str__(self):
        return f"Sync Firebase: {self.competition.name} - {self.last_sync}"


class OfflineData(models.Model):
    """Modelo para almacenar datos offline temporales"""
    
    judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='offline_data')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, 
                                   related_name='offline_data')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, 
                                   related_name='offline_data')
    
    # Datos serializados (JSON)
    data = models.JSONField('Datos')
    
    # Estado de sincronización
    is_synced = models.BooleanField('Sincronizado', default=False)
    sync_attempts = models.PositiveSmallIntegerField('Intentos de sincronización', default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dato Offline'
        verbose_name_plural = 'Datos Offline'
        
    def __str__(self):
        return f"Datos Offline: {self.judge.get_full_name()} - {self.competition.name}"