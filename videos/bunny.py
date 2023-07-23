import json
from urllib.parse import urlencode

import requests
from django.conf import settings

from users.models import User


def create_video(title, collection_id):
    url = f"https://video.bunnycdn.com/library/{settings.BUNNY_VIDEO_LIBRARY_ID}/videos"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "AccessKey": settings.BUNNY_VIDEO_API_KEY,
    }

    data = {
        'title': title,
        'collectionId': collection_id,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    return response.json().get('guid')


def upload_video(video_id, video):
    url = f"https://video.bunnycdn.com/library/{settings.BUNNY_VIDEO_LIBRARY_ID}/videos/{video_id}"

    headers = {
        "accept": "application/json",
        "AccessKey": settings.BUNNY_VIDEO_API_KEY,
    }

    response = requests.put(url, headers=headers, data=video)

    return response.text


def set_video_thumbnail(video_id, thumbnail_url):
    url = f"https://video.bunnycdn.com/library/{settings.BUNNY_VIDEO_LIBRARY_ID}/videos/{video_id}/thumbnail"

    query_params = {
        'thumbnailUrl': thumbnail_url,
    }

    url += f"?{urlencode(query_params)}"

    headers = {
        "accept": "application/json",
        "AccessKey": settings.BUNNY_VIDEO_API_KEY,
    }

    requests.post(url, headers=headers)


def get_video_collection_for_user(user: User):
    if user.video_collection_id:
        return user.video_collection_id

    url = "https://video.bunnycdn.com/library/140045/collections"

    headers = {
        "accept": "application/json",
        "content-type": "application/*+json"
    }

    data = {
        'name': f"@{user.username}",
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    collection_id = response.json().get('guid')

    user.video_collection_id = collection_id
    user.save()

    return collection_id
