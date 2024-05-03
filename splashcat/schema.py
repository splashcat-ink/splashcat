from typing import List

import strawberry
import strawberry_django
from strawberry import relay
from strawberry.extensions import QueryDepthLimiter, MaxTokensLimiter, ParserCache, ValidationCache
from strawberry.extensions.tracing import ApolloTracingExtension
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info
from strawberry_django.auth.utils import get_current_user
from strawberry_django.optimizer import DjangoOptimizerExtension
from strawberry_django.relay import ListConnectionWithTotalCount
from strawberry_persisted_queries import PersistedQueriesExtension
from strawberry_persisted_queries.django_cache import DjangoPersistedQueryCache
from django.conf import settings

from battles.schema import BattlesQuery, BattlesMutation
from splatnet_album.schema import SplatNetAlbumQuery, SplatNetAlbumMutation
from users.schema import UsersQuery, UsersMutation


@strawberry.type(name="Query")
class Query(BattlesQuery, UsersQuery, SplatNetAlbumQuery):
    node: relay.Node = relay.node()


@strawberry.type(name="Mutation")
class Mutation(BattlesMutation, UsersMutation, SplatNetAlbumMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        DjangoOptimizerExtension,
        PersistedQueriesExtension(cache_backend=DjangoPersistedQueryCache()),
        QueryDepthLimiter(max_depth=10),
        MaxTokensLimiter(max_token_count=1000),
        ParserCache(maxsize=100),
        ValidationCache(maxsize=100),
        # ApolloTracingExtension if settings.DEBUG else None,
    ],
)
