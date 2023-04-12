import json

from allauth.socialaccount.models import SocialAccount
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from splashcat.decorators import github_webhook
from .models import User


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    return render(request, 'users/profile.html', {'profile_user': user})


@csrf_exempt
@require_http_methods(['POST'])
@github_webhook
def github_sponsors_webhook(request):
    data = json.loads(request.body)
    action = data['action']
    if action == 'created' or action == 'tier_changed':
        try:
            social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
            user = social_account.user
            user.is_splashcat_sponsor = data['sponsorship']['tier']['monthly_price_in_dollars'] >= 5
            user.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
        except SocialAccount.DoesNotExist:
            pass
    elif action == 'edited':
        try:
            social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
            user = social_account.user
            user.is_sponsor_public = data['sponsorship']['privacy_level'] == 'public'
        except SocialAccount.DoesNotExist:
            pass
    elif action == 'cancelled':
        try:
            social_account = SocialAccount.objects.get(provider='github', uid=data['sponsor']['id'])
            user = social_account.user
            user.is_splashcat_sponsor = False
        except SocialAccount.DoesNotExist:
            pass
    return HttpResponse("ok")
