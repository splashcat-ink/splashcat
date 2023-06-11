from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from users.forms import AuthenticationForm
from users.views import *

app_name = "users"
urlpatterns = [
    path('api/github-sponsors-webhook/', github_sponsors_webhook, name='github_sponsors_webhook'),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html", form_class=AuthenticationForm),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset/form.html",
            email_template_name="users/password_reset/email_content.txt",
            subject_template_name="users/password_reset/email_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),

        ),
        name="password_reset",
    ),
    path("password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset/done.html"),
         name='password_reset_done'),
    path("password-reset/confirm/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset/confirm.html",
                                                     success_url=reverse_lazy("users:password_reset_complete")),
         name='password_reset_confirm'),
    path("password-reset/complete/",
         auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset/complete.html"),
         name='password_reset_complete'),
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
    path(
        "settings/request-data-export/",
        request_data_export,
        name="request_data_export",
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
    path('verify-email/resend/',
         resend_verification_email,
         name='resend_verification_email'),
]
