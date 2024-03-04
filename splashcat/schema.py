from typing import List

import strawberry
import strawberry_django
from strawberry import relay
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import ListConnectionWithTotalCount
from strawberry_persisted_queries import PersistedQueriesExtension

from battles.schema import BattlesQuery, BattlesMutation
from users.schema import UsersQuery, UsersMutation


@strawberry.type(name="Query")
class Query(BattlesQuery, UsersQuery):
    node: relay.Node = relay.node()


@strawberry.type(name="Mutation")
class Mutation(BattlesMutation, UsersMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
        # PersistedQueriesExtension,
    ],
)
