import json

import jsonschema
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate

from battles.models import Battle
from splashcat.decorators import api_auth_required


# Create your views here.

@csrf_exempt
@require_http_methods(['POST'])
@api_auth_required
def upload_battle(request):
    request_data = request.body
    if request.content_type == 'application/json':
        data = json.loads(request_data)
    elif request.content_type == 'application/x-messagepack':
        import msgpack
        data = msgpack.unpackb(request_data)

    try:
        validate(data, {
            'type': 'object',
            'properties': {
                'battle': {
                    'type': 'object',
                },
                'data_type': {
                    'enum': ['splatnet3']
                }
            },
        })
    except jsonschema.ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(e)
        )

    # passed input validation, validate the battle data

    with open('splatnet_assets/schemas/splatnet3.json') as f:
        schema = json.load(f)

    try:
        validate(data['battle'], schema)
    except jsonschema.ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(e)
        )

    # passed input validation, save the battle data

    battle = Battle(data_type="splatnet3", raw_data=data['battle'], uploader=request.user)
    battle.save()

    return JsonResponse({
        'status': 'ok',
        'battle_id': battle.id,
    })
