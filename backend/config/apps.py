# backend/config/apps.py

from django.apps import AppConfig

class ConfigAppConfig(AppConfig):
    name = 'config'
    verbose_name = "Configuración del Sistema"

    def ready(self):
        """
        Este método se ejecuta cuando la aplicación está inicializada
        y es el lugar adecuado para conectar señales y realizar otras
        tareas de inicialización.
        """
        # Importar y conectar señales
        from config.settings import connect_signals
        connect_signals()
        
        # Configurar logging adicional si es necesario
        import logging
        logger = logging.getLogger("config")
        logger.info("Sistema Ecuestre APSAN inicializado correctamente.")
        
        # Verificar configuración de caché
        from django.core.cache import cache
        try:
            cache.set('cache_test', 'ok', 10)
            result = cache.get('cache_test')
            if result == 'ok':
                logger.info("Sistema de caché funciona correctamente.")
            else:
                logger.warning("Sistema de caché no funciona como se esperaba.")
        except Exception as e:
            logger.error(f"Error en la configuración de caché: {e}")
        
        # Registrar middleware personalizado si es necesario