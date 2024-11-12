import datetime
import hashlib
from array import array
from datetime import timedelta
from enum import Enum
from io import BytesIO
import re
from PIL import Image, ImageOps
import io
from uuid import uuid4

import requests
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import models
from django.db.models import Prefetch
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django_choices_field import TextChoicesField

import django.contrib.auth.models as django_auth_models

from battles.models import Battle, Player
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

github_sponsors_to_entitlements = {
    SponsorshipTiers.SPONSOR: ["sponsor-badge", "favorite-color", "page-backgrounds", ],
    SponsorshipTiers.S_PLUS_PONSOR: ["sponsor-badge", "favorite-color", "page-backgrounds", "ai-battle-descriptions", ],
    SponsorshipTiers.X_PONSOR: ["sponsor-badge", "favorite-color", "page-backgrounds", "ai-battle-descriptions",
                                "assistant"],
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
    profile_cover = models.ImageField(_("profile cover"), upload_to='profile_covers', blank=True, null=True)
    page_background = models.ImageField(_("page background"), upload_to='page_backgrounds', blank=True, null=True)
    saved_favorite_color = ColorField(default="9333eaff")
    approved_to_upload_videos = models.BooleanField(_("approved to upload videos"), default=False)
    video_collection_id = models.CharField(_("video collection id"), max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField(_("stripe customer id"), max_length=100, blank=True, null=True)
    _stripe_entitlements = models.JSONField(_("stripe entitlements"), default=list, blank=True)
    coral_friend_url = models.URLField(_("Nintendo Switch Online app friend URL"), blank=True, null=True,
                                       validators=[URLValidator(
                                           regex=r"^https:\/\/lounge\.nintendo\.com\/friendcode\/\d{4}-\d{4}-\d{4}\/[A-Za-z0-9]{10}$")])

    def save(self, *args, **kwargs):
        for field_name in ['profile_picture', 'profile_cover', 'page_background']:
            image = getattr(self, field_name)
            if image and hasattr(image, 'name'):
                try:
                    with Image.open(image) as img:
                        img = ImageOps.exif_transpose(img)

                        img_no_exif = Image.new(img.mode, img.size)
                        img_no_exif.putdata(list(img.getdata()))

                        buffer = io.BytesIO()

                        output_format = 'JPEG'
                        img_no_exif.save(buffer, format=output_format)
                        buffer.seek(0)

                        new_filename = f"{uuid4()}.{output_format.lower()}"
                        image.save(new_filename, ContentFile(buffer.read()), save=False)
                except Exception as e:
                    print(f"Error processing image for {field_name}: {e}")

        super().save(*args, **kwargs)

    @property
    def entitlements(self):
        entitlements = set(self._stripe_entitlements)

        github_sponsorship_tiers = self.sponsor_tiers
        for tier, active in github_sponsorship_tiers.items():
            if active:
                tier_entitlements = github_sponsors_to_entitlements[tier]
                for entitlement in tier_entitlements:
                    entitlements.add(entitlement)

        return entitlements

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
        if "favorite-color" in self.entitlements:
            return self.saved_favorite_color

    @property
    def display_sponsor_badge(self):
        if self.github_link and self.github_link.is_sponsor:
            return self.sponsor_tiers[SponsorshipTiers.SPONSOR] and self.github_link.is_sponsor_public
        else:
            return "sponsor-badge" in self.entitlements

    @property
    def sponsor_tiers(self) -> dict[SponsorshipTiers, bool]:
        if hasattr(self, 'github_link') and self.github_link.is_sponsor:
            sponsorship_amount = self.github_link.sponsorship_amount_usd
        else:
            sponsorship_amount = 0
        return {tier: sponsorship_amount >= amount for tier, amount in sponsorship_tier_costs.items()}

    @property
    def has_splashcat_assistant(self):
        return "assistant" in self.entitlements

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
        return ("sponsor-badge" in self.entitlements) or \
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
            player_prefetch_queryset = Player.objects \
                .select_related('title_adjective__string', 'title_subject__string', 'nameplate_background__image',
                                'nameplate_badge_1__image', 'nameplate_badge_2__image', 'nameplate_badge_3__image',
                                'nameplate_badge_1__description', 'nameplate_badge_2__description',
                                'nameplate_badge_3__description').filter(is_self=True)
            player_prefetch = Prefetch(
                'teams__players',
                queryset=player_prefetch_queryset,
            )
            return self.battles.prefetch_related(player_prefetch).latest('played_time').splashtag
        except Battle.DoesNotExist:
            return None

    def get_npln_id(self):
        try:
            player_prefetch_queryset = Player.objects \
                .only('npln_id').filter(is_self=True)
            player_prefetch = Prefetch(
                'teams__players',
                queryset=player_prefetch_queryset,
            )
            return self.battles.prefetch_related(player_prefetch).latest('played_time').player.npln_id
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


class CustomAnonymousUser(django_auth_models.AnonymousUser):
    @property
    def entitlements(self):
        return set()


django_auth_models.AnonymousUser = CustomAnonymousUser
