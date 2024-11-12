from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from battles.models import Player, Battle


# Create your views here.

@login_required
def search_for_players_played_with(request, npln_id: str):
    request_user_player = Player.objects.filter(team__battle__uploader_id=request.user.id, is_self=True).latest(
        'team__battle__played_time')
    if str.lower(request_user_player.npln_id) == str.lower(npln_id):
        return HttpResponseBadRequest('You cannot search for yourself.')

    players = Player.objects.filter(team__battle__uploader_id=request.user.id, npln_id__iexact=npln_id).distinct()
    battles_with_player = Battle.objects.with_card_prefetch().filter(teams__players__in=players).distinct().order_by(
        '-played_time')

    return render(request, 'search/search_for_players_played_with.html', {
        'battles': battles_with_player,
        'player': players.latest('team__battle__played_time') if len(players) > 0 else None,
    })
