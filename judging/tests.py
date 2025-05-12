from django.test import TestCase
from decimal import Decimal
from .processors import fei_processor

class FEICalculationTests(TestCase):
    def test_calculate_result_normal(self):
        """Probar cálculo normal FEI"""
        # Caso: calificación 7.5, coeficiente 1
        result = fei_processor.calculate_result(7.5, 1)
        self.assertEqual(result, 8)  # 7.5 redondeado a 8
        
        # Caso: calificación 6.0, coeficiente 2
        result = fei_processor.calculate_result(6.0, 2)
        self.assertEqual(result, 10)  # Limitado al máximo de 10
    
    def test_calculate_result_edge_cases(self):
        """Probar casos límite del cálculo FEI"""
        # Caso: calificación 0, coeficiente 1
        result = fei_processor.calculate_result(0, 1)
        self.assertEqual(result, 0)
        
        # Caso: calificación 10, coeficiente 3 (debería ser limitado a 10)
        result = fei_processor.calculate_result(10, 3)
        self.assertEqual(result, 10)
    
    def test_validate_score(self):
        """Probar validación de calificaciones"""
        # Calificaciones válidas
        self.assertTrue(fei_processor.validate_score(0))
        self.assertTrue(fei_processor.validate_score(5))
        self.assertTrue(fei_processor.validate_score(7.5))
        self.assertTrue(fei_processor.validate_score(10))
        
        # Calificaciones inválidas
        with self.assertRaises(ValueError):
            fei_processor.validate_score(-1)
        with self.assertRaises(ValueError):
            fei_processor.validate_score(11)