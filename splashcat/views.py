from django.shortcuts import render

from battles.models import Battle
from users.models import User


def home(request):
    recent_battles = Battle.objects.with_prefetch() \
                         .prefetch_related('uploader__github_link') \
                         .select_related('vs_stage__name') \
                         .order_by('-id')[:24]
    user_recent_battles = request.user.battles.with_prefetch().select_related('vs_stage__name') \
                              .order_by('-id')[:12] if request.user.is_authenticated else None

    return render(request, 'splashcat/home.html', {
        'recent_battles': recent_battles,
        'user_recent_battles': user_recent_battles,
    })


def sponsor(request):
    current_sponsors = User.objects.filter(github_link__is_sponsor=True, github_link__is_sponsor_public=True) \
        .order_by('github_link__sponsorship_amount_usd').reverse()
    return render(request, 'splashcat/sponsor.html', {
        'current_sponsors': current_sponsors,
    })


def uploaders_information(request):
    return render(request, 'splashcat/uploaders_information.html')
