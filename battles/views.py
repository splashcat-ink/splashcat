import json

import jsonschema
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate

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
            },
        })
    except jsonschema.ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(e)
        )
