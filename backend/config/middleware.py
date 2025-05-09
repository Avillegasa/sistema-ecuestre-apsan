# backend/config/middleware.py

import time
import logging
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class QueryCountMiddleware:
    """
    Middleware para contar y registrar el número de consultas SQL realizadas 
    durante una solicitud. Útil para identificar problemas de rendimiento.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Código ejecutado antes de la vista
        start_queries = len(connection.queries)
        start_time = time.time()
        
        # Llamar al siguiente middleware o a la vista
        response = self.get_response(request)
        
        # Código ejecutado después de la vista
        end_time = time.time()
        end_queries = len(connection.queries)
        
        # Calcular estadísticas
        duration = end_time - start_time
        num_queries = end_queries - start_queries
        
        # Establecer un umbral para registrar solicitudes con muchas consultas
        QUERY_THRESHOLD = 50
        
        # Si hay demasiadas consultas o la solicitud tomó mucho tiempo, registrar
        if num_queries > QUERY_THRESHOLD or duration > 1.0:
            logger.warning(
                f"Solicitud a {request.path} realizó {num_queries} consultas en {duration:.2f}s"
            )
            
            # En modo DEBUG, registrar detalles adicionales
            if settings.DEBUG:
                # Agrupar consultas duplicadas
                query_count = {}
                for query in connection.queries[start_queries:end_queries]:
                    sql = query['sql']
                    query_count[sql] = query_count.get(sql, 0) + 1
                
                # Registrar consultas que se repiten más de 3 veces
                duplicate_queries = {sql: count for sql, count in query_count.items() if count > 3}
                if duplicate_queries:
                    logger.warning(f"Consultas duplicadas detectadas: {duplicate_queries}")
        
        return response

class PerformanceMonitorMiddleware:
    """
    Middleware para monitorear el rendimiento de las solicitudes y establecer 
    encabezados con información de rendimiento en modo DEBUG.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Llamar al siguiente middleware o a la vista
        response = self.get_response(request)
        
        # Calcular duración
        duration = time.time() - start_time
        
        # Añadir encabezados con información de rendimiento en modo DEBUG
        if settings.DEBUG:
            response['X-Request-Time'] = f"{duration:.2f}s"
            response['X-Query-Count'] = str(len(connection.queries))
        
        # Registrar solicitudes lentas (más de 2 segundos)
        if duration > 2.0:
            logger.warning(
                f"Solicitud lenta detectada: {request.method} {request.path} - {duration:.2f}s"
            )
        
        return response

class SecurityHeadersMiddleware:
    """
    Middleware para añadir encabezados de seguridad adicionales a todas las respuestas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Añadir encabezados de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (CSP) para prevenir XSS
        if not settings.DEBUG:
            csp_value = (
                "default-src 'self'; "
                "img-src 'self' data:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )
            response['Content-Security-Policy'] = csp_value
        
        return response

# Para usar estos middlewares, agregar a settings.py:
"""
MIDDLEWARE = [
    # Django middlewares...
    'config.middleware.SecurityHeadersMiddleware',
    'config.middleware.PerformanceMonitorMiddleware',
    'config.middleware.QueryCountMiddleware',  # Sólo en desarrollo
]
"""