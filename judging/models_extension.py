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
                'percentage': final_ranking['percentage'],
                # La posición se actualizará en update_participant_rankings
                'position': 0
            }
        )
        
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