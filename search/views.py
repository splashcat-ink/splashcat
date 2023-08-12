from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from battles.models import Player, Battle


# Create your views here.

@login_required
def search_for_players_played_with(request, npln_id: str):
    players = Player.objects.filter(team__battle__uploader_id=request.user.id, npln_id__iexact=npln_id).distinct()
    battles_with_player = Battle.objects.filter(teams__players__in=players).distinct().order_by('-played_time')

    return render(request, 'search/search_for_players_played_with.html', {
        'battles': battles_with_player,
        'player': players.latest('team__battle__played_time'),
    })
