from users.models import User


def userinfo(claims, user: User):
    # Populate claims dict.
    claims['email'] = user.email
    claims['name'] = user.display_name
    claims['preferred_username'] = user.username

    return claims
