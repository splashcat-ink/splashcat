from django.shortcuts import render, get_object_or_404

from .models import User


# Create your views here.

def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    return render(request, 'users/profile.html', {'user': user})
