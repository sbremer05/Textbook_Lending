from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("redirect-after-login/", views.post_login_redirect, name="post_login_redirect"),
    path("patron-dashboard/", views.patron_dashboard, name="patron_dashboard"),
    path("librarian-dashboard/", views.librarian_dashboard, name="librarian_dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("choose-role/", views.choose_role, name="choose_role"),
    path("upload-profile-picture/", views.profile_picture_upload, name="upload_profile_picture"),
]
