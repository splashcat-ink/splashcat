from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def indexnow_api_key(request):
    return HttpResponse(settings.INDEXNOW_API_KEY)
