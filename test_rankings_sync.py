# test_rankings_sync.py
print("Iniciando script...")

import os
import sys
import django
import random
import traceback
from decimal import Decimal

print("Importaciones completadas")

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
print("Configurando Django...")
django.setup()
print("Django configurado correctamente")

def generate_scores(competition_id):
    """Genera calificaciones aleatorias para todos los participantes"""
    try:
        print("\n=== Generando Calificaciones Aleatorias ===")
        
        # Importar modelos
        from competitions.models import Competition, Participant, CompetitionJudge
        from judging.models import Score, CompetitionParameter
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Obtener competencia
        competition = Competition.objects.get(id=competition_id)
        print(f"Competencia: {competition.name} (ID: {competition_id})")
        
        # Obtener participantes
        participants = Participant.objects.filter(competition=competition)
        if not participants.exists():
            print("ERROR: No hay participantes en la competencia")
            return False
        print(f"Participantes encontrados: {participants.count()}")
        
        # Obtener parámetros
        parameters = CompetitionParameter.objects.filter(competition=competition)
        if not parameters.exists():
            print("ERROR: No hay parámetros en la competencia")
            return False
        print(f"Parámetros encontrados: {parameters.count()}")
        
        # Obtener jueces
        judges = CompetitionJudge.objects.filter(competition=competition)
        if not judges.exists():
            # Crear un juez de prueba si no hay ninguno
            print("No hay jueces asignados. Creando juez de prueba...")
            
            test_judge = None
            # Buscar si hay algún juez en el sistema
            judge_users = User.objects.filter(is_judge=True)
            if judge_users.exists():
                test_judge = judge_users.first()
                print(f"Usando juez existente: {test_judge.get_full_name()}")
            else:
                # Crear un nuevo juez
                test_judge = User.objects.create_user(
                    email='juez_test@apsan.org',
                    password='test123',
                    username='juez_test',
                    first_name='Juez',
                    last_name='Test',
                    is_judge=True
                )
                print(f"Juez de prueba creado: {test_judge.get_full_name()}")
            
            # Asignar a la competencia
            judge = CompetitionJudge.objects.create(
                competition=competition,
                judge=test_judge,
                is_head_judge=True
            )
            print(f"Juez asignado a la competencia: {judge.judge.get_full_name()}")
            judges = [judge]
        else:
            print(f"Jueces encontrados: {judges.count()}")
        
        # Generar calificaciones para cada participante y cada juez
        total_scores = 0
        
        for participant in participants:
            print(f"\nGenerando calificaciones para: {participant}")
            
            for judge in judges:
                print(f"  Juez: {judge.judge.get_full_name()}")
                
                for param in parameters:
                    # Generar una calificación aleatoria entre 4.0 y 9.5
                    score_value = round(random.uniform(4.0, 9.5), 1)
                    
                    # Crear o actualizar calificación
                    score, created = Score.objects.update_or_create(
                        competition=competition,
                        participant=participant,
                        judge=judge.judge,
                        parameter=param,
                        defaults={
                            'value': Decimal(str(score_value)),
                            'comments': f"Calificación generada automáticamente: {score_value}"
                        }
                    )
                    
                    if created:
                        print(f"    - Creada calificación para {param.parameter.name}: {score_value}")
                    else:
                        print(f"    - Actualizada calificación para {param.parameter.name}: {score_value}")
                    
                    total_scores += 1
        
        print(f"\nTotal de calificaciones generadas: {total_scores}")
        
        # Verificar que se hayan guardado correctamente
        saved_scores = Score.objects.filter(competition=competition).count()
        print(f"Calificaciones guardadas en base de datos: {saved_scores}")
        
        if saved_scores > 0:
            print("¡Calificaciones generadas exitosamente!")
            return True
        else:
            print("ERROR: No se guardaron las calificaciones")
            return False
        
    except Exception as e:
        print(f"ERROR al generar calificaciones: {str(e)}")
        traceback.print_exc()
        return False

def update_rankings(competition_id):
    """Actualiza los rankings para la competencia"""
    try:
        print("\n=== Actualizando Rankings ===")
        
        # Importar funciones necesarias
        from judging.services import update_participant_rankings
        
        # Verificar calificaciones existentes
        from judging.models import Score
        scores_count = Score.objects.filter(competition_id=competition_id).count()
        print(f"Calificaciones existentes: {scores_count}")
        
        if scores_count == 0:
            print("No hay calificaciones para calcular rankings. Intenta generar calificaciones primero.")
            return False
        
        # Actualizar rankings
        print("Calculando rankings...")
        rankings = update_participant_rankings(competition_id, recalculate_all=True)
        print(f"Rankings actualizados: {len(rankings)}")
        
        # Verificar rankings en base de datos
        from judging.models import Ranking
        saved_rankings = Ranking.objects.filter(competition_id=competition_id)
        print(f"Rankings guardados en base de datos: {saved_rankings.count()}")
        
        # Mostrar rankings calculados
        print("\nRankings calculados:")
        print("Posición | Participante | Porcentaje")
        print("---------|-------------|----------")
        for rank in rankings:
            participant = rank['participant']
            # Asegurarse de que el porcentaje sea un valor válido
            percentage = float(rank.get('percentage', 0))
            print(f"{rank['position']:8} | {participant} | {percentage:8.2f}%")
        
        return rankings
        
    except Exception as e:
        print(f"ERROR al actualizar rankings: {str(e)}")
        traceback.print_exc()
        return False

def sync_with_firebase(competition_id, rankings):
    """Sincroniza los rankings con Firebase"""
    try:
        print("\n=== Sincronizando con Firebase ===")
        
        from judging.firebase import sync_rankings
        result = sync_rankings(competition_id, rankings)
        print(f"Resultado de sincronización: {result}")
        
        return result
        
    except Exception as e:
        print(f"ERROR al sincronizar con Firebase: {str(e)}")
        traceback.print_exc()
        return False

def run_full_test():
    """Ejecuta la prueba completa"""
    try:
        print("\n=== Iniciando Prueba Completa ===")
        
        # Obtener datos de la competencia
        from competitions.models import Competition
        
        competitions = Competition.objects.all()
        if not competitions.exists():
            print("No hay competencias en la base de datos. Creando una...")
            # Aquí deberías llamar a una función para crear una competencia
            # Pero por simplicidad, solo mostraremos un error
            print("ERROR: Necesitas crear una competencia primero")
            return False
        
        # Usar la primera competencia
        competition = competitions.first()
        competition_id = competition.id
        print(f"Usando competencia: {competition.name} (ID: {competition_id})")
        
        # Generar calificaciones
        if not generate_scores(competition_id):
            print("ERROR: Falló la generación de calificaciones")
            return False
        
        # Actualizar rankings
        rankings = update_rankings(competition_id)
        if not rankings:
            print("ERROR: Falló la actualización de rankings")
            return False
        
        # Sincronizar con Firebase
        if not sync_with_firebase(competition_id, rankings):
            print("ERROR: Falló la sincronización con Firebase")
            return False
        
        print("\n¡Prueba completa finalizada exitosamente!")
        return True
        
    except Exception as e:
        print(f"ERROR en la prueba completa: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Ejecutando prueba completa...")
    
    try:
        run_full_test()
    except Exception as e:
        print(f"Error al ejecutar la prueba: {str(e)}")
        traceback.print_exc()
    
    print("Fin del script")