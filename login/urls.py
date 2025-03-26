from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("redirect-after-login/", views.post_login_redirect, name="post_login_redirect"),
    path("patron-dashboard/", views.patron_dashboard, name="patron_dashboard"),
    path("librarian-dashboard/", views.librarian_dashboard, name="librarian_dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("request-librarian/", views.request_librarian, name="request_librarian"),
    path("librarian-requests/", views.librarian_requests, name="librarian_requests"),
    path("upload-profile-picture/", views.profile_picture_upload, name="upload_profile_picture"),
    path("guest-login/", views.guest_login, name="guest_login")
]
