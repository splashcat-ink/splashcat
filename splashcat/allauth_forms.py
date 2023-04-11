from typing import OrderedDict

import django.forms
from allauth.account.forms import *


def overwrite_classes(fields: OrderedDict[str, django.forms.Field]):
    print(fields)
    for name, field in fields.items():
        field.widget.attrs['class'] = 'bg-gray-900 rounded'


class SplashcatLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)


class SplashcatResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        overwrite_classes(self.fields)
