from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


# Create your models here.


class User(AbstractUser):
    is_splashcat_sponsor = models.BooleanField(default=False)
    is_sponsor_public = models.BooleanField(default=False)
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

    profile_picture = models.ImageField(_("profile picture"), upload_to='profile_pictures', blank=True, null=True)

    def get_full_name(self):
        return self.display_name.strip()

    def get_short_name(self):
        return self.display_name.strip()

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.username})


def generate_key():
    return get_random_string(20)


class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=40, primary_key=True, unique=True, default=generate_key)
    created = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'API Key {self.key} (@{self.user.username})'
