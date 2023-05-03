import json

import jsonschema
from django.core import serializers
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate

from battles.models import *
from battles.parsers.splashcat import parse_splashcat
from battles.parsers.splatnet3 import parse_splatnet3, BattleAlreadyExistsError
from splashcat.decorators import api_auth_required


# Create your views here.

def view_battle(request, battle_id):
    battle = get_object_or_404(Battle.objects.with_prefetch(), id=battle_id)
    return render(request, 'battles/view_battle.html', {
        'battle': battle,
    })


def get_battle_json(request, battle_id):
    battle = get_object_or_404(Battle.objects.with_prefetch(), id=battle_id)
    data = serializers.serialize('json', [battle])
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
@require_http_methods(['POST'])
@api_auth_required
@transaction.atomic
def upload_battle(request):
    data = request.body
    if request.content_type == 'application/json':
        data = json.loads(data)
    elif request.content_type == 'application/x-messagepack':
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
        return HttpResponseBadRequest(
            json.dumps(e)
        )

    if data['data_type'] == 'splatnet3':
        try:
            battle = parse_splatnet3(data, request)
        except jsonschema.ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps(e)
            )
        except BattleAlreadyExistsError as e:
            return HttpResponseBadRequest(
                json.dumps({
                    'status': 'error',
                    'error': 'battle already exists',
                })
            )
        except NotImplementedError as e:
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
            return HttpResponseBadRequest(
                json.dumps(e)
            )
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
