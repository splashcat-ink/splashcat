from django.urls import path

from grizzco_jobs.views import *

app_name = "battles"
urlpatterns = [
    path('api/upload/', upload_job, name='upload_job'),
    path('<int:job_id>/', view_job, name='view_job'),
    path('<int:job_id>/opengraph/', job_opengraph, name='job_opengraph'),
    path('redir/<str:uploader_username>/<str:splatnet_id>/', redirect_from_splatnet_id,
         name='redirect_from_splatnet_id'),
    # path('api/<int:battle_id>/json/', get_battle_json, name='get_battle_json'),
    path('api/<str:splatnet_id>/exists/', check_if_job_exists, name='check_job_exists'),
    path('api/recent/', get_recent_job_ids, name='get_recent_job_ids')
]
