import strawberry_django
from strawberry import auto

from . import models


@strawberry_django.type(models.User)
class User:
    id: auto
    username: auto
