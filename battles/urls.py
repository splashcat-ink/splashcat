from django.urls import path

from battles.views import *

app_name = "battles"
urlpatterns = [
    path('api/upload/', upload_battle, name='upload_battle'),
    path('<int:battle_id>/', view_battle, name='view_battle'),
    path('<int:battle_id>/opengraph/', battle_opengraph, name='battle_opengraph'),
    path('redir/<str:uploader_username>/<str:splatnet_id>/', redirect_from_splatnet_id,
         name='redirect_from_splatnet_id'),
    path('api/<int:battle_id>/json/', get_battle_json, name='get_battle_json'),
    path('api/<str:splatnet_id>/exists/', check_if_battle_exists, name='check_battle_exists'),
    path('api/recent/', get_recent_battle_ids, name='get_recent_battle_ids'),
    path('htmx/latest/', get_latest_battles, name='htmx_latest_battles'),
    path('global-data-export/', global_data_export, name='global_data_export'),
    path('global-data-export/redirect/', redirect_global_data_export, name='redirect_global_data_export'),
]
