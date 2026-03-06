"""hive_sbi_api URL Configuration
app/hive_sbi_api/urls.py

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include
from django.views.generic import RedirectView

from hive_sbi_api.v0.router import api_v0_urlpatterns as api_v0
from hive_sbi_api.v1.router import api_v1_urlpatterns as api_v1


schema_view = get_schema_view(
    openapi.Info(
        title="Hive - SBI API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='docs')),
    path('docs/', schema_view.with_ui()),
    path("getUserInfo", legacy_get_user_info),
    path('', include((api_v0, 'v0'), namespace='v0')),
    path('v1/', include((api_v1, 'v1'), namespace='v1')),
]

if settings.DEBUG:

    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
