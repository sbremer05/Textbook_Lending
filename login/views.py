from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile

# Home view (Debugging included)
def home(request):
    print(f"User authenticated? {request.user.is_authenticated}")  # Debugging

    if request.user.is_authenticated:
        print(f"User {request.user.username} is logged in!")  # Debugging
        print("Redirecting to post-login check...")  # Debugging
        return redirect('post_login_redirect')  # Redirect to check role

    return render(request, "login/home.html")

# Logout view
def logout_view(request):
    logout(request)
    return redirect("/")

# Post-login redirection: Checks if user needs to select a role
@login_required
def post_login_redirect(request):
    user = request.user
    social_account = SocialAccount.objects.filter(user=user, provider='google').first()

    if social_account:
        profile, created = Profile.objects.get_or_create(user=user)

        if created or not profile.is_setup:
            print(f"User {user.username} needs to choose a role.")
            return redirect("choose_role")  # Named URL for choosing role

        print(f"Redirecting {user.username} to their dashboard ({profile.role})")
        return redirect("librarian_dashboard" if profile.role == "librarian" else "patron_dashboard")

    return redirect("/")

# Choose role view: Allows user to set Patron or Librarian role
@login_required
def choose_role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role in ["patron", "librarian"]:
            profile = request.user.profile
            profile.role = role
            profile.is_setup = True
            profile.save()
            print(f"User {request.user.username} selected role: {role}")
            return redirect("librarian_dashboard" if profile.role == "librarian" else "patron_dashboard")

    return render(request, "login/choose_role.html")

# Patron Dashboard
@login_required
def patron_dashboard(request):
    return render(request, "login/dashboard_patron.html", {"user": request.user})

# Librarian Dashboard
@login_required
def librarian_dashboard(request):
    return render(request, "login/dashboard_librarian.html", {"user": request.user})
