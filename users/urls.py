from django.urls import path

from users.views import *

app_name = "users"
urlpatterns = [
    path('api/github-sponsors-webhook/', github_sponsors_webhook, name='github_sponsors_webhook')
]
