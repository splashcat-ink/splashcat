from django.urls import path

from videos import views

app_name = "videos"
urlpatterns = [
    path("upload/battle/", views.upload_video, name="upload_battle"),
]
