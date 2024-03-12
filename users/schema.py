from typing import cast

import strawberry
import strawberry_django
import stripe
from django.core.exceptions import ValidationError
from strawberry.types import Info
from strawberry_django.auth.utils import get_current_user
from strawberry_django.relay import ListConnectionWithTotalCount

from users.types import User


@strawberry.type(name="Query")
class UsersQuery:
    user: User = strawberry_django.node()
    users: ListConnectionWithTotalCount[User] = strawberry_django.connection()

    @strawberry_django.field()
    def current_user(self, info: Info) -> User | None:
        user = get_current_user(info)
        if user.is_authenticated:
            return cast(User, user)
        else:
            return None


@strawberry.type(name="Mutation")
class UsersMutation:
    @strawberry.mutation
    def begin_subscription(self, price_id: str) -> str:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url='https://splashcat.ink/success.html',
            cancel_url='https://splashcat.ink/cancel.html',
        )
        return checkout_session.url
