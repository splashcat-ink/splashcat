import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView

from splashcat.decorators import github_webhook
from .forms import RegisterForm, AccountSettingsForm
from .models import User, GitHubLink


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    latest_battles = user.battles.order_by('-played_time') \
                         .select_related('vs_stage__name')[:12]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    battle_count = user.battles.count()
    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.exclude(judgement__in=['WIN', 'DRAW']).count()
    win_rate = win_count / battle_count * 100 if battle_count else 0

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
    action = data['action']

    github_link, _created = GitHubLink.objects.get_or_create(github_id=data['sponsorship']['sponsor']['id'])

    if action == 'created' or action == 'tier_changed':
        github_link.is_sponsor = True
        github_link.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
        github_link.sponsorship_amount_usd = data['sponsorship']['tier']['monthly_price_in_dollars']
    elif action == 'edited':
        github_link.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
        github_link.sponsorship_amount_usd = data['sponsorship']['tier']['monthly_price_in_dollars']
    elif action == 'cancelled':
        github_link.is_sponsor = False
        github_link.is_sponsor_public = False
        github_link.sponsorship_amount_usd = 0
    github_link.save()
    return HttpResponse("ok")


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, 'users/settings.html', {
        'form': form,
    })
