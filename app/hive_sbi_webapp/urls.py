"""hive_sbi_webapp URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include

from hive_sbi_webapp.webapp.views import (HomeView,
                                          UserInfoView,
                                          TransactionHistory,
                                          EnrolledHiveSBI,
                                          SponsoredHiveSBI,
                                          DeliveredVotesView)

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        '',
        HomeView.as_view(),
        name='home',
    ),

    path(
        'userinfo/',
        UserInfoView.as_view(),
        name='userinfo_form',
    ),

    path(
        'transaction-history/',
        TransactionHistory.as_view(),
        name='transaction_history',
    ),

    path(
        'transaction-history/enrolled-hive-SBI/',
        EnrolledHiveSBI.as_view(),
        name='enrolled_hive_sbi',
    ),

    path(
        'transaction-history/sponsored-hive-SBI/',
        SponsoredHiveSBI.as_view(),
        name='sponsored_hive_sbi',
    ),

    path(
        'delivered-votes/',
        DeliveredVotesView.as_view(),
        name='delivered_votes',
    ),
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
