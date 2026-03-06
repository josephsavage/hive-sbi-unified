# app/hive_sbi_api/v0/views.py

import logging
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django_celery_results.models import TaskResult

from hive_sbi_api.core.models import Member
from .serializers import (
    UserSerializer,
    NotFoundSerializer,
    StatusSerializer,
    MemberSerializer,
)

logger = logging.getLogger("v0")


@api_view(["GET"])
def legacy_get_user_info(request):
    username = request.GET.get("user", "").lower()
    member = get_object_or_404(Member, account=username)
    return Response(MemberSerializer(member).data)


class MemberViewSet(RetrieveModelMixin, GenericViewSet):
    lookup_value_regex = r"[^/]+"
    lookup_field = "account"

    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    user_response = openapi.Response("response description", UserSerializer)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if lookup_url_kwarg not in self.kwargs:
            raise AssertionError(
                f"Expected view {self.__class__.__name__} to be called with "
                f"a URL keyword argument named '{lookup_url_kwarg}'."
            )

        filter_kwargs = {
            self.lookup_field: self.kwargs[lookup_url_kwarg].lower()
        }

        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def _get_last_sync_status(self):
        """
        Returns a dict compatible with StatusSerializer.
        Handles empty TaskResult table safely.
        """
        try:
            last_sync = (
                TaskResult.objects.filter(
                    task_name="hive_sbi_api.sbi.tasks.sync_members"
                )
                .latest("date_done")
            )
            last_updated = last_sync.date_done
        except TaskResult.DoesNotExist:
            last_updated = None

        if last_updated:
            next_exec = last_updated + timedelta(hours=2, minutes=24)
            now = timezone.now()
            waiting_minutes = int((next_exec - now).total_seconds() / 60)
        else:
            waiting_minutes = None

        return {
            "lastUpdatedTime": last_updated,
            "estimatedMinutesUntilNextUpdate": waiting_minutes,
            "maxSBIVote": 0,
        }

    @swagger_auto_schema(tags=["V0"], responses={200: user_response})
    def retrieve(self, request, *args, **kwargs):
        member = self.get_object()
        status_data = self._get_last_sync_status()
        status_serialized = StatusSerializer(status_data).data

        if member:
            member_data = self.get_serializer(member).data

            response = {
                "success": True,
                "data": member_data,
                "status": status_serialized,
            }

            return Response(UserSerializer(response).data)

        response = {
            "success": False,
            "error": "User doesn't have any shares or doesn't exist.",
            "status": status_serialized,
        }

        return Response(NotFoundSerializer(response).data)
