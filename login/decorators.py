from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles, redirect_to="patron_dashboard"):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]  # Allow single-role use

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            if hasattr(request.user, "profile") and request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return redirect(redirect_to)
        return _wrapped_view
    return decorator
