from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile
from .forms import ProfilePictureForm
from .decorators import role_required
from django.contrib.auth.models import User

# Home view (Debugging included)
def home(request):
    print(f"User authenticated? {request.user.is_authenticated}")  # Debugging

    if request.user.is_authenticated:
        print(f"User {request.user.username} is logged in!")  # Debugging
        print("Redirecting to post-login check...")  # Debugging
        return redirect('post_login_redirect')  # Redirect to check role

    return render(request, "login/home.html")

def guest_login(request):

    guest_user = User.objects.create_user(username=f"guest_{str(Profile.objects.count() + 1)}", email="guest@example.com")

    guest_profile, created = Profile.objects.get_or_create(user=guest_user)

    if created:
        guest_profile.is_guest = True
        guest_profile.save()

    guest_user.backend = 'django.contrib.auth.backends.ModelBackend'

    login(request, guest_user)

    return redirect('patron_dashboard')
    

# Logout view
def logout_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_guest:
        guest_profile = request.user.profile
        guest_profile.delete()  

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
            print(f"User {user.username} assigned default role: Patron.")
            profile.role = "patron"
            profile.is_setup = True
            profile.save()
            return redirect("patron_dashboard")

        print(f"Redirecting {user.username} to their dashboard ({profile.role})")
        return redirect("librarian_dashboard" if profile.role == "librarian" else "patron_dashboard")
    else:
        return redirect("/")

@login_required
def profile_picture_upload(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('patron_dashboard' if request.user.profile.role == 'patron' else 'librarian_dashboard')

    form = ProfilePictureForm(instance=request.user.profile)
    return render(request, "login/upload_profile_picture.html", {"form": form})

@login_required
def dashboard(request):
    """ Redirect users to the correct dashboard based on their role. """
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role == 'librarian':
        return redirect('librarian_dashboard')
    return redirect('patron_dashboard')

# Patron Dashboard
@role_required('patron', 'pending')
#@login_required
def patron_dashboard(request):
    return render(request, "login/dashboard_patron.html", {"user": request.user})

# Librarian Dashboard
@role_required('librarian')
#@login_required
def librarian_dashboard(request):
    return render(request, "login/dashboard_librarian.html", {"user": request.user})

# Librarian Requests Page - handles Pending Requests
@role_required('librarian')
#@login_required
def librarian_requests(request):
    if request.user.profile.role != "librarian":
        return redirect("patron_dashboard")  # Only librarians can access

    # Fetch pending requests along with user details
    pending_requests = Profile.objects.filter(role="pending").select_related("user")

    # Approve requests and reset page
    if request.method == "POST":
        user_id = request.POST.get("approve_user")
        if user_id:
            profile = Profile.objects.get(id=user_id)
            profile.role = "librarian"
            profile.save()
            return redirect("librarian_requests")

    return render(request, "login/librarian_requests.html", {"pending_requests": pending_requests})

# Request Librarian
@role_required('patron', 'pending')
#@login_required
def request_librarian(request):
    profile = request.user.profile
    if profile.role == "patron" or profile.role == "pending":
        profile.role = "pending"
        profile.save()
        messages.success(request, "Your request for librarian status has been submitted!")
    return redirect("patron_dashboard")