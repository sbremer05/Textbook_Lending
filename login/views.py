from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Profile

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
        return render(request, 'dashboard_librarian.html', {'user': request.user})
    else:
        return render(request, 'dashboard_patron.html', {'user': request.user})
