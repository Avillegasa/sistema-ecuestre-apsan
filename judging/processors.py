"""
Procesadores de calificación específicos para el sistema FEI (3 celdas).
Este módulo contiene las clases y funciones para procesar y validar calificaciones.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class FEIScoreProcessor:
    """
    Procesador para calificaciones según el sistema FEI de 3 celdas.
    Implementa las reglas y validaciones del sistema FEI.
    """
    
    def __init__(self, max_value: int = 10):
        """Inicializar procesador con valor máximo permitido"""
        self.max_value = max_value
    
    def validate_score(self, score: Union[int, float, str, Decimal]) -> bool:
        """
        Validar que una calificación esté en el rango correcto
        
        Args:
            score: Calificación a validar
            
        Returns:
            bool: True si la calificación es válida
            
        Raises:
            ValueError: Si la calificación no se puede convertir a decimal
        """
        try:
            # Convertir a decimal si es necesario
            if not isinstance(score, Decimal):
                score = Decimal(str(score))
            
            # Validar rango (0-10)
            return Decimal('0') <= score <= Decimal(str(self.max_value))
        except Exception as e:
            logger.error(f"Error validando calificación: {e}")
            raise ValueError(f"La calificación no es válida: {score}")
    
    def calculate_result(self, 
                        score: Union[int, float, str, Decimal], 
                        coefficient: Union[int, float, str, Decimal]
                       ) -> int:
        """
        Calcular el resultado según la fórmula FEI
        
        Args:
            score: Calificación del juez
            coefficient: Coeficiente del parámetro
            
        Returns:
            int: Resultado calculado
            
        Raises:
            ValueError: Si los valores no son válidos
        """
        try:
            # Convertir a decimal si es necesario
            if not isinstance(score, Decimal):
                score = Decimal(str(score))
            if not isinstance(coefficient, Decimal):
                coefficient = Decimal(str(coefficient))
            
            # Validar calificación
            if not self.validate_score(score):
                raise ValueError(f"La calificación debe estar entre 0 y {self.max_value}")
            
            # Validar coeficiente
            if coefficient <= Decimal('0'):
                raise ValueError("El coeficiente debe ser mayor a cero")
            
            # Realizar cálculo
            result = score * coefficient
            
            # El resultado no debe exceder el valor máximo
            result = min(result, Decimal(str(self.max_value)))
            
            # El resultado debe ser un número entero
            result = int(result.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            return result
        except Exception as e:
            logger.error(f"Error calculando resultado: {e}")
            raise
    
    def calculate_average(self, scores: List[Union[int, float, Decimal]]) -> Decimal:
        """
        Calcular el promedio de un conjunto de calificaciones
        
        Args:
            scores: Lista de calificaciones
            
        Returns:
            Decimal: Promedio calculado con 2 decimales
        """
        if not scores:
            return Decimal('0')
        
        # Convertir todas las puntuaciones a Decimal
        decimal_scores = [Decimal(str(score)) for score in scores]
        
        # Calcular promedio
        total = sum(decimal_scores)
        average = total / Decimal(len(decimal_scores))
        
        # Redondear a 2 decimales
        return average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_percentage(self, average: Union[int, float, Decimal]) -> Decimal:
        """
        Convertir promedio a porcentaje
        
        Args:
            average: Promedio (0-10)
            
        Returns:
            Decimal: Porcentaje (0-100) con 2 decimales
        """
        if not isinstance(average, Decimal):
            average = Decimal(str(average))
        
        percentage = (average / Decimal(str(self.max_value))) * Decimal('100')
        return percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ParticipantRankingCalculator:
    """
    Calculador de rankings para participantes.
    Combina calificaciones de múltiples jueces siguiendo el sistema FEI.
    """
    
    def __init__(self):
        """Inicializar calculador de rankings"""
        self.score_processor = FEIScoreProcessor()
    
    def calculate_judge_ranking(self, 
                              scores: List[Dict[str, Any]],
                              parameters: Optional[Dict[str, Any]] = None
                             ) -> Dict[str, Any]:
        """
        Calcular ranking de un juez para un participante
        
        Args:
            scores: Lista de calificaciones del juez
            parameters: Información sobre parámetros (opcional)
            
        Returns:
            Dict: Datos del ranking para este juez
        """
        if not scores:
            return {
                'average': Decimal('0.00'),
                'percentage': Decimal('0.00'),
                'count': 0
            }
        
        # Calcular resultados si no están calculados
        calculated_scores = []
        for score in scores:
            if 'calculated_result' in score:
                calculated_scores.append(Decimal(str(score['calculated_result'])))
            elif parameters and 'parameter_id' in score and 'value' in score:
                param_id = str(score['parameter_id'])
                if param_id in parameters:
                    coefficient = parameters[param_id].get('coefficient', 1)
                    result = self.score_processor.calculate_result(
                        score['value'], coefficient
                    )
                    calculated_scores.append(Decimal(str(result)))
            elif 'value' in score:
                # Si no hay información de parámetros, usar la calificación directamente
                calculated_scores.append(Decimal(str(score['value'])))
        
        # Calcular promedio y porcentaje
        average = self.score_processor.calculate_average(calculated_scores)
        percentage = self.score_processor.calculate_percentage(average)
        
        return {
            'average': average,
            'percentage': percentage,
            'count': len(calculated_scores)
        }
    
    def calculate_final_ranking(self, 
                              judge_rankings: List[Dict[str, Any]]
                             ) -> Dict[str, Any]:
        """
        Calcular ranking final combinando calificaciones de todos los jueces
        
        Args:
            judge_rankings: Lista de rankings de los jueces
            
        Returns:
            Dict: Ranking final
        """
        if not judge_rankings:
            return {
                'average': Decimal('0.00'),
                'percentage': Decimal('0.00'),
                'judge_count': 0
            }
        
        # Calcular promedio de porcentajes de todos los jueces
        percentages = [ranking['percentage'] for ranking in judge_rankings]
        avg_percentage = self.score_processor.calculate_average(percentages)
        
        # Convertir de nuevo a promedio (0-10)
        max_value = Decimal('10')
        final_average = (avg_percentage / Decimal('100')) * max_value
        final_average = final_average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            'average': final_average,
            'percentage': avg_percentage,
            'judge_count': len(judge_rankings)
        }


# Instancia compartida para usar en el proyecto
fei_processor = FEIScoreProcessor()
ranking_calculator = ParticipantRankingCalculator()