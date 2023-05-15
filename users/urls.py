from django.contrib.auth import views as auth_views
from django.urls import path

from users.views import *

app_name = "users"
urlpatterns = [
    path('api/github-sponsors-webhook/', github_sponsors_webhook, name='github_sponsors_webhook'),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    path(
        "register/",
        register,
        name="register",
    ),
    path(
        "settings/",
        user_settings,
        name="settings",
    ),
    path('github/link/',
         link_github_account,
         name='link_github_account'),
    path('github/link/callback/',
         link_github_account_callback,
         name='link_github_account_callback'),
    path('api-keys/create/',
         create_api_key,
         name='create_api_key'),
    path('api-keys/<str:key>/delete/',
         delete_api_key,
         name='delete_api_key'),
    path('verify-email/<int:user_id>/<str:token>/',
         verify_email,
         name='verify_email'),
]
