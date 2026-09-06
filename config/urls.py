"""URL configuration for config project.

Two adapters sit on top of the same use cases: REST under /api/v1/ and
GraphQL under /graphql/. This module is the composition root of the web
layer — where the use cases are built and handed to each adapter.

The browsable interfaces —Swagger, Redoc and GraphiQL— are mounted only
when `DOCS_ENABLED` is on. With the flag off, drf-spectacular is never
imported and GraphiQL is not served, so neither schema generation nor the
explorer is reachable in production.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from products.api.graphql.schema import schema as graphql_schema
from products.api.graphql.view import ProductsGraphQLView

# The API is stateless and carries no cookie-based authentication, so there is
# no CSRF surface to protect: DRF already skips the check for the REST adapter
# for the same reason. Should session authentication ever be introduced, this
# exemption has to go.
graphql_view = csrf_exempt(
    ProductsGraphQLView.as_view(
        schema=graphql_schema,
        # None disables the explorer entirely; "graphiql" serves it.
        graphql_ide='graphiql' if settings.DOCS_ENABLED else None,
    )
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('products.api.urls')),
    path('graphql/', graphql_view, name='graphql'),
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
