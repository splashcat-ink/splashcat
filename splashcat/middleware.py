import datetime
import re

from django.conf import settings
from django.db import InternalError
from django.http import HttpRequest, HttpResponse
from psycopg.errors import ReadOnlySqlTransaction

THRESHOLD_COOKIE = "fly-replay-threshold"
THRESHOLD_TIME = datetime.timedelta(seconds=5)


def get_fly_replay_state(request: HttpRequest):
    header_value = request.headers.get('fly-replay-src', '')
    return re.search(r"(?<=state=)[^;]*", header_value).group(0) if header_value else None


class FlyDotIoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.method != 'GET' and settings.FLY_REGION != settings.FLY_PRIMARY_REGION:
            response = HttpResponse(f'Replaying in {settings.FLY_PRIMARY_REGION} because of http method', status=409,
                                    headers={
                                        'fly-replay': f'region={settings.FLY_PRIMARY_REGION};state=http_method',
                                    })
        elif float(request.COOKIES.get(THRESHOLD_COOKIE, 0)) - datetime.datetime.utcnow().timestamp() > 0 \
                and settings.FLY_REGION != settings.FLY_PRIMARY_REGION:
            response = HttpResponse(f'Replaying in {settings.FLY_PRIMARY_REGION} because of threshold', status=409,
                                    headers={
                                        'fly-replay': f'region={settings.FLY_PRIMARY_REGION};state=threshold',
                                    })
        elif (request.path_info.startswith('/openid/') or request.path_info.startswith('/users/password-reset/')) \
                and settings.FLY_REGION != settings.FLY_PRIMARY_REGION:
            response = HttpResponse(f'Replaying in {settings.FLY_PRIMARY_REGION} by force', status=409,
                                    headers={
                                        'fly-replay': f'region={settings.FLY_PRIMARY_REGION};state=force',
                                    })
        else:
            response = self.get_response(request)

        replay_state = get_fly_replay_state(request)
        if replay_state is not None and replay_state != 'threshold':
            response.set_cookie(THRESHOLD_COOKIE, (datetime.datetime.utcnow() + THRESHOLD_TIME).timestamp(),
                                httponly=True)
            print("set threshold cookie")

        response.headers['x-fly-region'] = settings.FLY_REGION

        return response


class PostgresReadOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_exception(_request: HttpRequest, exception: Exception):
        if isinstance(exception, InternalError):
            # check if it's an error related to read-only replica
            # if so, return a 409 with a fly-replay header
            if isinstance(exception.__cause__, ReadOnlySqlTransaction):
                return HttpResponse(f'Replaying in {settings.FLY_PRIMARY_REGION} because of captured write', status=409,
                                    headers={
                                        'fly-replay': f'region={settings.FLY_PRIMARY_REGION};state=captured_write',
                                    })
        else:
            return None
