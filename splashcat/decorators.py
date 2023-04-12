import hashlib
import hmac
from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden

from users.models import ApiKey
from .settings import GITHUB_SPONSORS_WEBHOOK_TOKEN


def api_auth_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get('Authorization', '').split(' ')[-1]
        try:
            api_key = ApiKey.objects.get(key=api_key)
        except ObjectDoesNotExist:
            return HttpResponseForbidden()
        request.user = api_key.user

    return wrapper


def github_webhook(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        signature = f'''
        sha256={hmac.new(GITHUB_SPONSORS_WEBHOOK_TOKEN.encode(), request.body, hashlib.sha256).hexdigest()}
        '''.strip()
        if hmac.compare_digest(signature, request.headers.get('X-Hub-Signature-256')):
            return func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return wrapper
