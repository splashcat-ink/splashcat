import datetime
import hashlib
from datetime import timedelta
from enum import Enum
from io import BytesIO
import re

import requests
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django_choices_field import TextChoicesField

from battles.models import Battle
from splatnet_assets.common_model_choices import XBattleDivisions
from splatnet_assets.fields import ColorField

# Create your models here.

sponsor_perks = {
    "badge": {
        "minimum_tier": "sponsor",
    },
    "favorite_color": {
        "minimum_tier": "sponsor",
    },
    "gpt_description": {
        "minimum_tier": "s+ponsor",
    },
    "assistant": {
        "minimum_tier": "xponsor",
    },
}


class SponsorshipTiers(Enum):
    SPONSOR = "sponsor"
    S_PLUS_PONSOR = "s+ponsor"
    X_PONSOR = "xponsor"


sponsorship_tier_costs = {
    SponsorshipTiers.SPONSOR: 5,
    SponsorshipTiers.S_PLUS_PONSOR: 10,
    SponsorshipTiers.X_PONSOR: 15,
}


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
    preferred_pronouns = models.CharField(_("preferred pronouns"), max_length=20, blank=True, null=True)

    x_battle_division = TextChoicesField(verbose_name=_("X Battle division"), choices_enum=XBattleDivisions,
                                         default=XBattleDivisions.UNSPECIFIED)

    last_data_export = models.DateTimeField(_("last data export"), blank=True, null=True)
    data_export_pending = models.BooleanField(_("data export pending"), default=False)

    profile_picture = models.ImageField(_("profile picture"), upload_to='profile_pictures', blank=True, null=True)
    saved_favorite_color = ColorField(default="9333eaff")
    approved_to_upload_videos = models.BooleanField(_("approved to upload videos"), default=False)
    video_collection_id = models.CharField(_("video collection id"), max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField(_("stripe customer id"), max_length=100, blank=True, null=True)
    coral_friend_url = models.URLField(_("Nintendo Switch Online app friend URL"), blank=True, null=True,
                                       validators=[URLValidator(
                                           regex=r"^https:\/\/lounge\.nintendo\.com\/friendcode\/\d{4}-\d{4}-\d{4}\/[A-Za-z0-9]{10}$")])

    @property
    def coral_friend_code(self):
        if not self.coral_friend_url:
            return None
        matches = re.search(r"^https://lounge\.nintendo\.com/friendcode/(\d{4}-\d{4}-\d{4})/[A-Za-z0-9]{10}$",
                            self.coral_friend_url)
        if matches:
            return matches.group(1)

    @property
    def favorite_color(self):
        if self.sponsor_tiers[SponsorshipTiers.SPONSOR] is True:
            return self.saved_favorite_color

    @property
    def display_sponsor_badge(self):
        return self.sponsor_tiers[SponsorshipTiers.SPONSOR] and self.github_link.is_sponsor_public

    @property
    def sponsor_tiers(self) -> dict[SponsorshipTiers, bool]:
        if hasattr(self, 'github_link') and self.github_link.is_sponsor:
            sponsorship_amount = self.github_link.sponsorship_amount_usd
        else:
            sponsorship_amount = 0
        return {tier: sponsorship_amount >= amount for tier, amount in sponsorship_tier_costs.items()}

    @property
    def has_splashcat_assistant(self):
        return self.sponsor_tiers[SponsorshipTiers.X_PONSOR]

    def get_full_name(self):
        return self.display_name.strip()

    def get_short_name(self):
        return self.display_name.strip()

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.username})

    @property
    def has_mastodon_account(self):
        return False  # Token.objects.filter(user=self, client_id=1).exists()

    @property
    def is_verified_for_export_download(self):
        # used for data exports
        # verified users have been on splashcat for at least 24 hours and have at least 5 battles, or are a sponsor
        return self.sponsor_tiers[SponsorshipTiers.SPONSOR] or \
            (
                    self.date_joined < datetime.datetime.now(datetime.timezone.utc) - timedelta(days=1) and
                    self.battles.count() >= 5 and
                    self.verified_email
            )

    def get_latest_battle(self):
        try:
            return self.battles.with_prefetch().latest('played_time')
        except Battle.DoesNotExist:
            return None

    @property
    def get_splashtag(self):
        try:
            return self.battles.with_prefetch().latest('played_time').splashtag
        except Battle.DoesNotExist:
            return None

    def get_npln_id(self):
        try:
            return self.battles.with_prefetch().latest('played_time').player.npln_id
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

    def get_groups(self):
        return list(self.groups_owned.all()) + list(self.group_set.all())

    def save_splatoon_identicon(self):
        response = requests.get('https://fancy.org.uk/api/nxapi/lhub-icon/splatoon-3')
        image_data = BytesIO(response.content)
        image = ContentFile(image_data.getvalue())

        image_hash = hashlib.sha256(image_data.getvalue()).hexdigest()

        self.profile_picture.save(f'identicon-{image_hash}.png', image, save=True)


def generate_key():
    return get_random_string(30)


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


class ProfileUrl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile_urls")
    url = models.URLField()
    is_rel_me_verified = models.BooleanField(default=False)
