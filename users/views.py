import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import FormView

from splashcat.decorators import github_webhook
from .forms import RegisterForm, AccountSettingsForm
from .models import User, GitHubLink, ApiKey


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
            return redirect('users:settings')
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, 'users/settings.html', {
        'form': form,
    })


@login_required
@require_http_methods(['POST'])
def link_github_account(request):
    if request.POST.get('is_refresh', False) == 'true':
        request.session['github_attempting_refresh'] = True

    return redirect('https://github.com/login/oauth/authorize?'
                    f'client_id={settings.GITHUB_OAUTH_CLIENT_ID}')


@login_required
def link_github_account_callback(request):
    github_session_code = request.GET.get('code')
    if not github_session_code:
        return HttpResponseBadRequest()
    response = requests.post('https://github.com/login/oauth/access_token',
                             data={
                                 'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
                                 'client_secret': settings.GITHUB_OAUTH_CLIENT_SECRET,
                                 'code': github_session_code,
                             },
                             headers={
                                 'Accept': 'application/json',
                             })
    if response.status_code != 200:
        return HttpResponseBadRequest()
    github_access_token = response.json()['access_token']
    response = requests.get('https://api.github.com/user',
                            headers={
                                'Authorization': f'token {github_access_token}',
                            })
    if response.status_code != 200:
        return HttpResponseBadRequest()

    if request.user.github_link:
        old_link = request.user.github_link
        old_link.linked_user = None
        old_link.save()

    github_user_id = response.json()['id']
    github_username = response.json()['login']
    GitHubLink.objects.update_or_create(github_id=github_user_id, defaults={
        'linked_user': request.user,
        'github_username': github_username,
    })

    messages.add_message(request, messages.SUCCESS,
                         f'Linked GitHub account @{github_username} to @{request.user.username}!'
                         )

    if request.session.get('github_attempting_refresh'):
        del request.session['github_attempting_refresh']

        graphql_query = """
        query {
          user(login:"%s") {
            sponsorshipForViewerAsSponsorable(activeOnly:true) {
                isOneTimePayment
                privacyLevel
                tier {
                    name
                    monthlyPriceInDollars
              }  
            }
          }
        }""" % github_username

        response = requests.post('https://api.github.com/graphql',
                                 json={'query': graphql_query},
                                 headers={
                                     'Authorization': f'token {settings.GITHUB_PERSONAL_ACCESS_TOKEN}',
                                 })
        if response.status_code == 200:
            data = response.json()['data']['user']['sponsorshipForViewerAsSponsorable']
            github_link = request.user.github_link
            if data:
                tier = data['tier']
                github_link.is_sponsor = data['isOneTimePayment'] is False
                github_link.is_sponsor_public = data['privacyLevel'] == 'PUBLIC'
                github_link.sponsorship_amount_usd = tier['monthlyPriceInDollars']
            else:
                github_link.is_sponsor = False
                github_link.is_sponsor_public = False
                github_link.sponsorship_amount_usd = 0
            github_link.save()

    return redirect('users:settings')


@login_required
@require_http_methods(['POST'])
def create_api_key(request):
    api_key = ApiKey.objects.create(user=request.user, note=request.POST.get('note', ''))
    messages.add_message(request, messages.SUCCESS,
                         f'Created API key `{api_key.key}` for @{request.user.username}!'
                         )
    return redirect('users:settings')


@login_required
@require_http_methods(['POST'])
def delete_api_key(request, key):
    api_key = get_object_or_404(ApiKey, key=key, user=request.user)
    api_key.delete()
    messages.add_message(request, messages.SUCCESS,
                         f'Deleted API key `{key}` for @{request.user.username}!'
                         )
    return redirect('users:settings')
