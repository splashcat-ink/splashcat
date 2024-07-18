from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from sponsors.views import *

app_name = "sponsors"
urlpatterns = [
    path('create-checkout-session/<str:price_id>/', create_checkout_session, name='create_checkout_session'),
    path('webhook/', webhook_received, name='webhook_received'),
    path('portal/', redirect_to_portal, name='redirect_to_portal'),
]
