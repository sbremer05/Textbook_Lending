from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("logout", views.logout_view, name="logout"),
    path("redirect-after-login/", views.post_login_redirect, name="post_login"),
    path("patron-dashboard/", views.patron_dashboard, name="patron_dashboard"),
    path("librarian-dashboard/", views.librarian_dashboard, name="librarian_dashboard"),
    path("choose-role/", views.choose_role, name="choose_role"),
]