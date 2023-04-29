from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class AccountSettingsForm(forms.Form):
    pass


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "display_name",
        )
