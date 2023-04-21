from django.urls import path

from battles.views import *

app_name = "battles"
urlpatterns = [
    path('api/upload/', upload_battle, name='upload_battle')
]
