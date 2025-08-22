from typing import Annotated

import strawberry
import strawberry_django
from strawberry import relay, auto

from splatnet_album import models
from users.types import StrawberryUser


@strawberry_django.type(models.AlbumImage)
class AlbumImage(relay.Node):
    splatnet_url: auto
    npln_image_id: auto
    image: auto
    height: auto
    width: auto
    uploaded_at: auto
    user: Annotated["StrawberryUser", strawberry.lazy("users.types")]
