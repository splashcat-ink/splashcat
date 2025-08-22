from typing import TYPE_CHECKING, Annotated

import strawberry.relay
import strawberry_django
from strawberry import auto, relay
from strawberry_django.relay import ListConnectionWithTotalCount

from battles.types import StrawberryBattle
from . import models

if TYPE_CHECKING:
    from splatnet_album.types import AlbumImage


@strawberry_django.type(models.User, name="User")
class StrawberryUser(relay.Node):
    username: auto
    saved_favorite_color: auto
    display_name: auto
    preferred_pronouns: auto
    x_battle_division: auto
    profile_picture: auto
    battles: ListConnectionWithTotalCount[StrawberryBattle] = strawberry_django.connection()
    album_images: ListConnectionWithTotalCount[
        Annotated["AlbumImage", strawberry.lazy("splatnet_album.types")]] = strawberry_django.connection()
