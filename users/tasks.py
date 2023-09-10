import ronkyuu
from celery import shared_task

from users.models import User, ProfileUrl


@shared_task
def generate_user_profile_picture(user_id):
    user = User.objects.get(pk=user_id)

    if not user.profile_picture:
        user.save_splatoon_identicon()


@shared_task
def validate_rel_me_links(user_id):
    user = User.objects.get(pk=user_id)
    links = ProfileUrl.objects.filter(user_id=user_id)

    for link in links:
        is_verified = ronkyuu.confirmRelMe(f"https://splashcat.ink/@{user.username}/", link.url)
        link.is_rel_me_verified = is_verified
        link.save()
