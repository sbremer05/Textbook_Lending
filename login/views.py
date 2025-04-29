from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from .models import Profile, Notification
from .forms import ProfilePictureForm
from .decorators import role_required
from django.contrib.auth.models import User
from django.urls import reverse

# Home view (Debugging included)
def home(request):
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        if created or not profile.is_setup:
            profile.role = "patron"  # Default role
            profile.is_setup = True
            profile.save()
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        context = {"user": request.user, "role": profile.role, "is_authenticated": True, "unread_notifications_count": unread_notifications_count}
    else:
        context = {"is_authenticated": False}
    return render(request, "login/home.html", context)


    

# Logout view
def logout_view(request):
    logout(request)
    
    return redirect("/")

# Post-login redirection: Checks if user needs to select a role
# @login_required
def post_login_redirect(request):
    user = request.user
    social_account = SocialAccount.objects.filter(user=user, provider='google').first()

    if social_account:
        profile, created = Profile.objects.get_or_create(user=user)

        if not profile.role:  # Only if no role at all
            profile.role = "patron"
            profile.is_setup = True
            profile.save()

        print(f"Redirecting {user.username} to their dashboard ({profile.role})")
        # return redirect("librarian_dashboard" if profile.role == "librarian" else "patron_dashboard")
        return redirect("home")
    else:
        return redirect("/")

# @login_required
def profile_picture_upload(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to upload a profile picture.")
        return render(request, "login/upload_profile_picture.html", {
            "form": None,
            "error_message": "You must be logged in to upload a profile picture. Please log in first."
        })

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('home' if request.user.profile.role != 'librarian' else 'home')

    form = ProfilePictureForm(instance=request.user.profile)
    return render(request, "login/upload_profile_picture.html", {"form": form})

# @login_required
def dashboard(request):
    """ Redirect users to the correct dashboard based on their role. """
    profile, created = Profile.objects.get_or_create(user=request.user)

    if profile.role == 'librarian':
        return redirect('home')
    return redirect('home')

# Patron Dashboard
# @role_required('patron', 'pending')
# @login_required
# def patron_dashboard(request):
#     return render(request, "login/dashboard_patron.html", {"user": request.user})

# Librarian Dashboard
@role_required('librarian')
@login_required
def librarian_dashboard(request):
    return render(request, "login/home.html", {"user": request.user})

# Librarian Requests Page - handles Pending Requests
# @role_required('librarian')
# @login_required
def librarian_requests(request):
    if not request.user.is_authenticated:
        return render(request, "login/librarian_requests.html", {
            "form": None,
            "error_message": "You must be logged in to view librarian requests."
        })
    if request.user.profile.role != "librarian":
        messages.error(request, "You do not have permission to access this page.")
        return redirect("home")  # Only librarians can access

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
# @login_required
def request_librarian(request):
    profile = request.user.profile
    if profile.role == "patron" or profile.role == "pending":
        profile.role = "pending"
        profile.save()
        for librarian in User.objects.filter(profile__role='librarian'):
            Notification.objects.create(
                user=librarian,
                message=f"{request.user.username} has requested librarian access.",
                url= reverse('librarian_requests')
            )
        messages.success(request, "Your request for librarian status has been submitted!")
    return redirect("home")

# @login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return render(request, "login/profile.html", {
            "form": None,
            "error_message": "You must be logged in to view your profile."
        })
    user = request.user
    profile = user.profile
    # Use first_name and last_name if available; otherwise, fallback to username.
    full_name = (f"{user.first_name} {user.last_name}").strip() if (user.first_name or user.last_name) else user.username

    context = {
        'full_name': full_name,
        'email': user.email,
        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        'date_joined': user.date_joined,
        'role': profile.role,
    }
    return render(request, "login/profile.html", context)


def view_notifications(request):
    if not request.user.is_authenticated:
        return render(request, "login/view_notifications.html", {
            "form": None,
            "error_message": "You must be logged in to view your notifications."
        })
    notifications = request.user.notifications.order_by('-created_at')

    notifications.update(is_read=True)

    return render(request, "login/view_notifications.html", {'notifications': notifications})
