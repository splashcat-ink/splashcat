import json

import jsonschema
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate

from battles.data_exports import get_latest_export_download_url
from battles.models import *
from battles.parsers.splashcat import parse_splashcat
from battles.parsers.splatnet3 import parse_splatnet3
from battles.utils import BattleAlreadyExistsError
from splashcat.decorators import api_auth_required
from users.models import User


# Create your views here.

def view_battle(request, battle_id):
    battle = get_object_or_404(Battle.objects.with_prefetch(), id=battle_id)
    return render(request, 'battles/view_battle.html', {
        'battle': battle,
    })


def redirect_from_splatnet_id(request, uploader_username, splatnet_id):
    battle = get_object_or_404(Battle, splatnet_id=splatnet_id, uploader__username=uploader_username)
    return redirect('view_battle', battle_id=battle.id)


def get_battle_json(request, battle_id):
    battle = get_object_or_404(Battle.objects.with_prefetch(), id=battle_id)
    data = serializers.serialize('json', [battle])
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
    recent_battles = request.user.battles.order_by('-played_time')[:100]
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

    try:
        validate(data, {
            'type': 'object',
            'properties': {
                'battle': {
                    'type': 'object',
                },
                'data_type': {
                    'enum': ['splatnet3', 'splashcat']
                }
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
