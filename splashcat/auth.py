from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError

from users.forms import AuthenticationForm


class AuthBackend(ModelBackend):
    def user_can_authenticate(self, user):
        super().user_can_authenticate(user)
        if not user.verified_email:
            raise ValidationError(
                AuthenticationForm.error_messages['email_not_verified'],
                code='email_not_verified',
            )
