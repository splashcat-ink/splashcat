from django import template

from splatnet_assets.models import SubWeapon, SpecialWeapon

register = template.Library()


@register.filter
def mask_id(weapon_object: SubWeapon | SpecialWeapon):
    return f"mask_id_{weapon_object.id}"
