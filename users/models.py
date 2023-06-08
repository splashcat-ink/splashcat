import datetime
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from battles.models import Battle
from splatnet_assets.common_model_choices import XBattleDivisions
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
    display_name = models.CharField(_("display name"), max_length=30)
    first_name = None
    last_name = None
    verified_email = models.BooleanField(_("verified email"), default=False)
    email = models.EmailField(_("email address"), unique=True)

    x_battle_division = models.CharField(_("X Battle division"), max_length=20, choices=XBattleDivisions.choices,
                                         default=XBattleDivisions.UNSPECIFIED)

    last_data_export = models.DateTimeField(_("last data export"), blank=True, null=True)
    data_export_pending = models.BooleanField(_("data export pending"), default=False)

    profile_picture = models.ImageField(_("profile picture"), upload_to='profile_pictures', blank=True, null=True)
    saved_favorite_color = ColorField(default="9333eaff")

    @property
    def favorite_color(self):
        if hasattr(self, 'github_link') and self.github_link.is_sponsor:
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

    @property
    def is_verified_for_export_download(self):
        # used for data exports
        # verified users have been on splashcat for at least 24 hours and have at least 5 battles, or are a sponsor
        return self.github_link.is_sponsor or \
            (
                    self.date_joined < datetime.datetime.now(datetime.timezone.utc) - timedelta(days=1) and
                    self.battles.count() >= 5 and
                    self.verified_email
            )

    @property
    def get_splashtag(self):
        try:
            return self.battles.with_prefetch().latest('played_time').splashtag
        except Battle.DoesNotExist:
            return None

    def send_verification_email(self):
        if not self.verified_email:
            site = Site.objects.get_current()
            token = default_token_generator.make_token(self)
            message_contents = render_to_string('emails/verify_email.txt', {
                'user': self,
                'token': token,
                'site': site,
            })
            self.email_user('Verify your email address', message_contents)


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
    github_username = models.CharField(max_length=39)
    is_sponsor = models.BooleanField(default=False)
    is_sponsor_public = models.BooleanField(default=False)
    sponsorship_amount_usd = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
