import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from announcements.models import Announcement
from battles.models import Battle
from users.models import User


def home(request):
    recent_battles = Battle.objects.with_card_prefetch().order_by('-uploaded_at')[:24]
    user_recent_battles = request.user.battles.with_card_prefetch().order_by('-uploaded_at')[
                          :12] if request.user.is_authenticated else None
    announcements = Announcement.objects.filter(active=True).order_by("-created_at")

    return render(request, 'splashcat/home.html', {
        'recent_battles': recent_battles,
        'user_recent_battles': user_recent_battles,
        'announcements': announcements,
    })


def sponsor(request):
    current_sponsors = User.objects.filter(github_link__is_sponsor=True, github_link__is_sponsor_public=True,
                                           github_link__sponsorship_amount_usd__gte=5) \
        .order_by('github_link__sponsorship_amount_usd').reverse()
    if settings.DEBUG:
        stripe_sponsors = User.objects.filter(stripe_customer_id__isnull=False)
    else:
        stripe_sponsors = User.objects.filter(_stripe_entitlements__contains="sponsor-badge")
    return render(request, 'splashcat/sponsor.html', {
        'current_sponsors': list(stripe_sponsors) + list(current_sponsors),
    })


def legal(request):
    return render(request, 'splashcat/legal.html')


def about(request):
    return render(request, 'splashcat/about.html')


def uploaders_information(request):
    developer_usernames = ["Joy", "catgirl"]
    developer_users = User.objects.filter(username__in=developer_usernames)

    developers = {}
    for user in developer_users:
        developers[user.username] = user

    return render(request, 'splashcat/uploaders_information.html', {
        'developers': developers,
    })


def health_check(request):
    return HttpResponse('okii :3')


def robots_txt(request):
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, 'robots.txt')
    with open(abs_file_path) as f:
        return HttpResponse(f.read(), content_type='text/plain', headers={'Cache-Control': 'public, max-age=86400'})


def ads_txt(request):
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, 'ads.txt')
    with open(abs_file_path) as f:
        return HttpResponse(f.read(), content_type='text/plain', headers={'Cache-Control': 'public, max-age=86400'})
