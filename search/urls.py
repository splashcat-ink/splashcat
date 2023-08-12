from django.urls import path

from search import views

app_name = "search"
urlpatterns = [
    path('players_played_with/<str:npln_id>/', views.search_for_players_played_with, name='players_played_with'),
]
