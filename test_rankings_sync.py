# test_rankings_sync.py
import os
import sys
import django
import random

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
django.setup()

# Importar funciones y modelos necesarios
from judging.services import update_participant_rankings
from judging.firebase import sync_rankings
from competitions.models import Competition, Participant
from judging.models import Score, CompetitionParameter
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def generate_random_scores(competition_id):
    print("=== Generando Calificaciones Aleatorias ===")
    
    try:
        # Obtener competencia
        competition = Competition.objects.get(id=competition_id)
        print(f"Competencia encontrada: {competition.name}")
        
        # Obtener juez
        judge = User.objects.filter(is_judge=True).first()
        if not judge:
            print("No se encontró ningún juez. Revisa los datos de prueba.")
            return False
        print(f"Juez seleccionado: {judge.first_name} {judge.last_name}")
        
        # Obtener participantes
        participants = Participant.objects.filter(competition=competition)
        if not participants.exists():
            print("No se encontraron participantes. Revisa los datos de prueba.")
            return False
        print(f"Participantes encontrados: {participants.count()}")
        
        # Obtener parámetros
        parameters = CompetitionParameter.objects.filter(competition=competition)
        if not parameters.exists():
            print("No se encontraron parámetros. Revisa los datos de prueba.")
            return False
        print(f"Parámetros encontrados: {parameters.count()}")
        
        # Generar calificaciones aleatorias para cada participante y parámetro
        for participant in participants:
            print(f"\nGenerando calificaciones para: {participant.rider.first_name} con {participant.horse.name}")
            
            for param in parameters:
                # Generar una calificación aleatoria entre 0 y 10
                score_value = round(random.uniform(4.0, 9.5), 1)
                
                # Crear o actualizar calificación
                score, created = Score.objects.update_or_create(
                    competition=competition,
                    participant=participant,
                    judge=judge,
                    parameter=param,
                    defaults={
                        'value': Decimal(str(score_value)),
                        'comments': f"Calificación generada automáticamente: {score_value}"
                    }
                )
                
                if created:
                    print(f"  - Creada calificación para {param.parameter.name}: {score_value}")
                else:
                    print(f"  - Actualizada calificación para {param.parameter.name}: {score_value}")
        
        print("\nCalificaciones generadas exitosamente!")
        return True
    
    except Exception as e:
        print(f"Error al generar calificaciones: {str(e)}")
        return False

def test_ranking_sync(competition_id):
    print("\n=== Prueba de Sincronización de Rankings ===")
    
    # Paso 1: Actualizar rankings para la competencia
    print("\nPaso 1: Actualizando rankings...")
    try:
        rankings = update_participant_rankings(competition_id, recalculate_all=True)
        print(f"Rankings actualizados: {len(rankings)}")
        
        # Mostrar rankings calculados
        print("\nRankings calculados:")
        print("Posición | Participante                | Porcentaje")
        print("---------|----------------------------|----------")
        for rank in rankings:
            participant = rank['participant']
            # Asegúrate de que el porcentaje se convierta a float
            percentage = float(rank['percentage']) if 'percentage' in rank else 0.0
            print(f"{rank['position']:8} | {participant.rider.first_name} con {participant.horse.name:15} | {percentage:8.2f}%")
        
    except Exception as e:
        print(f"Error al actualizar rankings: {str(e)}")
        return False
    
    # Paso 2: Sincronizar con Firebase
    print("\nPaso 2: Sincronizando rankings con Firebase...")
    try:
        sync_result = sync_rankings(competition_id, rankings)
        print(f"¿Rankings sincronizados correctamente?: {sync_result}")
        return sync_result
    except Exception as e:
        print(f"Error al sincronizar rankings: {str(e)}")
        return False

def run_complete_test():
    # Primero crear datos de prueba
    try:
        # Importar la función para crear datos de prueba
        from create_test_data import create_test_data
        
        # Crear datos de prueba
        competition_id = create_test_data()
        
        # Generar calificaciones aleatorias
        if generate_random_scores(competition_id):
            # Probar sincronización de rankings
            test_ranking_sync(competition_id)
    except ImportError:
        print("El archivo create_test_data.py no existe. Ejecútalo primero para crear datos.")
    except Exception as e:
        print(f"Error en la prueba: {str(e)}")

if __name__ == "__main__":
    run_complete_test()