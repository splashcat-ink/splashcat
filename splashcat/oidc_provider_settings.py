import re
from functools import wraps

from django.http import HttpResponse
from oidc_provider.lib.errors import BearerTokenError
from oidc_provider.lib.utils.oauth2 import extract_access_token
from oidc_provider.models import Token

from users.models import User


def userinfo(claims, user: User):
    # Populate claims dict.
    claims['email'] = user.email
    claims['name'] = user.display_name
    claims['preferred_username'] = user.username
    claims['picture'] = user.profile_picture.url

    return claims


def idtoken_processing_hook(id_token, user: User, token, request, **kwargs):
    id_token['splashcat_username'] = user.username
    id_token['picture'] = user.profile_picture.url
    return id_token


def openid_auth(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if re.compile(r'^[Bb]earer .+$').match(auth_header):
            access_token = auth_header.split()[1]

            if access_token is not None:
                try:
                    try:
                        token = await Token.objects.select_related("user").aget(access_token=access_token)
                    except Token.DoesNotExist:
                        raise BearerTokenError('invalid_token')

                    if token.has_expired():
                        raise BearerTokenError('invalid_token')
                except BearerTokenError as error:
                    response = HttpResponse(status=error.status)
                    response['WWW-Authenticate'] = 'error="{0}", error_description="{1}"'.format(
                        error.code, error.description)
                    return response
                request.user = token.user

        return await func(request, *args, **kwargs)

    return wrapper
