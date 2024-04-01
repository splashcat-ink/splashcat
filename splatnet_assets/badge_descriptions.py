import re

from splatnet_assets.models import NameplateBadge, LocalizationString

level_regex = re.compile(r"_Lv\d{2}")
group_regex = re.compile(r"\[group=0004.+]")

bad_badge_prefixes = [
    "WeaponLevel_",
    "WinCount_WeaponSp_",
    "GearTotalRarity_",
    # "CoopGrade_Normal_",
    # "CoopRareEnemyKillNum_",
    # "CoopBossKillNum_",
]

salmon_run_badge_prefixes = [
    "CoopGrade_Normal_",
    "CoopRareEnemyKillNum_",
    "CoopBossKillNum_",
]


def has_prefix(s, prefixes):
    return any(s.startswith(prefix) for prefix in prefixes)


def get_proper_badge_localization(badge: NameplateBadge, locale: str = None) -> str:
    localization_string = badge.description.get_string(locale)
    if has_prefix(badge.internal_id, bad_badge_prefixes):
        # find replacement string and replace
        object_id = badge.internal_id
        for prefix in bad_badge_prefixes:
            object_id = object_id.replace(prefix, "")
        object_id = level_regex.sub("", object_id)

        try:
            object_name: LocalizationString = LocalizationString.objects.get(internal_id=object_id)
        except LocalizationString.DoesNotExist:
            return ""
        localization_string = group_regex.sub(object_name.string, localization_string)
    elif has_prefix(badge.internal_id, salmon_run_badge_prefixes):
        localization_string = ""
    return localization_string
