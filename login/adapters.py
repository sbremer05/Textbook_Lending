from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import resolve_url
from allauth.exceptions import ImmediateHttpResponse

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return resolve_url("post_login")

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        messages.error(request, "Third-party login failed. Please try again.")
        raise ImmediateHttpResponse(redirect("home"))