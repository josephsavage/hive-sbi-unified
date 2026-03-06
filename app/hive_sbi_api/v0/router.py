# app/hive_sbi_api/v0/router.py

from django.urls import path
from rest_framework import routers

from .views import MemberViewSet, legacy_get_user_info

router = routers.DefaultRouter()
router.register(r'users', MemberViewSet)

# Combine router-generated URLs with manual legacy endpoints
api_v0_urlpatterns = [
    path("getUserInfo", legacy_get_user_info),
]

# Append router URLs (users/, users/<pk>/, etc.)
api_v0_urlpatterns += router.urls
