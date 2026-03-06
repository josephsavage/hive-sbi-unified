# app/hive_sbi_webapp/webapp/views.py

import json
import logging
import requests

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.shortcuts import render
from utils.metabase import signed_dashboard_url

from .viewmixins import BaseMixinView
from .forms import UseInfoForm


logger = logging.getLogger('webapp')


class HomeView(BaseMixinView, TemplateView):
    template_name = "webapp/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_home'] = True
        return context


class UserInfoForm(BaseMixinView, TemplateView):
    template_name = "webapp/userinfo_form.html"

    def get_user(self, **kwargs):
        return self.request.GET.get('user')

    def get_userinfo_form(self, **kwargs):
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

    url = f"{settings.SBI_API_URL}/getUserInfo?user={user}"

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
    if "success" in content:
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

        #try:
        response = requests.get(
            "{}/users/{}/".format(settings.SBI_API_URL_V1, user),
        )

        userinfo_hive["status_code"] = response.status_code

        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))

            userinfo_hive["success"] = content["success"]

            if userinfo_hive["success"]:
                userinfo_hive["data"] = content["data"]
            else:
                userinfo_hive["error"] = content["error"]

        #except requests.exceptions.ConnectionError:
        #    userinfo_hive["error"] = "Connection Error"

        return userinfo_hive

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_userinfo'] = True
        context['user'] = self.get_user()
        context['userinfo_form'] = self.get_userinfo_form()

        context['userinfo'] = self.get_userinfo()
        context['userinfo_hive'] = self.get_userinfo_hive()

        return context


class RichListView(BaseMixinView, TemplateView):
    template_name = "webapp/rich_list.html"

    def get_richlist(self, **kwargs):
        LIMIT = 200

        ordering = self.request.GET.get("ordering", "")

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        richlist = {
            "status_code": None,
            "previous": None,
            "next": None,
            "active_page_number": None,
            "prev_page_number": None,
            "next_page_number": None,
        }

        try:
            params = ""

            if ordering:
                params = "?ordering={}".format(ordering)

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/members/{}".format(settings.SBI_API_URL_V1, params),
            )

            richlist["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content["previous"]:
                    richlist["previous"] = content["previous"].split("?")[1]

                if content["next"]:
                    richlist["next"] = content["next"].split("?")[1]

                active_page_number = offset / LIMIT + 1

                richlist["active_page_number"] = int(active_page_number)
                richlist["prev_page_number"] = int(active_page_number - 1)

                if offset + 200 < content["count"]:
                    richlist["next_page_number"] = int(active_page_number + 1)

                richlist["results"] = content["results"]

        except requests.exceptions.ConnectionError:
            richlist["content"] = "Connection Error"

        return richlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_richlist'] = True

        context['richlist'] = self.get_richlist()

        context['total_shares_ascending_active'] = False
        context['total_shares_descending_active'] = False
        context['shares_ascending_active'] = False
        context['shares_descending_active'] = False
        context['bonus_shares_ascending_active'] = False
        context['bonus_shares_descending_active'] = False
        context['pending_balance_ascending_active'] = False
        context['pending_balance_descending_active'] = False
        context['next_upvote_estimate_ascending_active'] = False
        context['next_upvote_estimate_descending_active'] = False
        context['estimate_rewarded_ascending_active'] = False
        context['estimate_rewarded_descending_active'] = False

        ordering = self.request.GET.get("ordering", "")

        if ordering == "total_shares":
            context['total_shares_ascending_active'] = True
        if ordering == "-total_shares":
            context['total_shares_descending_active'] = True

        if ordering == "shares":
            context['shares_ascending_active'] = True
        if ordering == "-shares":
            context['shares_descending_active'] = True

        if ordering == "bonus_shares":
            context['bonus_shares_ascending_active'] = True
        if ordering == "-bonus_shares":
            context['bonus_shares_descending_active'] = True

        if ordering == "pending_balance":
            context['pending_balance_ascending_active'] = True
        if ordering == "-pending_balance":
            context['pending_balance_descending_active'] = True

        if ordering == "next_upvote_estimate":
            context['next_upvote_estimate_ascending_active'] = True
        if ordering == "-next_upvote_estimate":
            context['next_upvote_estimate_descending_active'] = True

        if ordering == "estimate_rewarded":
            context['estimate_rewarded_ascending_active'] = True
        if ordering == "-estimate_rewarded":
            context['estimate_rewarded_descending_active'] = True

        return context


class TransactionHistory(BaseMixinView, TemplateView):
    template_name = "webapp/transaction_history.html"

    def get_user(self, **kwargs):
        return self.request.GET.get('user')

    def get_userinfo_form(self, **kwargs):
        user = self.get_user()

        initial = {}

        if user:
            initial = {'user': user}

        return UseInfoForm(initial=initial)

    def get(self, request, *args, **kwargs):
        if self.get_user():
            response = redirect('enrolled_hive_sbi')
            response['Location'] += '?user={}'.format(self.get_user())

            return response

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_transaction_history'] = True
        context['active_enrolled_hive_sbi'] = False
        context['active_sponsored_hive_sbi'] = False

        context['userinfo_form'] = self.get_userinfo_form()
        context['user'] = self.get_user()

        return context


class EnrolledHiveSBI(TransactionHistory):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_enrolled_hive_sbi(self, **kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        enrolled_hive_sbi = {
            "status_code": None,
            "previous": None,
            "next": None,
            "active_page_number": None,
            "prev_page_number": None,
            "next_page_number": None,
        }

        try:
            params = "?account={}".format(self.get_user())

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/transactions/{}".format(settings.SBI_API_URL_V1, params),
            )

            enrolled_hive_sbi["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content["previous"]:
                    enrolled_hive_sbi["previous"] = content["previous"].split(
                        "?")[1].replace('account=', 'user=')

                if content["next"]:
                    enrolled_hive_sbi["next"] = content["next"].split(
                        "?")[1].replace('account=', 'user=')

                active_page_number = offset / LIMIT + 1

                enrolled_hive_sbi["active_page_number"] = int(active_page_number)
                enrolled_hive_sbi["prev_page_number"] = int(active_page_number - 1)

                if offset + 200 < content["count"]:
                    enrolled_hive_sbi["next_page_number"] = int(active_page_number + 1)

                enrolled_hive_sbi["results"] = content["results"]

        except requests.exceptions.ConnectionError:
            enrolled_hive_sbi["content"] = "Connection Error"

        return enrolled_hive_sbi

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_enrolled_hive_sbi'] = True

        context['trx_list'] = self.get_enrolled_hive_sbi()

        return context


class SponsoredHiveSBI(TransactionHistory):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_sponsored_hive_sbi(self, **kwargs):
        LIMIT = 200

        try:
            offset = int(self.request.GET.get("offset", 0))
        except ValueError:
            offset = 0

        sponsored_hive_sbi = {
            "status_code": None,
            "previous": None,
            "next": None,
            "active_page_number": None,
            "prev_page_number": None,
            "next_page_number": None,
        }

        try:
            params = "?sponsee={}".format(self.get_user())

            if offset:
                if params:
                    params = "{}&offset={}".format(params, offset)
                else:
                    params = "?offset={}".format(offset)

            response = requests.get(
                "{}/v1/transactions/{}".format(settings.SBI_API_URL_V1, params),
            )

            sponsored_hive_sbi["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content["previous"]:
                    sponsored_hive_sbi["previous"] = content["previous"].split(
                        "?")[1].replace('sponsee=', 'user=')

                if content["next"]:
                    sponsored_hive_sbi["next"] = content["next"].split(
                        "?")[1].replace('sponsee=', 'user=')

                active_page_number = offset / LIMIT + 1

                sponsored_hive_sbi["active_page_number"] = int(active_page_number)
                sponsored_hive_sbi["prev_page_number"] = int(active_page_number - 1)

                if offset + 200 < content["count"]:
                    sponsored_hive_sbi["next_page_number"] = int(active_page_number + 1)

                sponsored_hive_sbi["results"] = content["results"]

        except requests.exceptions.ConnectionError:
            sponsored_hive_sbi["content"] = "Connection Error"

        return sponsored_hive_sbi

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sponsored_hive_sbi'] = True

        context['trx_list'] = self.get_sponsored_hive_sbi()

        return context


class DeliveredVotesView(BaseMixinView, TemplateView):
    template_name = "webapp/delivered_votes.html"

    def get_user(self, **kwargs):
        if self.request.GET.get('user'):
            return self.request.GET.get('user')

        return self.request.GET.get('author')

    def get_userinfo_form(self, **kwargs):
        user = self.get_user()

        initial = {}

        if user:
            initial = {'user': user}

        return UseInfoForm(initial=initial)

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
            "active_page_number": None,
            "prev_page_number": None,
            "next_page_number": None,
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
                "{}/v1/posts/{}".format(settings.SBI_API_URL_V1, params),
            )

            posts["status_code"] = response.status_code

            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))

                if content["previous"]:
                    posts["previous"] = content["previous"].split(
                        "?")[1].replace('account=', 'author=')

                if content["next"]:
                    posts["next"] = content["next"].split(
                        "?")[1].replace('account=', 'author=')

                active_page_number = offset / LIMIT + 1

                posts["active_page_number"] = int(active_page_number)
                posts["prev_page_number"] = int(active_page_number - 1)

                if offset + 200 < content["count"]:
                    posts["next_page_number"] = int(active_page_number + 1)

                posts["results"] = content["results"]

        except requests.exceptions.ConnectionError:
            posts["content"] = "Connection Error"

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_transaction_history'] = False
        context['active_enrolled_hive_sbi'] = False
        context['active_sponsored_hive_sbi'] = False

        context['userinfo_form'] = self.get_userinfo_form()
        context['user'] = self.get_user()
        context['posts'] = self.get_posts()

        ordering = self.request.GET.get("ordering", "")

        if not ordering:
            context['created_descending_active'] = True

        if ordering == "created":
            context['created_ascending_active'] = True
        if ordering == "-created":
            context['created_descending_active'] = True


        return context
