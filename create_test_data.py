# create_test_data.py
import os
import sys
import django
import random
from datetime import datetime, timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
django.setup()

# Importar modelos necesarios
from django.contrib.auth import get_user_model
from competitions.models import Competition, Category, Rider, Horse, Participant
from judging.models import EvaluationParameter, CompetitionParameter

User = get_user_model()

def create_test_data():
    print("=== Creando Datos de Prueba ===")
    
    # 1. Crear usuario administrador si no existe
    try:
        admin_user = User.objects.get(email='admin@apsan.org')
        print("Usuario admin ya existe.")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            email='admin@apsan.org',
            password='adminpwd123',
            first_name='Admin',
            last_name='APSAN',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        print("Usuario admin creado.")
    
    # 2. Crear usuario juez si no existe
    try:
        judge_user = User.objects.get(email='juez@apsan.org')
        print("Usuario juez ya existe.")
    except User.DoesNotExist:
        judge_user = User.objects.create_user(
            email='juez@apsan.org',
            password='juezpwd123',
            first_name='Juez',
            last_name='Principal',
            role='judge',
            is_judge=True
        )
        print("Usuario juez creado.")
    
    # 3. Crear categoría si no existe
    try:
        category = Category.objects.get(code='ADIESTRAMIENTO')
        print("Categoría ya existe.")
    except Category.DoesNotExist:
        category = Category.objects.create(
            name='Adiestramiento',
            code='ADIESTRAMIENTO',
            description='Competencia de adiestramiento ecuestre'
        )
        print("Categoría creada.")
    
    # 4. Crear competencia si no existe
    today = datetime.now().date()
    start_date = today - timedelta(days=1)
    end_date = today + timedelta(days=2)
    
    try:
        competition = Competition.objects.get(name='Competencia de Prueba')
        print("Competencia ya existe.")
    except Competition.DoesNotExist:
        competition = Competition.objects.create(
            name='Competencia de Prueba',
            description='Competencia para pruebas del sistema',
            location='La Paz, Bolivia',
            start_date=start_date,
            end_date=end_date,
            status='active',
            is_public=True,
            creator=admin_user
        )
        print("Competencia creada.")
    
    # 5. Asignar juez a la competencia
    from competitions.models import CompetitionJudge
    if not CompetitionJudge.objects.filter(competition=competition, judge=judge_user).exists():
        CompetitionJudge.objects.create(
            competition=competition,
            judge=judge_user,
            is_head_judge=True
        )
        print("Juez asignado a competencia.")
    else:
        print("Juez ya asignado a competencia.")
    
    # 6. Crear parámetros de evaluación FEI si no existen
    parameters = [
        {'name': 'Entrada y parada', 'coefficient': 2},
        {'name': 'Transición al trote', 'coefficient': 1},
        {'name': 'Círculo de 20m', 'coefficient': 1},
        {'name': 'Cambio de mano', 'coefficient': 2},
        {'name': 'Transición al galope', 'coefficient': 3}
    ]
    
    eval_params = []
    for param_data in parameters:
        param, created = EvaluationParameter.objects.get_or_create(
            name=param_data['name'],
            defaults={
                'coefficient': param_data['coefficient'],
                'max_value': 10
            }
        )
        if created:
            print(f"Parámetro '{param.name}' creado.")
        else:
            print(f"Parámetro '{param.name}' ya existe.")
        eval_params.append(param)
    
    # 7. Asignar parámetros a la competencia
    for i, param in enumerate(eval_params):
        comp_param, created = CompetitionParameter.objects.get_or_create(
            competition=competition,
            parameter=param,
            defaults={'order': i+1}
        )
        if created:
            print(f"Parámetro '{param.name}' asignado a competencia.")
        else:
            print(f"Parámetro '{param.name}' ya asignado a competencia.")
    
    # 8. Crear 3 jinetes si no existen
    riders_data = [
        {'first_name': 'Ana', 'last_name': 'Pérez'},
        {'first_name': 'Carlos', 'last_name': 'López'},
        {'first_name': 'María', 'last_name': 'González'}
    ]
    
    riders = []
    for rider_data in riders_data:
        rider, created = Rider.objects.get_or_create(
            first_name=rider_data['first_name'],
            last_name=rider_data['last_name']
        )
        if created:
            print(f"Jinete '{rider.first_name} {rider.last_name}' creado.")
        else:
            print(f"Jinete '{rider.first_name} {rider.last_name}' ya existe.")
        riders.append(rider)
    
    # 9. Crear 3 caballos si no existen
    horses_data = [
        {'name': 'Tornado', 'breed': 'Pura Sangre'},
        {'name': 'Relámpago', 'breed': 'Árabe'},
        {'name': 'Estrella', 'breed': 'Andaluz'}
    ]
    
    horses = []
    for horse_data in horses_data:
        horse, created = Horse.objects.get_or_create(
            name=horse_data['name'],
            defaults={'breed': horse_data['breed']}
        )
        if created:
            print(f"Caballo '{horse.name}' creado.")
        else:
            print(f"Caballo '{horse.name}' ya existe.")
        horses.append(horse)
    
    # 10. Crear participantes (combinaciones de jinete y caballo)
    for i in range(3):
        participant, created = Participant.objects.get_or_create(
            competition=competition,
            rider=riders[i],
            horse=horses[i],
            defaults={
                'category': category,
                'number': i+1,
                'order': i+1,
                'is_withdrawn': False
            }
        )
        if created:
            print(f"Participante '{riders[i].first_name} con {horses[i].name}' creado.")
        else:
            print(f"Participante '{riders[i].first_name} con {horses[i].name}' ya existe.")
    
    print("\nDatos de prueba creados exitosamente!")
    print(f"ID de la competencia para pruebas: {competition.id}")
    return competition.id

if __name__ == "__main__":
    create_test_data()