from celery import shared_task

from users.models import User


@shared_task
def generate_user_profile_picture(user_id):
    user = User.objects.get(pk=user_id)

    if not user.profile_picture:
        user.save_splatoon_identicon()
