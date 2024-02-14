import requests
from bs4 import BeautifulSoup
from celery import shared_task

from users.models import User, ProfileUrl


@shared_task(autoretry_for=(Exception,), retry_backoff=True)
def generate_user_profile_picture(user_id):
    user = User.objects.get(pk=user_id)

    if not user.profile_picture:
        user.save_splatoon_identicon()


@shared_task
def validate_rel_me_links(user_id):
    user = User.objects.get(pk=user_id)
    links = ProfileUrl.objects.filter(user_id=user_id)
    profile_url = f"https://splashcat.ink/@{user.username}/"

    for link in links:
        link.is_rel_me_verified = False
        html = requests.get(link.url).content
        bs4 = BeautifulSoup(html, "html.parser")
        a_links = bs4.find_all("a[rel=me]")
        for a_link in a_links:
            if a_link.get("href") == profile_url:
                link.is_rel_me_verified = True
                break

        if not link.is_rel_me_verified:
            link_links = bs4.find_all("link[rel=me]")
            for link_link in link_links:
                if link_link.get("href") == profile_url:
                    link.is_rel_me_verified = True
                    break

        link.save()
