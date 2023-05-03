import json

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView

from splashcat.decorators import github_webhook
from .forms import RegisterForm
from .models import User


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    # get their latest battles and splashtag
    latest_battles = user.battles.order_by('-played_time') \
                         .select_related('player_nameplate_badge_1__image') \
                         .select_related('player_nameplate_badge_2__image') \
                         .select_related('player_nameplate_badge_3__image') \
                         .select_related('vs_stage__name')[:12]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    battle_count = user.battles.count()
    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.exclude(judgement__in=['WIN', 'DRAW']).count()
    win_rate = win_count / (win_count + lose_count) * 100

    return render(request, 'users/profile.html',
                  {
                      'profile_user': user,
                      'splashtag': splashtag,
                      'latest_battles': latest_battles,
                      'battle_count': battle_count,
                      'win_count': win_count,
                      'lose_count': lose_count,
                      'win_rate': win_rate,
                  })


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm


@csrf_exempt
@require_http_methods(['POST'])
@github_webhook
def github_sponsors_webhook(request):
    data = json.loads(request.body)
    _action = data['action']
    # if action == 'created' or action == 'tier_changed':
    #     try:
    #         social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
    #         user = social_account.user
    #         user.is_splashcat_sponsor = data['sponsorship']['tier']['monthly_price_in_dollars'] >= 5
    #         user.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
    #     except SocialAccount.DoesNotExist:
    #         pass
    # elif action == 'edited':
    #     try:
    #         social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
    #         user = social_account.user
    #         user.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
    #     except SocialAccount.DoesNotExist:
    #         pass
    # elif action == 'cancelled':
    #     try:
    #         social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
    #         user = social_account.user
    #         user.is_splashcat_sponsor = False
    #     except SocialAccount.DoesNotExist:
    #         pass
    # return HttpResponse("ok")
