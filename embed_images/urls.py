from django.urls import path

from embed_images import views

app_name = "embed_images"
urlpatterns = [
    path('', views.index, name='index'),
    path('user/@<str:username>/stats/', views.user_stats, name='user_stats'),
    path('user/@<str:username>/splashtag/', views.user_splashtag, name='user_splashtag'),
    path('user/@<str:username>/gear/', views.user_gear, name='user_gear'),
]
