import random

from django import template
from django.utils.crypto import get_random_string

from splatnet_assets.fields import Color
from splatnet_assets.models import SubWeapon, SpecialWeapon
from users.models import User, SponsorshipTiers

register = template.Library()


@register.filter
def mask_id(weapon_object: SubWeapon | SpecialWeapon):
    random_string = get_random_string(4)
    return f"mask_id_{weapon_object.id}_{random_string}"


random_color_options = [
    Color.from_hex("cd43a6"),
]


@register.simple_tag(takes_context=True)
def get_color(context, uploader: User, use_random_color: bool):
    user = context.get('user')
    if uploader.sponsor_tiers[SponsorshipTiers.SPONSOR]:
        context['color'] = uploader.favorite_color
    elif user and user.is_authenticated:
        context['color'] = context['user'].favorite_color
    if not context.get('color'):
        context['color'] = random.choice(random_color_options) if use_random_color else uploader.battles.latest(
            "played_time").teams.first().color
    return ''
