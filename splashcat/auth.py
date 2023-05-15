from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            return False
        if not user.verified_email:
            return False
        return True
