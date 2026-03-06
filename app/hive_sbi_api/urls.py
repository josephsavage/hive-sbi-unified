"""
hive_sbi_api URL Configuration
app/hive_sbi_api/urls.py
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from hive_sbi_api.v0.router import api_v0_urlpatterns as api_v0
from hive_sbi_api.v1.router import api_v1_urlpatterns as api_v1


# --- Swagger / OpenAPI schema ---
schema_view = get_schema_view(
    openapi.Info(
        title="Hive - SBI API",
        default_version="v1",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# --- Root URL patterns ---
urlpatterns = [
    path("admin/", admin.site.urls),

    # Redirect root → docs
    path("", RedirectView.as_view(url="docs")),

    # Swagger UI
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),

    # V0 API (includes /getUserInfo and /users/<account>/)
    path("", include((api_v0, "v0"), namespace="v0")),

    # V1 API
    path("v1/", include((api_v1, "v1"), namespace="v1")),
]


# --- Debug-only additions ---
if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
