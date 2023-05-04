from django.shortcuts import render

from battles.models import Battle


def home(request):
    recent_battles = Battle.objects.order_by('-id')[:24]
    user_recent_battles = request.user.battles.order_by('-id')[:12] if request.user else None

    return render(request, 'splashcat/home.html', {
        'recent_battles': recent_battles,
        'user_recent_battles': user_recent_battles,
    })
