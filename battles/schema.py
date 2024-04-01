import strawberry
import strawberry_django
from strawberry_django.relay import ListConnectionWithTotalCount

from battles.types import Battle, Player


@strawberry.type(name="Query")
class BattlesQuery:
    battle: Battle = strawberry_django.node()
    battles: ListConnectionWithTotalCount[Battle] = strawberry_django.connection()
    player: Player = strawberry_django.node()


@strawberry.type(name="Mutation")
class BattlesMutation:
    pass
