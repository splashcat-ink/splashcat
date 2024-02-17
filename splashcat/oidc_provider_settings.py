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
