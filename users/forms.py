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
            "profile_cover",
            "page_background",
            "saved_favorite_color",
            "x_battle_division",
            "preferred_pronouns",
            "coral_friend_url",
        )
        labels = {
            "saved_favorite_color": _("Favorite Color"),
        }
        help_texts = {
            "saved_favorite_color": _("Shown when you sponsor Splashcat."),
        }
        widgets = {
            "profile_cover": ImageWidget,
            "page_background": ImageWidget,
        }

    profile_picture = forms.ImageField(
        label=_("Profile Picture"),
        required=True,
        widget=ImageWidget()
    )

    # override the attributes on the preferred_pronouns field to prevent autocomplete
    preferred_pronouns = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "autocorrect": "off",
            }
        )
    )

    coral_friend_url = forms.URLField(
        required=False,
        error_messages={
            'invalid': _("Enter a valid Nintendo Switch Friend URL from the Nintendo Switch Online app."),
        },
        widget=forms.URLInput(
            attrs={
                'class': '!w-full',
            }
        )
    )


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

    def clean(self):
        username = self.cleaned_data.get("username")
        if username is not None:
            try:
                user = User.objects.get(username=username)
                if user:
                    if not user.verified_email:
                        raise forms.ValidationError(
                            self.error_messages['email_not_verified'],
                            code='email_not_verified',
                        )
            except User.DoesNotExist:
                pass
        super().clean()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.verified_email:
            raise forms.ValidationError(
                self.error_messages['email_not_verified'],
                code='email_not_verified',
            )


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(label=_("Email address"), max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email is not None:
            user = User.objects.get(email=email)
            if user:
                if user.verified_email:
                    raise forms.ValidationError(
                        _("This email address is already verified."),
                        code='email_already_verified',
                    )
        return email

    def send_email(self):
        email = self.cleaned_data.get("email")
        if email is not None:
            user = User.objects.get(email=email)
            if user:
                user.send_verification_email()
