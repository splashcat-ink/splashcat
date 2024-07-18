import json

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseServerError, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from users.models import User


# Create your views here.


@require_POST
@login_required
def create_checkout_session(request, price_id: str):
    if request.user.stripe_customer_id:
        customer_id = request.user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=request.user.email,
        )

        request.user.stripe_customer_id = customer.id
        request.user.save()

        customer_id = customer.id

    session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                'price': price_id,
                'quantity': 1,
            },
        ],
        mode='subscription',
        client_reference_id="user-" + str(request.user.id),
        customer=customer_id,
        customer_update={
            "address": "auto",
            "name": "auto",
        },
        success_url='https://splashcat.ink/sponsors/success/?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://splashcat.ink/sponsor/',
        automatic_tax={'enabled': True},
    )

    return redirect(session.url)


@require_POST
@csrf_exempt
def webhook_received(request):
    request_data = json.loads(request.body.decode())

    if settings.STRIPE_WEBHOOK_SECRET:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request_data, sig_header=signature, secret=settings.STRIPE_WEBHOOK_SECRET)
            data = event['data']
        except Exception as e:
            print(e)
            return HttpResponseServerError()
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    customer_id = data_object['customer']
    user = User.objects.get(stripe_customer_id=customer_id)

    if event_type == 'entitlements.active_entitlement_summary.updated':
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        print(data)
        entitlements = data_object['entitlements']['data']
        entitlements_list = [entitlement['lookup_key'] for entitlement in entitlements]

        user._stripe_entitlements = entitlements_list
        user.save()
    else:
        print('Unhandled event type {}'.format(event_type))

    return HttpResponse("ok")


@require_POST
@login_required
def redirect_to_portal(request):
    user: User = request.user
    if not user.stripe_customer_id:
        return HttpResponseBadRequest()
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url="https://splashcat.ink/users/settings/",
    )
    return redirect(session.url)


def checkout_success(request):
    messages.success(request, 'Thank you for supporting Splashcat!')
    return redirect('home')
