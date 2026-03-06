# app/hivesbiwebapp/webapp/views.py

import json
import logging
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.shortcuts import render
from utils.metabase import signeddashboardurl

from .viewmixins import BaseMixinView
from .forms import UseInfoForm


logger = logging.getLogger('webapp')


class HomeView(BaseMixinView, TemplateView):
    template_name = "webapp/home.html"

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['active_home'] = True
        return context


class UserInfoForm(BaseMixinView, TemplateView):
    templatename = "webapp/userinfoform.html"

    def get_user(self, kwargs):
        return self.request.GET.get('user')

    def getuserinfoform(self, kwargs):
        user = self.get_user()

        initial = {}

        if user:
            initial = {'user': user}

        return UseInfoForm(initial=initial)

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

    def getuserinfohive(self, kwargs):
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

        userinfohive["statuscode"] = response.status_code

        if response.status_code == 200:
            try:
                content = json.loads(response.content.decode("utf-8"))
            except (ValueError, TypeError):
                userinfo_hive["error"] = "Invalid JSON from Hive API"
                return userinfo_hive

            # If the v1 endpoint returns the unified wrapper
            if isinstance(content, dict) and "success" in content:
                userinfo_hive["success"] = content.get("success", False)
                if userinfo_hive["success"]:
                    userinfo_hive["data"] = content.get("data")
                else:
                    userinfo_hive["error"] = content.get("error")
            # If v1 returns raw member data (fallback)
            elif isinstance(content, dict) and "shares" in content:
                userinfo_hive["success"] = True
                userinfo_hive["data"] = content
            else:
                userinfo_hive["error"] = "Unexpected API response"

        return userinfo_hive

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['active_userinfo'] = True
        context['user'] = self.get_user()
        context['userinfoform'] = self.getuserinfo_form()

        context['userinfo'] = self.get_userinfo()
        context['userinfohive'] = self.getuserinfo_hive()

        return context


Removed RichListView per project decision to replace with Metabase dashboards.

If you later want a server-side rich list, reintroduce a dedicated view here.

Remaining views below unchanged (kept for completeness).


class TransactionHistory(BaseMixinView, TemplateView):
    templatename = "webapp/transactionhistory.html"

    def get_user(self, kwargs):
        return self.request.GET.get('user')

    def getuserinfoform(self, kwargs):
        user = self.get_user()

        initial = {}

        if user:
            initial = {'user': user}

        return UseInfoForm(initial=initial)

    def get(self, request, args, *kwargs):
        if self.get_user():
            response = redirect('enrolledhivesbi')
            response['Location'] += '?user={}'.format(self.get_user())

            return response

        return super().get(request, args, *kwargs)

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['activetransactionhistory'] = True
        context['activeenrolledhive_sbi'] = False
        context['activesponsoredhive_sbi'] = False

        context['userinfoform'] = self.getuserinfo_form()
        context['user'] = self.get_user()

        return context


class EnrolledHiveSBI(TransactionHistory):
    def get(self, request, args, *kwargs):
        context = self.getcontextdata(kwargs)
        return self.rendertoresponse(context)

    def getenrolledhive_sbi(self, kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        enrolledhivesbi = {
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

            enrolledhivesbi["statuscode"] = response.statuscode

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content.get("previous"):
                    enrolledhivesbi["previous"] = content["previous"].split(
                        "?")[1].replace('account=', 'user=')

                if content.get("next"):
                    enrolledhivesbi["next"] = content["next"].split(
                        "?")[1].replace('account=', 'user=')

                activepagenumber = offset / LIMIT + 1

                enrolledhivesbi["activepagenumber"] = int(activepagenumber)
                enrolledhivesbi["prevpagenumber"] = int(activepagenumber - 1)

                if offset + 200 < content.get("count", 0):
                    enrolledhivesbi["nextpagenumber"] = int(activepagenumber + 1)

                enrolledhivesbi["results"] = content.get("results", [])

        except requests.exceptions.ConnectionError:
            enrolledhivesbi["content"] = "Connection Error"

        return enrolledhivesbi

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['activeenrolledhive_sbi'] = True

        context['trxlist'] = self.getenrolledhivesbi()

        return context


class SponsoredHiveSBI(TransactionHistory):
    def get(self, request, args, *kwargs):
        context = self.getcontextdata(kwargs)
        return self.rendertoresponse(context)

    def getsponsoredhive_sbi(self, kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        sponsoredhivesbi = {
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

            sponsoredhivesbi["statuscode"] = response.statuscode

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content.get("previous"):
                    sponsoredhivesbi["previous"] = content["previous"].split(
                        "?")[1].replace('sponsee=', 'user=')

                if content.get("next"):
                    sponsoredhivesbi["next"] = content["next"].split(
                        "?")[1].replace('sponsee=', 'user=')

                activepagenumber = offset / LIMIT + 1

                sponsoredhivesbi["activepagenumber"] = int(activepagenumber)
                sponsoredhivesbi["prevpagenumber"] = int(activepagenumber - 1)

                if offset + 200 < content.get("count", 0):
                    sponsoredhivesbi["nextpagenumber"] = int(activepagenumber + 1)

                sponsoredhivesbi["results"] = content.get("results", [])

        except requests.exceptions.ConnectionError:
            sponsoredhivesbi["content"] = "Connection Error"

        return sponsoredhivesbi

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['activesponsoredhive_sbi'] = True

        context['trxlist'] = self.getsponsoredhivesbi()

        return context


class DeliveredVotesView(BaseMixinView, TemplateView):
    templatename = "webapp/deliveredvotes.html"

    def get_user(self, kwargs):
        if self.request.GET.get('user'):
            return self.request.GET.get('user')

        return self.request.GET.get('author')

    def getuserinfoform(self, kwargs):
        user = self.get_user()

        initial = {}

        if user:
            initial = {'user': user}

        return UseInfoForm(initial=initial)

    def get_posts(self, kwargs):
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

            posts["statuscode"] = response.statuscode

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

    def getcontextdata(self, kwargs):
        context = super().getcontextdata(kwargs)
        context['activetransactionhistory'] = False
        context['activeenrolledhive_sbi'] = False
        context['activesponsoredhive_sbi'] = False

        context['userinfoform'] = self.getuserinfo_form()
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
