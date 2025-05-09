# backend/evaluaciones/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from competencias.models import Inscripcion, CriterioEvaluacion
from usuarios.models import Juez

class Evaluacion(models.Model):
    """
    Modelo para almacenar las evaluaciones de los jueces a los participantes.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('anulada', 'Anulada'),
    ]
    
    inscripcion = models.ForeignKey(
        Inscripcion, 
        on_delete=models.CASCADE, 
        related_name='evaluaciones',
        verbose_name="Inscripción"
    )
    juez = models.ForeignKey(
        Juez, 
        on_delete=models.CASCADE, 
        related_name='evaluaciones',
        verbose_name="Juez"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    comentario_general = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Comentario General"
    )
    fecha_inicio = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Inicio de Evaluación"
    )
    fecha_finalizacion = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Fecha de Finalización de Evaluación"
    )
    puntaje_total = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        blank=True, 
        null=True,
        verbose_name="Puntaje Total"
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
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['inscripcion', 'juez']
        unique_together = ['inscripcion', 'juez']
    
    def __str__(self):
        return f"Evaluación de {self.juez.usuario.get_full_name()} a {self.inscripcion}"
    
    def calcular_puntaje_total(self):
        """
        Calcula el puntaje total de la evaluación basado en las puntuaciones
        de cada criterio y sus pesos respectivos.
        """
        puntuaciones = self.puntuaciones.select_related('criterio').all()
        
        if not puntuaciones:
            return None
        
        puntaje_total = 0
        for puntuacion in puntuaciones:
            puntaje_ponderado = puntuacion.valor * puntuacion.criterio.peso
            puntaje_total += puntaje_ponderado
        
        return round(puntaje_total, 2)
    
    def actualizar_puntaje_total(self):
        """
        Actualiza el puntaje total de la evaluación.
        """
        self.puntaje_total = self.calcular_puntaje_total()
        self.save(update_fields=['puntaje_total'])
    
    def verificar_completitud(self):
        """
        Verifica si todos los criterios han sido evaluados.
        """
        criterios_categoria = self.inscripcion.categoria.criterios.count()
        puntuaciones_realizadas = self.puntuaciones.count()
        
        return criterios_categoria == puntuaciones_realizadas

class Puntuacion(models.Model):
    """
    Modelo para almacenar las puntuaciones específicas por criterio en una evaluación.
    """
    evaluacion = models.ForeignKey(
        Evaluacion, 
        on_delete=models.CASCADE, 
        related_name='puntuaciones',
        verbose_name="Evaluación"
    )
    criterio = models.ForeignKey(
        CriterioEvaluacion, 
        on_delete=models.CASCADE, 
        related_name='puntuaciones',
        verbose_name="Criterio de Evaluación"
    )
    valor = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Puntuación"
    )
    comentario = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Comentario"
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
        verbose_name = "Puntuación"
        verbose_name_plural = "Puntuaciones"
        ordering = ['evaluacion', 'criterio']
        unique_together = ['evaluacion', 'criterio']
    
    def __str__(self):
        return f"{self.criterio.nombre}: {self.valor}"
    
    def clean(self):
        """
        Validar que la puntuación no exceda el máximo del criterio.
        """
        from django.core.exceptions import ValidationError
        
        if self.valor > self.criterio.puntaje_maximo:
            raise ValidationError({
                'valor': f'La puntuación no puede ser mayor que el máximo permitido para este criterio ({self.criterio.puntaje_maximo}).'
            })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para validar puntuación y actualizar el total de la evaluación.
        """
        self.clean()
        super().save(*args, **kwargs)
        
        # Actualizar el puntaje total de la evaluación
        self.evaluacion.actualizar_puntaje_total()