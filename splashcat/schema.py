from typing import List

import strawberry
import strawberry_django
from strawberry import relay
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import ListConnectionWithTotalCount

from battles.types import Battle, Player
from users.types import User


@strawberry.type
class Query:
    node: relay.Node = relay.node()
    user: User = strawberry_django.node()
    users: ListConnectionWithTotalCount[User] = strawberry_django.connection()
    battle: Battle = strawberry_django.node()
    battles: ListConnectionWithTotalCount[Battle] = strawberry_django.connection()
    player: Player = strawberry_django.node()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
)
