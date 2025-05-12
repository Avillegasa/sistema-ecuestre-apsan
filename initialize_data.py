# initialize_data.py
import os
import django
import environ

env = environ.Env()
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
environ.Env.read_env(env_file)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
django.setup()

from django.db import transaction
from users.models import User, JudgeProfile
from competitions.models import Competition, Category, Rider, Horse, Participant, CompetitionJudge
from judging.models import EvaluationParameter, CompetitionParameter
from django.utils import timezone
from datetime import timedelta

print("Inicializando datos para el Sistema Ecuestre APSAN")

# Función para inicializar datos base en Django
@transaction.atomic
def initialize_django_data():
    print("\nCreando datos base en Django...")
    
    # 1. Crear usuarios base
    try:
        admin = User.objects.get(email='admin@apsan.org')
        print("✓ Admin ya existe")
    except User.DoesNotExist:
        admin = User.objects.create_user(
            email='admin@apsan.org',
            password='admin123',
            first_name='Admin',
            last_name='APSAN',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        print("✓ Admin creado")

    # Crear jueces
    judges = []
    for i in range(1, 4):  # Crear 3 jueces
        email = f'juez{i}@apsan.org'
        try:
            judge = User.objects.get(email=email)
            print(f"✓ Juez {i} ya existe")
        except User.DoesNotExist:
            judge = User.objects.create_user(
                email=email,
                password='juez123',
                first_name=f'Juez{i}',
                last_name=f'Apellido{i}',
                role='judge'
            )
            
            # Crear perfil de juez
            JudgeProfile.objects.create(
                user=judge,
                specialty='Adiestramiento',
                contact_phone=f'+5917777777{i}'
            )
            print(f"✓ Juez {i} creado")
        judges.append(judge)

    # 2. Crear categorías
    categories = []
    category_data = [
        {'name': 'Prelim A', 'code': 'PA', 'min_age': 12, 'max_age': 18},
        {'name': 'Intermedia I', 'code': 'IN1', 'min_age': 18, 'max_age': None},
        {'name': 'Gran Premio', 'code': 'GP', 'min_age': 21, 'max_age': None}
    ]
    
    for cat_info in category_data:
        try:
            category = Category.objects.get(code=cat_info['code'])
            print(f"✓ Categoría {cat_info['name']} ya existe")
        except Category.DoesNotExist:
            category = Category.objects.create(**cat_info)
            print(f"✓ Categoría {cat_info['name']} creada")
        categories.append(category)

    # 3. Crear competencia
    try:
        competition = Competition.objects.get(name='Torneo APSAN 2025')
        print(f"✓ Competencia ya existe")
    except Competition.DoesNotExist:
        competition = Competition.objects.create(
            name='Torneo APSAN 2025',
            location='La Paz, Bolivia',
            description='Torneo oficial de la Asociación Paceña de Salto y Adiestramiento',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            status='active',
            creator=admin
        )
        print(f"✓ Competencia creada")

    # 4. Asignar jueces a la competencia
    for i, judge in enumerate(judges):
        is_head = (i == 0)  # Primer juez es el principal
        CompetitionJudge.objects.get_or_create(
            competition=competition,
            judge=judge,
            defaults={'is_head_judge': is_head}
        )
    print(f"✓ Jueces asignados a la competencia")

    # 5. Crear parámetros de evaluación FEI
    parameters = []
    parameter_data = [
        {'name': 'Entrada al trote reunido', 'coefficient': 1, 'description': 'Evaluación de la entrada al rectángulo al trote reunido'},
        {'name': 'Parada, inmovilidad, saludo', 'coefficient': 2, 'description': 'Evaluación de la calidad de la parada, inmovilidad y saludo inicial'},
        {'name': 'Paso medio', 'coefficient': 1, 'description': 'Evaluación del paso medio, regularidad, elasticidad'},
        {'name': 'Paso extendido', 'coefficient': 2, 'description': 'Evaluación del paso extendido, cobertura de terreno'},
        {'name': 'Trote reunido', 'coefficient': 1, 'description': 'Evaluación del trote reunido, elasticidad y suspensión'},
        {'name': 'Trote medio', 'coefficient': 1, 'description': 'Evaluación del trote medio, amplitud y tempo'},
        {'name': 'Trote extendido', 'coefficient': 2, 'description': 'Evaluación del trote extendido, máxima cobertura de terreno'},
        {'name': 'Galope reunido', 'coefficient': 1, 'description': 'Evaluación del galope reunido, impulsión y cadencia'},
        {'name': 'Galope extendido', 'coefficient': 2, 'description': 'Evaluación del galope extendido, equilibrio y alargamiento'},
        {'name': 'Transiciones', 'coefficient': 3, 'description': 'Evaluación de las transiciones entre aires'}
    ]
    
    for param_info in parameter_data:
        param, created = EvaluationParameter.objects.get_or_create(
            name=param_info['name'],
            defaults={
                'coefficient': param_info['coefficient'],
                'description': param_info['description'],
                'max_value': 10  # Valor estándar FEI
            }
        )
        if created:
            print(f"✓ Parámetro '{param_info['name']}' creado")
        parameters.append(param)

    # 6. Asociar parámetros a la competencia
    for i, param in enumerate(parameters):
        CompetitionParameter.objects.get_or_create(
            competition=competition,
            parameter=param,
            defaults={'order': i+1}
        )
    print(f"✓ Parámetros asociados a la competencia")

    # 7. Crear jinetes
    riders = []
    rider_data = [
        {'first_name': 'Carlos', 'last_name': 'Montaño', 'nationality': 'Bolivia', 'gender': 'M'},
        {'first_name': 'María', 'last_name': 'Fernández', 'nationality': 'Bolivia', 'gender': 'F'},
        {'first_name': 'Juan', 'last_name': 'Pérez', 'nationality': 'Bolivia', 'gender': 'M'},
        {'first_name': 'Ana', 'last_name': 'Sánchez', 'nationality': 'Bolivia', 'gender': 'F'},
        {'first_name': 'Diego', 'last_name': 'Vargas', 'nationality': 'Bolivia', 'gender': 'M'}
    ]
    
    for rider_info in rider_data:
        rider, created = Rider.objects.get_or_create(
            first_name=rider_info['first_name'],
            last_name=rider_info['last_name'],
            defaults={
                'nationality': rider_info['nationality'],
                'gender': rider_info['gender']
            }
        )
        if created:
            print(f"✓ Jinete {rider_info['first_name']} {rider_info['last_name']} creado")
        riders.append(rider)

    # 8. Crear caballos
    horses = []
    horse_data = [
        {'name': 'Tornado', 'breed': 'Andaluz', 'color': 'Negro', 'birth_year': 2018},
        {'name': 'Luna', 'breed': 'Lusitano', 'color': 'Blanco', 'birth_year': 2017},
        {'name': 'Trueno', 'breed': 'Pura Sangre', 'color': 'Zaino', 'birth_year': 2016},
        {'name': 'Canela', 'breed': 'Criollo', 'color': 'Alazán', 'birth_year': 2019},
        {'name': 'Relámpago', 'breed': 'Warmblood', 'color': 'Bayo', 'birth_year': 2015}
    ]
    
    for horse_info in horse_data:
        horse, created = Horse.objects.get_or_create(
            name=horse_info['name'],
            defaults={
                'breed': horse_info['breed'],
                'color': horse_info['color'],
                'birth_year': horse_info['birth_year']
            }
        )
        if created:
            print(f"✓ Caballo {horse_info['name']} creado")
        horses.append(horse)

    # 9. Crear participantes
    for i, (rider, horse) in enumerate(zip(riders, horses)):
        category = categories[i % len(categories)]
        participant, created = Participant.objects.get_or_create(
            competition=competition,
            rider=rider,
            horse=horse,
            defaults={
                'category': category,
                'number': i+1,
                'order': i+1
            }
        )
        if created:
            print(f"✓ Participante {rider.first_name} con {horse.name} creado")
    
    return competition

# Función para sincronizar con Firebase
def sync_with_firebase(competition_id):
    print("\nSincronizando datos con Firebase...")
    
    try:
        # Importar funciones de sincronización
        from judging.firebase import initialize_firebase, sync_rankings
        
        # Inicializar Firebase
        if initialize_firebase():
            print("✓ Firebase inicializado correctamente")
            
            # Crear estructura base en Firebase si es necesario
            from firebase_admin import db
            root_ref = db.reference('/')
            
            # Verificar si ya hay datos
            data = root_ref.get()
            if not data:
                # Crear estructura base
                root_ref.set({
                    'system': {
                        'status': 'initialized',
                        'lastUpdate': {'.sv': 'timestamp'}
                    }
                })
                print("✓ Estructura base creada en Firebase")
            
            # Sincronizar rankings
            if sync_rankings(competition_id):
                print(f"✓ Rankings sincronizados para competencia {competition_id}")
            else:
                print(f"× Error al sincronizar rankings")
                
            return True
        else:
            print("× Error al inicializar Firebase")
            return False
            
    except Exception as e:
        print(f"× Error durante la sincronización con Firebase: {e}")
        return False

# Ejecutar inicialización
if __name__ == "__main__":
    # Paso 1: Inicializar datos en Django
    competition = initialize_django_data()
    
    # Paso 2: Sincronizar con Firebase
    if competition:
        sync_success = sync_with_firebase(competition.id)
        
        if sync_success:
            print("\n✅ Inicialización completa. El sistema está listo.")
        else:
            print("\n⚠️ Datos creados en Django pero hubo errores en la sincronización con Firebase.")
    else:
        print("\n❌ Error al inicializar datos en Django.")