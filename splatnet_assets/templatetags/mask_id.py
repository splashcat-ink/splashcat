from django import template

from splatnet_assets.models import SubWeapon, SpecialWeapon
from users.models import User

register = template.Library()


@register.filter
def mask_id(weapon_object: SubWeapon | SpecialWeapon):
    return f"mask_id_{weapon_object.id}"


@register.simple_tag(takes_context=True)
def get_color(context, uploader: User):
    if hasattr(uploader, 'github_link') and uploader.github_link.is_sponsor:
        context['color'] = uploader.favorite_color
    else:
        context['color'] = context['user'].favorite_color
    return ''
