# test_firebase_connection.py
import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecuestre_project.settings')
django.setup()

# Importar funciones a probar
from judging.firebase import initialize_firebase, verify_firebase_connection

def run_test():
    print("=== Prueba de Conexión a Firebase ===")
    
    # Inicializar Firebase
    print("Inicializando Firebase...")
    initialization_result = initialize_firebase()
    print(f"¿Firebase inicializado correctamente?: {initialization_result}")
    
    # Verificar conexión
    print("\nVerificando conexión con Firebase...")
    connection_status = verify_firebase_connection()
    print(f"Estado de conexión: {connection_status}")

if __name__ == "__main__":
    run_test()