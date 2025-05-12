from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class JudgingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'judging'
    
    def ready(self):
        """Conectar señales e inicializar integración en tiempo real cuando la aplicación está lista"""
        try:
            # Conectar señales
            from . import signals
            signals.connect_signals()
            
            # Inicializar Firebase
            from .firebase import initialize_firebase
            firebase_initialized = initialize_firebase()
            if firebase_initialized:
                logger.info("Firebase inicializado correctamente en arranque")
                
                # Inicializar listeners de Firebase (solo en servidor de producción)
                import os
                if os.environ.get('DJANGO_ENV') == 'production':
                    from .realtime import initialize_firebase_listeners
                    initialize_firebase_listeners()
            else:
                logger.warning("Firebase no se pudo inicializar en arranque")
                
        except ImportError as e:
            logger.error(f"Error al importar módulos necesarios: {e}")
        except Exception as e:
            logger.error(f"Error general en ready(): {e}")