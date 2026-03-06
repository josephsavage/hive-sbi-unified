import json
import logging
import requests

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .viewmixins import BaseMixinView
from .forms import UserInfoForm  # Corrected UseInfoForm to UserInfoForm


logger = logging.getLogger('webapp')


class HomeView(BaseMixinView, TemplateView):
    template_name = "webapp/home.html"  # Corrected templatename

    # Corrected getcontextdata to standard Django get_context_data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_home'] = True
        return context


class UserInfoView(BaseMixinView, TemplateView):  # Renamed from UserInfoForm to avoid collision with the actual form
    template_name = "webapp/userinfoform.html"  # Corrected templatename

    def get_user(self, **kwargs):
        return self.request.GET.get('user')

    # Aligned method name with how it is called in get_context_data
    def get_userinfo_form(self, **kwargs):
        user = self.get_user()
        initial = {}

        if user:
            initial = {'user': user}

        return UserInfoForm(initial=initial)

    def get_userinfo(self):
        user = self.request.GET.get("user", "").strip().lower()
        if not user:
            return {
                "success": False,
                "data": None,
                "error": "No user provided",
                "status": None,
            }

        url = f"{settings.SBIAPIURL}/getUserInfo?user={user}"

        try:
            r = requests.get(url, timeout=10)
            content = r.json()
        except Exception:
            return {
                "success": False,
                "data": None,
                "error": "API unreachable",
                "status": None,
            }

        # --- CASE 1: Legacy v0 response (raw fields, no wrapper) ---
        if isinstance(content, dict) and "shares" in content and "totalShares" in content:
            return {
                "success": True,
                "data": content,   # raw v0 data
                "error": None,
                "status": None,    # v0 has no status block
            }

        # --- CASE 2: Unified wrapper (if ever added later) ---
        if isinstance(content, dict) and "success" in content:
            return {
                "success": content.get("success", False),
                "data": content.get("data"),
                "error": content.get("error"),
                "status": content.get("status"),
            }

        # --- CASE 3: Unexpected format ---
        return {
            "success": False,
            "data": None,
            "error": "Unexpected API response",
            "status": None,
        }

    # Aligned method name with how it is called in get_context_data
    def get_userinfo_hive(self, **kwargs):
        user = self.get_user()
        userinfo_hive = None

        if not user:
            return userinfo_hive

        userinfo_hive = {
            "status_code": None,
            "success": False,
            "data": None,
            "error": None,
        }

        try:
            response = requests.get(
                "{}/users/{}/".format(settings.SBIAPIURL_V1, user),
                timeout=10,
            )
        except requests.exceptions.RequestException:
            userinfo_hive["error"] = "Connection Error"
            return userinfo_hive

        # Fixed variable typo from userinfohive to userinfo_hive
        userinfo_hive["status_code"] = response.status_code

        if response.status_code == 200:
            try:
                content = json.loads(response.content.decode("utf-8"))
            except (ValueError, TypeError):
                userinfo_hive["error"] = "Invalid JSON from Hive API"
                return userinfo_hive

            if isinstance(content, dict) and "success" in content:
                userinfo_hive["success"] = content.get("success", False)
                if userinfo_hive["success"]:
                    userinfo_hive["data"] = content.get("data")
                else:
                    userinfo_hive["error"] = content.get("error")
            elif isinstance(content, dict) and "shares" in content:
                userinfo_hive["success"] = True
                userinfo_hive["data"] = content
            else:
                userinfo_hive["error"] = "Unexpected API response"

        return userinfo_hive

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_userinfo'] = True
        context['user'] = self.get_user()
        context['userinfoform'] = self.get_userinfo_form()

        context['userinfo'] = self.get_userinfo()
        context['userinfohive'] = self.get_userinfo_hive()

        return context


class TransactionHistory(BaseMixinView, TemplateView):
    template_name = "webapp/transactionhistory.html"

    def get_user(self, **kwargs):
        return self.request.GET.get('user')

    def get_userinfo_form(self, **kwargs):
        user = self.get_user()
        initial = {}

        if user:
            initial = {'user': user}

        return UserInfoForm(initial=initial)

    # Fixed args/kwargs signature for standard Django get()
    def get(self, request, *args, **kwargs):
        if self.get_user():
            response = redirect('enrolledhivesbi')
            response['Location'] += '?user={}'.format(self.get_user())
            return response

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activetransactionhistory'] = True
        context['activeenrolledhive_sbi'] = False
        context['activesponsoredhive_sbi'] = False

        context['userinfoform'] = self.get_userinfo_form()
        context['user'] = self.get_user()

        return context


class EnrolledHiveSBI(TransactionHistory):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)  # Fixed rendertoresponse typo

    # Aligned method name
    def get_enrolled_hive_sbi(self, **kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        enrolledhive_sbi = {
            "status_code": None,
            "previous": None,
            "next": None,
            "activepagenumber": None,
            "prevpagenumber": None,
            "nextpagenumber": None,
        }

        try:
            params = "?account={}".format(self.get_user())

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/transactions/{}".format(settings.SBIAPIURL_V1, params),
                timeout=10,
            )

            enrolledhive_sbi["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content.get("previous"):
                    enrolledhive_sbi["previous"] = content["previous"].split(
                        "?")[1].replace('account=', 'user=')

                if content.get("next"):
                    enrolledhive_sbi["next"] = content["next"].split(
                        "?")[1].replace('account=', 'user=')

                activepagenumber = offset / LIMIT + 1

                enrolledhive_sbi["activepagenumber"] = int(activepagenumber)
                enrolledhive_sbi["prevpagenumber"] = int(activepagenumber - 1)

                if offset + 200 < content.get("count", 0):
                    enrolledhive_sbi["nextpagenumber"] = int(activepagenumber + 1)

                enrolledhive_sbi["results"] = content.get("results", [])

        except requests.exceptions.ConnectionError:
            enrolledhive_sbi["content"] = "Connection Error"

        return enrolledhive_sbi

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activeenrolledhive_sbi'] = True
        context['trxlist'] = self.get_enrolled_hive_sbi()
        return context


class SponsoredHiveSBI(TransactionHistory):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    # Aligned method name
    def get_sponsored_hive_sbi(self, **kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        sponsoredhive_sbi = {
            "status_code": None,
            "previous": None,
            "next": None,
            "activepagenumber": None,
            "prevpagenumber": None,
            "nextpagenumber": None,
        }

        try:
            params = "?sponsee={}".format(self.get_user())

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/transactions/{}".format(settings.SBIAPIURL_V1, params),
                timeout=10,
            )

            sponsoredhive_sbi["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content.get("previous"):
                    sponsoredhive_sbi["previous"] = content["previous"].split(
                        "?")[1].replace('sponsee=', 'user=')

                if content.get("next"):
                    sponsoredhive_sbi["next"] = content["next"].split(
                        "?")[1].replace('sponsee=', 'user=')

                activepagenumber = offset / LIMIT + 1

                sponsoredhive_sbi["activepagenumber"] = int(activepagenumber)
                sponsoredhive_sbi["prevpagenumber"] = int(activepagenumber - 1)

                if offset + 200 < content.get("count", 0):
                    sponsoredhive_sbi["nextpagenumber"] = int(activepagenumber + 1)

                sponsoredhive_sbi["results"] = content.get("results", [])

        except requests.exceptions.ConnectionError:
            sponsoredhive_sbi["content"] = "Connection Error"

        return sponsoredhive_sbi

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activesponsoredhive_sbi'] = True
        context['trxlist'] = self.get_sponsored_hive_sbi()
        return context


class DeliveredVotesView(BaseMixinView, TemplateView):
    template_name = "webapp/deliveredvotes.html"

    def get_user(self, **kwargs):
        if self.request.GET.get('user'):
            return self.request.GET.get('user')

        return self.request.GET.get('author')

    def get_userinfo_form(self, **kwargs):
        user = self.get_user()
        initial = {}

        if user:
            initial = {'user': user}

        return UserInfoForm(initial=initial)

    def get_posts(self, **kwargs):
        LIMIT = 200

        ordering = self.request.GET.get("ordering", "")

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        posts = {
            "status_code": None,
            "previous": None,
            "next": None,
            "activepagenumber": None,
            "prevpagenumber": None,
            "nextpagenumber": None,
        }

        try:
            if ordering:
                params = "?ordering={}".format(ordering)
            else:
                params = "?ordering=-created"

            if self.get_user():
                params = "{}&author={}".format(params, self.get_user())

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/posts/{}".format(settings.SBIAPIURL_V1, params),
                timeout=10,
            )

            posts["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content.get("previous"):
                    posts["previous"] = content["previous"].split(
                        "?")[1].replace('account=', 'author=')

                if content.get("next"):
                    posts["next"] = content["next"].split(
                        "?")[1].replace('account=', 'author=')

                activepagenumber = offset / LIMIT + 1

                posts["activepagenumber"] = int(activepagenumber)
                posts["prevpagenumber"] = int(activepagenumber - 1)

                if offset + 200 < content.get("count", 0):
                    posts["nextpagenumber"] = int(activepagenumber + 1)

                posts["results"] = content.get("results", [])

        except requests.exceptions.ConnectionError:
            posts["content"] = "Connection Error"

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activetransactionhistory'] = False
        context['activeenrolledhive_sbi'] = False
        context['activesponsoredhive_sbi'] = False

        context['userinfoform'] = self.get_userinfo_form()
        context['user'] = self.get_user()
        context['posts'] = self.get_posts()

        ordering = self.request.GET.get("ordering", "")

        if not ordering:
            context['createddescendingactive'] = True

        if ordering == "created":
            context['createdascendingactive'] = True
        if ordering == "-created":
            context['createddescendingactive'] = True

        return context
            
