# app/hive_sbi_api/v0/router.py

from rest_framework import routers
from .views import MemberViewSet
from .views import legacy_get_user_info

router = routers.DefaultRouter()
router.register(r'users', MemberViewSet)

api_v0_urlpatterns = router.urls
