import json

import jsonschema
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate
from sentry_sdk import capture_exception, capture_message

from battles.data_exports import get_latest_export_download_url
from battles.models import *
from battles.parsers.splashcat import parse_splashcat
from battles.parsers.splatnet3 import parse_splatnet3
from battles.tasks import generate_battle_description
from battles.utils import BattleAlreadyExistsError
from splashcat.decorators import api_auth_required
from splatnet_assets.models import Weapon
from users.models import User, SponsorshipTiers


# Create your views here.

def view_battle(request, battle_id):
    battle: Battle = get_object_or_404(Battle.objects.with_prefetch(True), id=battle_id)

    team_bar_display = make_team_bar_display(battle)

    return render(request, 'battles/view_battle.html', {
        'battle': battle,
        'team_bar_display': team_bar_display,
    })


def battle_opengraph(request, battle_id):
    battle: Battle = get_object_or_404(Battle.objects.with_prefetch(True), id=battle_id)

    team_bar_display = make_team_bar_display(battle)

    return render(request, 'battles/battle_opengraph.html', {
        'battle': battle,
        'team_bar_display': team_bar_display,
    })


def make_team_bar_display(battle):
    team_bar_display = []
    total = 0
    for i, team in enumerate(battle.teams.all()):
        team_value = 0
        display_text = ""
        if battle.vs_rule != battle.VsRule.TURF_WAR and team.score is not None:
            total += team.score
            team_value = team.score
            display_text = _("KNOCKOUT!") if team.score == 100 else _("Score: %(score)d") % {'score': team.score}
        elif team.paint_ratio is not None:
            total += team.paint_ratio
            team_value = team.paint_ratio
            display_text = _("%(percent).1f%%") % {'percent': team.paint_ratio * 100}
        display_object = {
            'display_text': display_text,
            'team_color': team.color,
            'team_value': team_value,
        }
        if team.is_my_team:
            team_bar_display.insert(0, display_object)
        else:
            team_bar_display.append(display_object)
    if total == 0:
        total = 1
    for display_object in team_bar_display:
        display_object['width'] = display_object['team_value'] / total * 100
    return team_bar_display


def redirect_from_splatnet_id(request, uploader_username, splatnet_id):
    battle = get_object_or_404(Battle, splatnet_id=splatnet_id, uploader__username=uploader_username)
    return redirect('battles:view_battle', battle_id=battle.id)


def redirect_to_user_latest_battle(request, uploader_username):
    uploader = get_object_or_404(User, username=uploader_username)

    uploader_latest_battle = uploader.battles.only("id").latest("played_time")

    return redirect('battles:view_battle', battle_id=uploader_latest_battle.id)


def get_battle_json(request, battle_id):
    battle = get_object_or_404(Battle.objects.with_prefetch(True), id=battle_id)
    data = json.dumps(battle.to_dict())
    return HttpResponse(data, content_type='application/json')


@login_required
def global_data_export(request):
    return render(request, 'battles/global_data_export.html')


@login_required
def redirect_global_data_export(request):
    user: User = request.user
    if user.is_verified_for_export_download:
        return redirect(get_latest_export_download_url())
    else:
        return HttpResponseForbidden()


@api_auth_required
def get_recent_battle_ids(request):
    recent_battles = request.user.battles.order_by('-played_time')[:300]
    return JsonResponse({
        'battle_ids': [battle.splatnet_id for battle in recent_battles],
    })


@csrf_exempt
@require_http_methods(['POST'])
@api_auth_required
@transaction.atomic
def upload_battle(request):
    data = request.body
    if request.content_type == 'application/json':
        data = json.loads(data)
    elif request.content_type == 'application/x-messagepack' or request.content_type == 'application/x-msgpack':
        import msgpack
        data = msgpack.unpackb(data)

    # deny request if data is over 512KB
    if len(data) > 512 * 1024:
        capture_message("request body too large")
        return HttpResponseBadRequest(
            json.dumps({
                'error': 'request too large',
            })
        )

    # normalize incoming data by recursively removing any fields containing None
    # this prevents weird cases where JSON data lacks the fields completely but MessagePack data has them as None
    def normalize(to_normalize):
        if isinstance(to_normalize, dict):
            return {k: normalize(v) for k, v in to_normalize.items() if v is not None}
        elif isinstance(to_normalize, list):
            return [normalize(v) for v in to_normalize]
        else:
            return to_normalize

    data = normalize(data)

    try:
        validate(data, {
            'type': 'object',
            'properties': {
                'battle': {
                    'type': 'object',
                },
                'data_type': {
                    'enum': ['splatnet3', 'splashcat']
                },
                'uploader_agent': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'maxLength': 32,
                        },
                        'version': {
                            'type': 'string',
                            'maxLength': 50,
                        },
                        'extra': {
                            'type': 'string',
                            'maxLength': 100,
                        },
                    },
                },
            },
            'required': ['battle', 'data_type'],
        })
    except jsonschema.ValidationError as e:
        capture_exception(e)
        return HttpResponseBadRequest(e, content_type='text/plain')

    if data['data_type'] == 'splatnet3':
        try:
            battle = parse_splatnet3(data, request)
        except jsonschema.ValidationError as e:
            capture_exception(e)
            return HttpResponseBadRequest(e, content_type='text/plain')
        except BattleAlreadyExistsError as e:
            capture_exception(e)
            return HttpResponseBadRequest(
                json.dumps({
                    'status': 'error',
                    'error': 'battle already exists',
                })
            )
        except NotImplementedError:
            capture_exception(e)
            return HttpResponseBadRequest(
                json.dumps({
                    'status': 'error',
                    'error': 'not implemented',
                })
            )
    elif data['data_type'] == 'splashcat':
        try:
            battle = parse_splashcat(data, request)
        except jsonschema.ValidationError as e:
            capture_exception(e)
            return HttpResponseBadRequest(e, content_type='text/plain')
        except BattleAlreadyExistsError as e:
            capture_exception(e)
            return HttpResponseBadRequest(
                json.dumps({
                    'status': 'error',
                    'error': 'battle already exists',
                })
            )

    user: User = request.user
    if battle.vs_mode == battle.VsMode.X_MATCH:
        battle.x_battle_division = user.x_battle_division
        battle.save()

    uploader_agent = data.get('uploader_agent', {})
    battle.uploader_agent_name = uploader_agent.get('name')
    battle.uploader_agent_version = uploader_agent.get('version')
    battle.uploader_agent_extra = uploader_agent.get('extra')
    battle.save()

    battle.splatfest = battle.find_current_splatfest()
    battle.save()

    related_video = battle.find_related_battle_video()
    if related_video:
        related_video.battle = battle
        related_video.save()
        related_video.update_video_thumbnail()

    if "ai-battle-descriptions" in user.entitlements:
        generate_battle_description.delay(battle.id)

    return JsonResponse({
        'status': 'ok',
        'battle_id': battle.id,
    })


@csrf_exempt
@require_http_methods(['GET'])
@api_auth_required
def check_if_battle_exists(request, splatnet_id):
    try:
        battle = Battle.objects.get(splatnet_id=splatnet_id, uploader=request.user)
        return JsonResponse({
            'status': 'ok',
            'exists': True,
            'battle_id': battle.id,
        }, status=200)
    except Battle.DoesNotExist:
        return JsonResponse({
            'status': 'ok',
            'exists': False,
        }, status=200)


@login_required
def get_latest_battles(request):
    battles = request.user.battles.with_prefetch().order_by('-id')[:10]
    return render(request, 'battles/htmx/latest_battles.html', {
        'battles': battles,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def create_battle_group(request):
    if request.method == 'POST':
        new_group = BattleGroup()
        new_group.creator = request.user
        new_group.save()

        query_battles = request.POST.keys()
        battle_ids = []
        key: str
        for key in query_battles:
            if key.startswith('battle-'):
                battle_ids.append(key.removeprefix('battle-'))

        battles = [Battle.objects.get(id=battle_id) for battle_id in battle_ids]

        if len(battles) < 2:
            return HttpResponseBadRequest()

        for battle in battles:
            if battle.uploader_id != request.user.id:
                return HttpResponseBadRequest()

        new_group.battles.add(*battles)

        new_group.save()

        return redirect('battles:view_battle_group', new_group.id)

    battles = Battle.objects.with_prefetch().filter(uploader=request.user).order_by('-id')[:50]
    return render(request, 'battles/groups/create.html', {
        'battles': battles,
    })


@login_required
def create_group_preview(request):
    query_battles = request.GET.keys()
    battle_ids = []
    key: str
    for key in query_battles:
        if key.startswith('battle-'):
            battle_ids.append(key.removeprefix('battle-'))

    battles = [Battle.objects.get(id=battle_id) for battle_id in battle_ids]

    return render(request, 'battles/groups/preview.html', {
        'battles': battles,
    })


def view_battle_group(request, group_id):
    battle_group = get_object_or_404(BattleGroup, id=group_id)

    win_count = battle_group.battles.filter(judgement='WIN').count()
    lose_count = battle_group.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    return render(request, 'battles/groups/view.html', {
        'battle_group': battle_group,
        'win_count': win_count,
        'lose_count': lose_count,
        'win_rate': win_rate,
        'battles': battle_group.battles.with_prefetch().order_by('-played_time'),
    })


def battle_group_opengraph(request, group_id):
    battle_group = get_object_or_404(BattleGroup, id=group_id)
    splashtag = battle_group.battles.latest('played_time').splashtag

    win_count = battle_group.battles.filter(judgement='WIN').count()
    lose_count = battle_group.battles.filter(judgement__in=['LOSE', 'DEEMED_LOSE']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    most_used_weapons = Player.objects.filter(team__battle__in=battle_group.battles.all(), is_self=True) \
                            .values('weapon').annotate(count=models.Count('weapon')).order_by('-count')[:3]
    most_used_weapons = Weapon.objects.filter(pk__in=[weapon['weapon'] for weapon in most_used_weapons])

    return render(request, 'battles/groups/opengraph.html',
                  {
                      'battle_group': battle_group,
                      'splashtag': splashtag,
                      'win_count': win_count,
                      'lose_count': lose_count,
                      'win_rate': win_rate,
                      'most_used_weapons': most_used_weapons,
                  })
