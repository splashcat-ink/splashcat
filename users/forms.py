from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm as DjangoAuthenticationForm
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
            "email",
        )


class AuthenticationForm(DjangoAuthenticationForm):
    error_messages = DjangoAuthenticationForm.error_messages | {
        'email_not_verified': _('Your email address is not verified. Please check your email for a verification link.'),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.verified_email:
            raise forms.ValidationError(
                self.error_messages['email_not_verified'],
                code='email_not_verified',
            )
