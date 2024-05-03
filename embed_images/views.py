import datetime

from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, get_object_or_404

from battles.models import Player
from splatnet_assets.models import Weapon
from users.models import User


# Create your views here.

@login_required
def index(request):
    return render(request, "embed_images/index.html")


def user_stats(request, username):
    user = get_object_or_404(User, username__iexact=username)
    latest_battle = user.battles.with_prefetch().latest('played_time')
    splashtag = latest_battle.splashtag if latest_battle else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    period_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    period_ago_wins = user.battles.filter(judgement='WIN', played_time__gte=period_ago).count()
    period_ago_loses = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).filter(played_time__gte=period_ago) \
        .count()
    period_ago_win_rate = period_ago_wins / (period_ago_wins + period_ago_loses) * 100 if \
        period_ago_wins + period_ago_loses else None

    most_used_weapon = Player.objects.filter(team__battle__uploader=user, is_self=True) \
        .values('weapon').annotate(count=models.Count('weapon')).order_by('-count')[0]
    most_used_weapon = Weapon.objects.filter(pk=most_used_weapon["weapon"])[0]

    return render(request, "embed_images/user_stats.html", {
        'profile_user': user,
        'splashtag': splashtag,
        'win_count': win_count,
        'lose_count': lose_count,
        'win_rate': win_rate,
        'period_ago_win_rate': period_ago_win_rate,
        'most_used_weapon': most_used_weapon,
    })


def user_gear(request, username):
    user = get_object_or_404(User, username__iexact=username)
    latest_battle = user.get_latest_battle()
    player = latest_battle.player
    gears = [player.head_gear, player.clothing_gear, player.shoes_gear]

    return render(request, "embed_images/user_gear.html", {
        'profile_user': user,
        'latest_battle': latest_battle,
        'player': player,
        'gears': gears,
    })


def user_splashtag(request, username):
    user = get_object_or_404(User, username__iexact=username)
    latest_battle = user.get_latest_battle()
    player = latest_battle.player
    splashtag = player.splashtag

    return render(request, "embed_images/user_gear.html", {
        'profile_user': user,
        'latest_battle': latest_battle,
        'player': player,
        'splashtag': splashtag,
    })
