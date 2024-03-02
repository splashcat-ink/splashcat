from typing import List

import strawberry.relay
import strawberry_django
from strawberry import auto, relay
from strawberry_django.relay import ListConnectionWithTotalCount

from battles.types import Battle
from . import models


@strawberry_django.type(models.User)
class User(relay.Node):
    username: auto
    saved_favorite_color: auto
    display_name: auto
    preferred_pronouns: auto
    x_battle_division: auto
    profile_picture: auto
    battles: ListConnectionWithTotalCount[Battle] = strawberry_django.connection()
