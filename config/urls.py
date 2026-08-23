"""URL configuration for config project.

Las rutas de documentación se montan solo si `DOCS_ENABLED` está activo. Con
la bandera apagada no se importa drf-spectacular ni se registra ninguna URL de
docs, así que la generación del esquema no ocurre nunca en runtime.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('products.api.urls')),
]

if settings.DOCS_ENABLED:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path(
            'api/docs/',
            SpectacularSwaggerView.as_view(url_name='schema'),
            name='swagger-ui',
        ),
        path(
            'api/redoc/',
            SpectacularRedocView.as_view(url_name='schema'),
            name='redoc',
        ),
    ]
