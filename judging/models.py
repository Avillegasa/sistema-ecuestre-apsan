from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from competitions.models import Competition, Participant

"""
Extensiones de modelos para la implementación del sistema FEI (3 celdas).
Este archivo debe importarse en models.py para añadir los métodos y funcionalidad.
"""
from decimal import Decimal
from .processors import fei_processor, ranking_calculator

class ScoreExtensionMixin:
    """
    Mixin para extender la funcionalidad del modelo Score.
    Añade métodos específicos para el sistema FEI.
    """
    
    def calculate_result(self):
        """
        Calcula el resultado de la calificación según la fórmula FEI.
        Este método se llama desde el método save() del modelo Score.
        
        Returns:
            Decimal: Resultado calculado
        """
        coefficient = self.parameter.effective_coefficient
        max_value = self.parameter.effective_max_value
        
        try:
            result = fei_processor.calculate_result(
                self.value, coefficient
            )
            return Decimal(str(result))
        except Exception as e:
            # Manejar error de cálculo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculando resultado para Score {self.id}: {e}")
            return Decimal('0')
    
    def validate_fei_rules(self):
        """
        Valida que la calificación cumpla con las reglas FEI.
        
        Returns:
            bool: True si la calificación es válida
            
        Raises:
            ValidationError: Si la calificación no cumple con las reglas
        """
        from django.core.exceptions import ValidationError
        
        try:
            # Validar que la calificación esté en el rango correcto (0-10)
            if not fei_processor.validate_score(self.value):
                raise ValidationError(
                    f"La calificación debe estar entre 0 y 10, recibido: {self.value}"
                )
            
            # Validar coeficiente (normalmente 1, 2 o 3 en FEI)
            coefficient = self.parameter.effective_coefficient
            if coefficient <= 0:
                raise ValidationError(
                    f"El coeficiente debe ser mayor que cero, recibido: {coefficient}"
                )
            
            return True
        except Exception as e:
            raise ValidationError(f"Error validando reglas FEI: {e}")
    
    def get_formatted_score(self):
        """
        Devuelve la calificación formateada para presentación.
        
        Returns:
            str: Calificación formateada
        """
        return f"{float(self.value):.1f}"
    
    def get_formatted_result(self):
        """
        Devuelve el resultado calculado formateado para presentación.
        
        Returns:
            str: Resultado formateado
        """
        return f"{float(self.calculated_result):.1f}"
    
    def to_firebase_dict(self):
        """
        Convierte el objeto Score a un diccionario para Firebase.
        
        Returns:
            dict: Datos formateados para Firebase
        """
        return {
            'id': self.id,
            'judgeId': self.judge_id,
            'judgeName': f"{self.judge.first_name} {self.judge.last_name}",
            'parameterId': self.parameter.parameter.id,
            'parameterName': self.parameter.parameter.name,
            'value': float(self.value),
            'calculatedResult': float(self.calculated_result),
            'comments': self.comments or '',
            'isEdited': self.is_edited,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class RankingExtensionMixin:
    """
    Mixin para extender la funcionalidad del modelo Ranking.
    Añade métodos específicos para el sistema FEI.
    """
    
    @classmethod
    def calculate_for_participant(cls, competition_id, participant_id):
        """
        Calcula el ranking para un participante específico.
        
        Args:
            competition_id: ID de la competencia
            participant_id: ID del participante
            
        Returns:
            Ranking: Objeto Ranking actualizado
        """
        from .models import Score, Ranking
        from competitions.models import Competition, Participant, CompetitionJudge
        
        # Obtener competencia y participante
        competition = Competition.objects.get(id=competition_id)
        participant = Participant.objects.get(id=participant_id, competition=competition)
        
        # Obtener jueces asignados
        judges = CompetitionJudge.objects.filter(
            competition=competition
        ).values_list('judge_id', flat=True)
        
        # Recopilar calificaciones agrupadas por juez
        judge_scores = {}
        scores = Score.objects.filter(
            competition=competition,
            participant=participant
        ).select_related('judge', 'parameter', 'parameter__parameter')
        
        for score in scores:
            if score.judge_id not in judge_scores:
                judge_scores[score.judge_id] = []
            judge_scores[score.judge_id].append(score)
        
        # Calcular ranking por juez
        judge_rankings = []
        for judge_id, scores_list in judge_scores.items():
            if scores_list:
                # Convertir a formato requerido por el calculador
                scores_data = [{
                    'calculated_result': score.calculated_result
                } for score in scores_list]
                
                judge_ranking = ranking_calculator.calculate_judge_ranking(scores_data)
                judge_rankings.append(judge_ranking)
        
        # Calcular ranking final
        final_ranking = ranking_calculator.calculate_final_ranking(judge_rankings)
        
        # Actualizar o crear objeto Ranking
        ranking, created = Ranking.objects.update_or_create(
        competition=competition,
        participant=participant,
        defaults={
            'average_score': final_ranking['average'],
            'percentage': final_ranking['percentage'],  # Asegúrate de que este valor sea correcto
            'position': 0  # La posición se actualizará en update_participant_rankings
        }
        )
        # CORRECCIÓN: Verifica que los valores se hayan guardado correctamente
        import logging
        logger = logging.getLogger(__name__)

        if float(ranking.percentage) == 0 and float(final_ranking['percentage']) > 0:
            logger.error(f"Problema al guardar porcentaje: valor original={final_ranking['percentage']}, guardado={ranking.percentage}")
            # Intentar forzar un valor válido
            ranking.percentage = final_ranking['percentage']
            ranking.save(update_fields=['percentage'])
        
        return ranking
    
    @classmethod
    def update_positions(cls, competition_id):
        """
        Actualiza las posiciones de todos los participantes en una competencia.
        
        Args:
            competition_id: ID de la competencia
            
        Returns:
            int: Número de rankings actualizados
        """
        from .models import Ranking
        
        # Obtener todos los rankings de la competencia ordenados por porcentaje
        rankings = Ranking.objects.filter(
            competition_id=competition_id
        ).order_by('-percentage')
        
        # Actualizar posiciones
        position = 1
        for ranking in rankings:
            ranking.position = position
            ranking.save(update_fields=['position'])
            position += 1
        
        return len(rankings)
    
    def to_firebase_dict(self):
        """
        Convierte el objeto Ranking a un diccionario para Firebase.
        
        Returns:
            dict: Datos formateados para Firebase
        """
        rider = self.participant.rider
        horse = self.participant.horse
        
        return {
            'participantId': self.participant.id,
            'rider': {
                'id': rider.id,
                'firstName': rider.first_name,
                'lastName': rider.last_name,
                'fullName': f"{rider.first_name} {rider.last_name}"
            },
            'horse': {
                'id': horse.id,
                'name': horse.name,
                'breed': horse.breed or ''
            },
            'position': self.position,
            'average': float(self.average_score),
            'percentage': float(self.percentage),
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

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
        return f"Ranking: {self.participant} - Pos: {self.position} ({float(self.percentage):.2f}%)"


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