import strawberry
import strawberry_django
import stripe
from strawberry_django.relay import ListConnectionWithTotalCount

from users.types import User


@strawberry.type(name="Query")
class UsersQuery:
    user: User = strawberry_django.node()
    users: ListConnectionWithTotalCount[User] = strawberry_django.connection()


@strawberry.type(name="Mutation")
class UsersMutation:
    @strawberry.mutation
    def begin_subscription(self, price_id: str) -> str:
        stripe.api_key = 'sk_test_51Oq6GcCJmzupkZn7qaGHbXzeo1WVh2nyRDo0U43VeUFD9SaGdepn1wOSazY3QErGdXug5Abl48Ail9rcATyzvTfL00qMATY4e2'
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
