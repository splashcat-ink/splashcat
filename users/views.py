import datetime
import json
import qrcode
from typing import Optional

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db import models
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from battles.models import Player, Battle
from battles.tasks import user_request_data_export
from splashcat.decorators import github_webhook
from splatnet_assets.models import Weapon
from . import tasks
from .forms import RegisterForm, AccountSettingsForm, ResendVerificationEmailForm
from .models import User, GitHubLink, ApiKey, ProfileUrl, Follow


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    latest_battles = user.battles.with_prefetch().order_by('-played_time') \
                         .select_related('vs_stage__name')[:18]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
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
    period_ago_loses = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).filter(played_time__gte=period_ago) \
        .count()
    period_ago_win_rate = period_ago_wins / (period_ago_wins + period_ago_loses) * 100 if \
        period_ago_wins + period_ago_loses else None

    most_used_weapon = Player.objects.filter(team__battle__uploader=user, is_self=True) \
        .values('weapon').annotate(count=models.Count('weapon')).order_by('-count').first()
    most_used_weapon = Weapon.objects.get(pk=most_used_weapon['weapon']) if most_used_weapon else None

    total_uploader_disconnects = Player.objects.filter(team__battle__uploader=user, is_self=True,
                                                       disconnect=True).count()
    
    following_list = Follow.objects.filter(follower=user).select_related('followed').order_by('-followed_on')
    followers_list = Follow.objects.filter(followed=user).select_related('follower').order_by('-followed_on')
    followed_user = user
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()

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
                      'total_uploader_disconnects': total_uploader_disconnects,
                      'following_list': following_list,
                      'followers_list': followers_list,
                      'followed_user': followed_user,
                      'is_following': is_following,
                  })


def profile_opengraph(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    latest_battles = user.battles.with_prefetch().order_by('-played_time') \
                         .select_related('vs_stage__name')[:12]
    splashtag = latest_battles[0].splashtag if latest_battles else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    period_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    period_ago_wins = user.battles.filter(judgement='WIN', played_time__gte=period_ago).count()
    period_ago_loses = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).filter(played_time__gte=period_ago) \
        .count()
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


def profile_json(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    try:
        latest_battle: Optional[Battle] = user.battles.with_prefetch().latest('played_time')
    except Battle.DoesNotExist:
        latest_battle = None
    splashtag = latest_battle.splashtag if latest_battle else None

    win_count = user.battles.filter(judgement='WIN').count()
    lose_count = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else None
    aggregates = Player.objects.filter(team__battle__uploader=user, is_self=True).aggregate(
        average_kills=models.Avg('kills'),
        average_assists=models.Avg('assists'),
        average_deaths=models.Avg('deaths'),
        average_specials=models.Avg('specials'),
        average_paint=models.Avg('paint'),
    )

    period_ago = datetime.datetime.now() - datetime.timedelta(hours=24)
    period_ago_wins = user.battles.filter(judgement='WIN', played_time__gte=period_ago).count()
    period_ago_loses = user.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).filter(played_time__gte=period_ago) \
        .count()
    period_ago_win_rate = period_ago_wins / (period_ago_wins + period_ago_loses) * 100 if \
        period_ago_wins + period_ago_loses else None
    period_ago_aggregates = Player.objects.filter(team__battle__uploader=user, is_self=True,
                                                  team__battle__played_time__gt=period_ago).aggregate(
        average_kills=models.Avg('kills'),
        average_assists=models.Avg('assists'),
        average_deaths=models.Avg('deaths'),
        average_specials=models.Avg('specials'),
        average_paint=models.Avg('paint'),
    )

    try:
        most_used_weapon = Player.objects.filter(team__battle__uploader=user, is_self=True) \
            .values('weapon').annotate(count=models.Count('weapon')).order_by('-count').first()
    except Player.DoesNotExist:
        most_used_weapon = None
    most_used_weapon = Weapon.objects.get(pk=most_used_weapon['weapon']) if most_used_weapon else None

    total_uploader_disconnects = Player.objects.filter(team__battle__uploader=user, is_self=True,
                                                       disconnect=True).count()

    splashtag_badge_images = [(badge.image.url if badge else None) for badge in
                              splashtag['badges']] if splashtag else None

    return JsonResponse({
        'splashtag': {
            'name': splashtag['name'],
            'name_id': splashtag['name_id'],
            'title': latest_battle.player.byname,
            'background_url': splashtag['background'].image.url,
            'badge_urls': splashtag_badge_images,
            'text_color': "#" + splashtag['background'].text_color.to_hex(),
        } if splashtag else None,
        'win_count': win_count,
        'lose_count': lose_count,
        'win_rate': win_rate,
        '24h_wins': period_ago_wins,
        '24h_loses': period_ago_loses,
        '24h_win_rate': period_ago_win_rate,
        'aggregates': aggregates,
        '24h_aggregates': period_ago_aggregates,
        'most_used_weapon': {
            'name': most_used_weapon.name.string,
            'image': most_used_weapon.flat_image.url,
            'image_3d': most_used_weapon.image_3d.url,
            'sub_name': most_used_weapon.sub.name.string,
            'sub_overlay_image': most_used_weapon.sub.overlay_image.url,
            'sub_mask_image': most_used_weapon.sub.mask_image.url,
            'special_name': most_used_weapon.special.name.string,
            'special_overlay_image': most_used_weapon.special.overlay_image.url,
            'special_mask_image': most_used_weapon.special.mask_image.url,
        } if most_used_weapon else None,
        'total_uploader_disconnects': total_uploader_disconnects,
        'profile_picture': user.profile_picture.url,
        'latest_battle_color': f"#{latest_battle.player.team.color.to_hex()}" if latest_battle else None,
        'sponsor_favorite_color': f"#{user.favorite_color.to_hex()}" if user.favorite_color else None,
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


def profile_album(request, username: str):
    user = get_object_or_404(User, username__iexact=username)

    return render(request, 'users/profile_album.html', {
        'profile_user': user,
        'splashtag': user.get_splashtag,
    })


def profile_qr_code(request, username: str):
    user = get_object_or_404(User, username__iexact=username)
    if not user.coral_friend_url:
        return HttpResponseBadRequest('User does not have coral friend url.')
    qr_code = qrcode.make(f"{user.coral_friend_url}?via=qr&utm_source=splashcat.ink&utm_medium=qr")
    response = HttpResponse(content_type="image/png")
    qr_code.save(response, "PNG")
    return response


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
            tasks.generate_user_profile_picture.delay(user.pk)

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
    profile_url_form_set = inlineformset_factory(User, ProfileUrl, fields=["url"], can_delete_extra=False)
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, request.FILES, instance=request.user)
        formset = profile_url_form_set(request.POST, instance=request.user)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            tasks.validate_rel_me_links.delay(request.user.id)
            return redirect('users:settings')
    else:
        form = AccountSettingsForm(instance=request.user)
        formset = profile_url_form_set(instance=request.user)
    return render(request, 'users/settings.html', {
        'form': form,
        'formset': formset,
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

def profile_follows(request, username: str, view_type: str):
    user = get_object_or_404(User, username__iexact=username)

    if view_type == 'followers':
        follow_list = Follow.objects.filter(followed=user).select_related('follower').order_by('-followed_on')
        follow_type = 'followers'
    elif view_type == 'following':
        follow_list = Follow.objects.filter(follower=user).select_related('followed').order_by('-followed_on')
        follow_type = 'following'
    else:
        # Handle invalid view_type, such as redirect or 404
        return redirect('profile', username=user.username)  # Or another appropriate response
    
    followed_user = user
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()

    return render(request, 'users/profile_follows.html', {
        'profile_user': user,
        'splashtag': user.get_splashtag,
        'follow_list': follow_list,
        'follow_type': follow_type,
        'followed_user': followed_user,
        'is_following': is_following,
    })

@login_required
def follow_user(request, username):
    followed_user = get_object_or_404(User, username__iexact=username)

    if request.user == followed_user:
        messages.error(request, "You cannot follow yourself.")
    elif Follow.objects.filter(follower=request.user, followed=followed_user).exists():
        messages.error(request, f"You are already following {followed_user.username}.")
    else:
        Follow.objects.create(follower=request.user, followed=followed_user)
        messages.success(request, f"You are now following {followed_user.username}.")
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def unfollow_user(request, username):
    followed_user = get_object_or_404(User, username=username)

    follow_instance = Follow.objects.filter(follower=request.user, followed=followed_user).first()
    if follow_instance:
        follow_instance.delete()
        messages.success(request, f"You have unfollowed {followed_user.username}.")
    else:
        messages.error(request, "You are not following this user.")

    return redirect(request.META.get('HTTP_REFERER', 'profile'))