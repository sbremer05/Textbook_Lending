from bs4.diagnose import profile
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile
from django.http import HttpResponse
# Create your views here.

def home(request):
    print(f"User authenticated? {request.user.is_authenticated}")  # Debugging

    if request.user.is_authenticated:
        print(f"User {request.user.username} is logged in!")  # Debugging
        print("Redirecting to dashboard...")  # Debugging
        return redirect('dashboard')  # Force redirect if logged in

    return render(request, "login/home.html")

# Logout view
def logout_view(request):
    logout(request)
    return redirect("/")

# Dashboard view with role-based redirection
@login_required
def dashboard(request):
    print(f"User {request.user.username} is logged in")
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role == 'librarian':
        return render(request, 'login/dashboard_librarian.html', {'user': request.user})
    else:
        return render(request, 'login/dashboard_patron.html', {'user': request.user})

@login_required
def post_login_redirect(request):
    user = request.user
    social_account = SocialAccount.objects.filter(user=user, provider='google').first()

    if social_account:
        profile, created = Profile.objects.get_or_create(user=user)

        if created or not profile.is_setup:
            return redirect("/choose-role/")

        return redirect("/librarian-dashboard/" if profile.role == "librarian" else "/patron-dashboard/")

    return redirect("/")

@login_required
def patron_dashboard(request):
    return render(request, "patron_dashboard.html", {"user": request.user})

@login_required
def librarian_dashboard(request):
    return render(request, "librarian_dashboard.html", {"user": request.user})

@login_required
def choose_role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role in ["patron", "librarian"]:
            profile = request.user.profile
            profile.role = role
            profile.is_setup = True
            profile.save()
            return redirect("/librarian-dashboard/" if profile.role == "librarian" else "/patron-dashboard/")

    return render(request, "choose_role.html")