import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from users.types import User


@strawberry.type
class Query:
    users: list[User] = strawberry_django.field()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
)
