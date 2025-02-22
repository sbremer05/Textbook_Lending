from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return resolve_url("post_login")  # Uses the named URL from urls.py
