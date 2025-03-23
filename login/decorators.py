from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def role_required(*roles, redirect_to="post_login_redirect"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")
            if hasattr(request.user, "profile") and request.user.profile.role in roles:
                return view_func(request, *args, **kwargs)
            # Redirect to safe fallback if role doesn't match
            return redirect(redirect_to)
        return _wrapped_view
    return decorator
