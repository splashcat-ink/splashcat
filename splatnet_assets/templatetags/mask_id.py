from django import template
from django.utils.crypto import get_random_string

from splatnet_assets.models import SubWeapon, SpecialWeapon
from users.models import User, SponsorshipTiers

register = template.Library()


@register.filter
def mask_id(weapon_object: SubWeapon | SpecialWeapon):
    random_string = get_random_string(4)
    return f"mask_id_{weapon_object.id}_{random_string}"


@register.simple_tag(takes_context=True)
def get_color(context, uploader: User):
    if uploader.sponsor_tiers[SponsorshipTiers.SPONSOR]:
        context['color'] = uploader.favorite_color
    elif hasattr(context, 'user') and context['user'].is_authenticated:
        context['color'] = context['user'].favorite_color
    if not context.get('color'):
        context['color'] = uploader.battles.latest("played_time").teams.first().color
    return ''
