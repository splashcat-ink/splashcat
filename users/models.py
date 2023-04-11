from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class User(AbstractUser):
    is_splashcat_sponsor = models.BooleanField(default=False)
    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    display_name = models.CharField(_("display name"), max_length=150, blank=True)
    first_name = None
    last_name = None

    def get_full_name(self):
        return self.display_name.strip()

    def get_short_name(self):
        return self.display_name.strip()
