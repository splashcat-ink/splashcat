import base64
from typing import Optional

from django.db.models.functions import Length

from battles.formats.vs_history_detail import BaseGear, Badge
from battles.models import PlayerGear
from splatnet_assets.models import LocalizationString, Gear, Ability, NameplateBadge


def get_splatnet_int_id(splatnet_id: str):
    splatnet_id = base64.b64decode(splatnet_id).decode('utf-8')
    return int(splatnet_id.split('-')[1])


def get_title_parts_from_string(title: str):
    localization_objects = LocalizationString.objects \
        .filter(type=LocalizationString.Type.TITLE_ADJECTIVE) \
        .order_by(Length('string_en_us').desc()) \
        .filter(string_en_us__icontains=title.split(' ')[0]) \
        .all()

    localization_object: LocalizationString
    for localization_object in localization_objects:
        if localization_object.string_en_us in title:
            subject_part = title.replace(localization_object.string_en_us, '')[1:]
            subject_localization: LocalizationString = LocalizationString.objects \
                .filter(type=LocalizationString.Type.TITLE_SUBJECT) \
                .filter(string_en_us__iexact=subject_part) \
                .first()
            if subject_localization:
                return localization_object.titleadjective, subject_localization.titlesubject

    return None, None


def get_ability(ability: str):
    try:
        return Ability.objects.get(name__string_en_us__iexact=ability)
    except Ability.DoesNotExist:
        return Ability.objects.get(internal_id='None')


def get_player_gear(gear: BaseGear):
    gear = PlayerGear(
        gear=Gear.objects.get(name__string_en_us=gear.name),
        primary_ability=get_ability(gear.primary_gear_power.name),
        secondary_ability_1=get_ability(gear.additional_gear_powers[0].name),
        secondary_ability_2=get_ability(gear.additional_gear_powers[1].name)
        if len(gear.additional_gear_powers) > 1 else None,
        secondary_ability_3=get_ability(gear.additional_gear_powers[2].name)
        if len(gear.additional_gear_powers) > 2 else None,
    )
    gear.save()
    return gear


def get_npln_id(data: str):
    return base64.b64decode(data).decode('utf-8').split(':')[-1].split('-')[-1]


def get_nameplate_badge(badge: Optional[Badge]):
    if badge is None:
        return None
    return NameplateBadge.objects.get(splatnet_id=get_splatnet_int_id(badge.id))


class BattleAlreadyExistsError(Exception):
    pass
