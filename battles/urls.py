from django.urls import path

from battles.views import *

app_name = "battles"
urlpatterns = [
    path('api/upload/', upload_battle, name='upload_battle'),
    path('<int:battle_id>/', view_battle, name='view_battle'),
    path('redir/<str:uploader_username>/<str:splatnet_id>/', redirect_from_splatnet_id,
         name='redirect_from_splatnet_id'),
    path('api/<int:battle_id>/json/', get_battle_json, name='get_battle_json'),
    path('api/<str:splatnet_id>/exists/', check_if_battle_exists, name='check_battle_exists'),
]
