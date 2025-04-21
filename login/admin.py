from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseForbidden
from .models import Profile

@admin.action(description = "Promote selected users to Librarian")
def promote_to_librarian(modeladmin, request, queryset):
    for user in queryset:
        user.profile.role = "librarian"
        user.profile.save()

@admin.action(description = "Demote selected users to Patron")
def demote_to_patron(modeladmin, request, queryset):
    for user in queryset:
        user.profile.role = "patron"
        user.profile.save()

class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "user_role")
    actions = [promote_to_librarian, demote_to_patron]

    def has_module_permission(self, request):
        """Deny access to non-superusers"""
        if not request.user.is_superuser:
            return False
        return True

    def user_role(self, obj):
        return obj.profile.role.capitalize() if obj.profile.role else "No Role"
    user_role.short_description = "User Role"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)