from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from users.models import User


class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = "users/widgets/image.html"


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "display_name",
            "profile_picture",
            "saved_favorite_color",
        )
        labels = {
            "saved_favorite_color": _("Favorite Color"),
        }
        help_texts = {
            "saved_favorite_color": _("Shown when you sponsor Splashcat."),
        }
        widgets = {
            "profile_picture": ImageWidget,
        }


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "display_name",
        )
