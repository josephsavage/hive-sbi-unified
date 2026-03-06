# app/hive_sbi_api/v0/router.py

from django.urls import path
from rest_framework import routers

from .views import MemberViewSet, legacy_get_user_info

# DRF router for standard v0 endpoints
router = routers.DefaultRouter()
router.register(r'users', MemberViewSet)

# Manual legacy endpoints (root-level)
api_v0_urlpatterns = [
    path("getUserInfo", legacy_get_user_info),
]

# Append router-generated URLs (users/, users/<pk>/, etc.)
api_v0_urlpatterns += router.urls
