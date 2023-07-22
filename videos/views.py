import datetime

from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from splashcat.decorators import api_auth_required
from users.models import User
from videos.bunny import create_video, upload_video as upload_to_bunny
from videos.models import BattleVideo


# Create your views here.

@require_POST
@csrf_exempt
@api_auth_required
def upload_video(request):
    user: User = request.user
    if not user.approved_to_upload_videos:
        return HttpResponseForbidden()
    battle_start_time = request.POST.get("battle_start_time")
    battle_start_time = datetime.datetime.fromisoformat(battle_start_time)
    video = request.FILES.get("video")
    video_id = create_video(f'{user.username}-{battle_start_time.isoformat()}', user.video_collection_id)
    upload_to_bunny(video_id, video)

    video_object = BattleVideo(
        uploader=user,
        battle_start_time=battle_start_time,
        bunny_video_id=video_id,
    )
    video_object.save()
    related_battle = video_object.find_related_battle()
    if related_battle:
        video_object.battle = related_battle
        video_object.update_video_thumbnail()
        video_object.save()
    return HttpResponse('ok')
