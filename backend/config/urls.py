# backend/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
   openapi.Info(
      title="Sistema Ecuestre APSAN API",
      default_version='v1',
      description="API para la gestión de competencias ecuestres de APSAN",
      terms_of_service="https://www.sistemapsan.com/terms/",
      contact=openapi.Contact(email="contact@sistemapsan.com"),
      license=openapi.License(name="Licencia Privada"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # Documentación de API
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Autenticación JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # APIs de las aplicaciones
    path('api/usuarios/', include('usuarios.urls')),
    path('api/competencias/', include('competencias.urls')),
    path('api/evaluaciones/', include('evaluaciones.urls')),
    path('api/rankings/', include('rankings.urls')),
]

# Configuración para servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)