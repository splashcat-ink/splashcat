from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from splatnet_assets.fields import ColorField, Color


# Create your models here.


class User(AbstractUser):
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
    display_name = models.CharField(_("display name"), max_length=30, blank=True)
    first_name = None
    last_name = None

    profile_picture = models.ImageField(_("profile picture"), upload_to='profile_pictures', blank=True, null=True)
    saved_favorite_color = ColorField(default="000000ff")

    @property
    def favorite_color(self):
        if self.github_link.is_sponsor:
            return self.saved_favorite_color
        else:
            return Color.from_hex("000000ff")

    @property
    def display_sponsor_badge(self):
        return self.github_link.is_sponsor and self.github_link.is_sponsor_public

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


class GitHubLink(models.Model):
    class Meta:
        verbose_name = "GitHub Link"

    linked_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='github_link', blank=True,
                                       null=True)
    github_id = models.IntegerField(unique=True)
    is_sponsor = models.BooleanField(default=False)
    is_sponsor_public = models.BooleanField(default=False)
    sponsorship_amount_usd = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
