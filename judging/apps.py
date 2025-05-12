from django.apps import AppConfig


class JudgingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'judging'
    
    def ready(self):
        """Conectar señales cuando la aplicación está lista"""
        try:
            from . import signals
            signals.connect_signals()
        except ImportError:
            pass