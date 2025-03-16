from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseForbidden
from .models import Profile

# Register your models here.

class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        """Deny access to non-superusers"""
        if not request.user.is_superuser:
            return False
        return True

admin.site.register(Profile)