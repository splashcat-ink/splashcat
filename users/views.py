import datetime
import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from battles.models import Player
from battles.tasks import user_request_data_export
from splashcat.decorators import github_webhook
from splatnet_assets.models import Weapon
from .forms import RegisterForm, AccountSettingsForm, ResendVerificationEmailForm
from .models import User, GitHubLink, ApiKey


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    latest_battles = user.battles.with_prefetch().order_by('-played_time') \
                         .select_related('vs_stage__name')[:18]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.exclude(judgement__in=['WIN', 'DRAW']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0
    aggregates = Player.objects.filter(team__battle__uploader=user, is_self=True).aggregate(
        average_kills=models.Avg('kills'),
        average_assists=models.Avg('assists'),
        average_deaths=models.Avg('deaths'),
        average_specials=models.Avg('specials'),
        average_paint=models.Avg('paint'),
    )

    period_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    period_ago_wins = user.battles.filter(judgement='WIN', played_time__gte=period_ago).count()
    period_ago_loses = user.battles.exclude(judgement__in=['WIN', 'DRAW']).filter(played_time__gte=period_ago).count()
    period_ago_win_rate = period_ago_wins / (period_ago_wins + period_ago_loses) * 100 if \
        period_ago_wins + period_ago_loses else None

    most_used_weapon = Player.objects.filter(team__battle__uploader=user, is_self=True) \
        .values('weapon').annotate(count=models.Count('weapon')).order_by('-count').first()
    most_used_weapon = Weapon.objects.get(pk=most_used_weapon['weapon']) if most_used_weapon else None

    return render(request, 'users/profile.html',
                  {
                      'profile_user': user,
                      'splashtag': splashtag,
                      'latest_battles': latest_battles,
                      'win_count': win_count,
                      'lose_count': lose_count,
                      'win_rate': win_rate,
                      'period_ago_wins': period_ago_wins,
                      'period_ago_loses': period_ago_loses,
                      'period_ago_win_rate': period_ago_win_rate,
                      'aggregates': aggregates,
                      'most_used_weapon': most_used_weapon,
                  })


def profile_opengraph(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    latest_battles = user.battles.with_prefetch().order_by('-played_time') \
                         .select_related('vs_stage__name')[:12]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.exclude(judgement__in=['WIN', 'DRAW']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    period_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    period_ago_wins = user.battles.filter(judgement='WIN', played_time__gte=period_ago).count()
    period_ago_loses = user.battles.exclude(judgement__in=['WIN', 'DRAW']).filter(played_time__gte=period_ago).count()
    period_ago_win_rate = period_ago_wins / (period_ago_wins + period_ago_loses) * 100 if \
        period_ago_wins + period_ago_loses else None

    most_used_weapons = Player.objects.filter(team__battle__uploader=user, is_self=True) \
                            .values('weapon').annotate(count=models.Count('weapon')).order_by('-count')[:3]
    most_used_weapons = Weapon.objects.filter(pk__in=[weapon['weapon'] for weapon in most_used_weapons])

    return render(request, 'users/opengraph/user.html',
                  {
                      'profile_user': user,
                      'splashtag': splashtag,
                      'latest_battles': latest_battles,
                      'win_count': win_count,
                      'lose_count': lose_count,
                      'win_rate': win_rate,
                      'period_ago_win_rate': period_ago_win_rate,
                      'most_used_weapons': most_used_weapons,
                  })


def profile_battle_list(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    battles = user.battles.with_prefetch().order_by('-played_time') \
        .select_related('vs_stage__name')

    paginator = Paginator(battles, 24)

    page = request.GET.get('page', 1)
    try:
        page = paginator.page(page)
    except (ValueError, TypeError, EmptyPage, InvalidPage):
        return HttpResponseBadRequest('Invalid page number.')

    return render(request, 'users/profile_battle_list.html', {
        'profile_user': user,
        'page': page,
        'splashtag': user.get_splashtag,
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if settings.HCAPTCHA_SECRET_KEY:
                hcaptcha_token = request.POST.get('h-captcha-response')
                if not hcaptcha_token:
                    messages.error(request, 'hCaptcha verification failed.')
                    return render(request, 'users/register.html', {
                        'form': form,
                    })
                hcaptcha_response = requests.post('https://hcaptcha.com/siteverify', data={
                    'secret': settings.HCAPTCHA_SECRET_KEY,
                    'response': hcaptcha_token,
                }).json()
                if not hcaptcha_response['success']:
                    messages.error(request, 'hCaptcha verification failed.')
                    return render(request, 'users/register.html', {
                        'form': form,
                    })

            user = form.save()

            user.send_verification_email()

            messages.success(request, 'Your account has been created. Please check your email to verify your account.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {
        'form': form,
    })


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

    if hasattr(request.user, 'github_link'):
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


def verify_email(request, user_id, token):
    user = get_object_or_404(User, id=user_id)
    correct_token = default_token_generator.check_token(user, token)
    if not correct_token:
        return HttpResponseBadRequest()
    user.verified_email = True
    user.is_active = True
    user.save()
    messages.add_message(request, messages.SUCCESS,
                         f'Verified email for @{user.username}!'
                         )
    return redirect('home')


def resend_verification_email(request):
    if request.method == 'POST':
        form = ResendVerificationEmailForm(request.POST)
        if form.is_valid():
            form.send_email()
            messages.add_message(request, messages.SUCCESS,
                                 f'Verification email sent to {form.cleaned_data["email"]}!'
                                 )
            return redirect('home')
    else:
        form = ResendVerificationEmailForm()
    return render(request, 'users/resend_verification_email.html', {
        'form': form,
    })


@login_required
@require_http_methods(['POST'])
def request_data_export(request):
    user: User = request.user
    # check that the last data export was more than 24 hours ago
    if (user.last_data_export and user.last_data_export > datetime.datetime.now(
            tz=user.last_data_export.tzinfo) - datetime.timedelta(days=1)):
        messages.add_message(request, messages.ERROR,
                             f'You can only request a data export once per day.'
                             )
        return redirect('users:settings')
    if user.data_export_pending:
        messages.add_message(request, messages.ERROR,
                             f'You already have a data export pending.'
                             )
        return redirect('users:settings')
    user.data_export_pending = True
    user.last_data_export = datetime.datetime.now()
    user_request_data_export.delay(user.pk)
    user.save()
    messages.add_message(request, messages.SUCCESS,
                         f'Requested data export for @{user.username}! You should receive an email soon.'
                         )
    return redirect('users:settings')
