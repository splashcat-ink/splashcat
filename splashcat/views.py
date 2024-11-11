import os

from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

from battles.models import Battle, Player
from users.models import User


def home(request):
    player_prefetch_queryset = Player.objects \
        .select_related('weapon__name', 'weapon__flat_image', 'weapon__sub__name',
                        'weapon__sub__overlay_image', 'weapon__sub__mask_image', 'weapon__special__name',
                        'weapon__special__overlay_image', 'weapon__special__mask_image').filter(is_self=True)
    player_prefetch = Prefetch(
        'teams__players',
        queryset=player_prefetch_queryset,
    )

    recent_battles = Battle.objects.prefetch_related('uploader__github_link', player_prefetch).select_related(
        'vs_stage__name', 'battlevideo', 'splatfest').order_by('-uploaded_at')[:24]
    user_recent_battles = request.user.battles.select_related('vs_stage__name', 'battlevideo',
                                                              'splatfest').prefetch_related(
        player_prefetch).order_by('-uploaded_at')[:12] if request.user.is_authenticated else None

    return render(request, 'splashcat/home.html', {
        'recent_battles': recent_battles,
        'user_recent_battles': user_recent_battles,
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
