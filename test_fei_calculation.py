# test_fei_calculation.py
import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
django.setup()

# Importar funciones a probar
from judging.processors import fei_processor
from decimal import Decimal, ROUND_HALF_UP

def run_test():
    print("=== Prueba de Cálculo FEI (Sistema 3 Celdas) ===")
    
    # Casos de prueba con diferentes valores
    test_cases = [
        (7.5, 1),  # Debería ser 8 (redondeado)
        (6.0, 2),  # Debería ser 10 (limitado al máximo)
        (4.5, 1),  # Debería ser 5 (redondeado)
        (0, 3),    # Debería ser 0
        (9.5, 1.5), # Debería ser 10 (limitado al máximo)
        (3.2, 1),  # Debería ser 3 (redondeado)
    ]
    
    print("Calificación | Coeficiente | Resultado Esperado | Resultado Obtenido | ¿Correcto?")
    print("-------------|-------------|-------------------|-------------------|----------")
    
    for score, coefficient in test_cases:
        # Determinar resultado esperado (reglas FEI: valor * coef, máx 10, redondeado)
        raw_result = score * coefficient
        expected = min(int(Decimal(str(raw_result)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)), 10)
        
        # Calcular resultado con el procesador FEI
        try:
            result = fei_processor.calculate_result(score, coefficient)
            
            # Verificar si coincide con lo esperado
            is_correct = result == expected
            
            print(f"{score:11} | {coefficient:11} | {expected:17} | {result:17} | {'✓' if is_correct else '✗'}")
        except Exception as e:
            print(f"{score:11} | {coefficient:11} | {expected:17} | Error: {str(e)}")

if __name__ == "__main__":
    run_test()