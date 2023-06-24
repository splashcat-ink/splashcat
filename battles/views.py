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

from battles.data_exports import get_latest_export_download_url
from battles.models import *
from battles.parsers.splashcat import parse_splashcat
from battles.parsers.splatnet3 import parse_splatnet3
from battles.tasks import generate_battle_description
from battles.utils import BattleAlreadyExistsError
from splashcat.decorators import api_auth_required
from users.models import User, SponsorshipTiers


# Create your views here.

def view_battle(request, battle_id):
    battle: Battle = get_object_or_404(Battle.objects.with_prefetch(True), id=battle_id)
    return render(request, 'battles/view_battle.html', {
        'battle': battle,
    })


def battle_opengraph(request, battle_id):
    battle: Battle = get_object_or_404(Battle.objects.with_prefetch(True), id=battle_id)

    team_bar_display = []

    total = 0
    for i, team in enumerate(battle.teams.all()):
        team_value = 0
        display_text = ""
        if battle.vs_rule != battle.VsRule.TURF_WAR and team.score is not None:
            total += team.score
            team_value = team.score
            display_text = _("KNOCKOUT!") if \
                team.score == 100 and battle.knockout == KnockoutJudgement.WIN or \
                battle.knockout == KnockoutJudgement.LOSE else _("Score: %(score)d") % {'score': team.score}
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

    for display_object in team_bar_display:
        display_object['width'] = display_object['team_value'] / max(total, 1) * 100

    return render(request, 'battles/battle_opengraph.html', {
        'battle': battle,
        'team_bar_display': team_bar_display,
    })


def redirect_from_splatnet_id(request, uploader_username, splatnet_id):
    battle = get_object_or_404(Battle, splatnet_id=splatnet_id, uploader__username=uploader_username)
    return redirect('battles:view_battle', battle_id=battle.id)


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
        return HttpResponseBadRequest(e, content_type='text/plain')

    if data['data_type'] == 'splatnet3':
        try:
            battle = parse_splatnet3(data, request)
        except jsonschema.ValidationError as e:
            return HttpResponseBadRequest(e, content_type='text/plain')
        except BattleAlreadyExistsError:
            return HttpResponseBadRequest(
                json.dumps({
                    'status': 'error',
                    'error': 'battle already exists',
                })
            )
        except NotImplementedError:
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
            return HttpResponseBadRequest(e, content_type='text/plain')
        except BattleAlreadyExistsError as e:
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

    if user.sponsor_tiers[SponsorshipTiers.S_PLUS_PONSOR]:
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
    battles = request.user.battles.order_by('-id')[:10]
    return render(request, 'battles/htmx/latest_battles.html', {
        'battles': battles,
    })
