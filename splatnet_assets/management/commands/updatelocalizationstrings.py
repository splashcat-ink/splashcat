import requests
from django.core.management import BaseCommand

from splatnet_assets.models import LocalizationString

locale_json_url = dict(
    string_de_de='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUde_full.json',
    string_en_gb='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUen_full.json',
    string_en_us='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/USen_full.json',
    string_es_es='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUes_full.json',
    string_es_mx='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/USes_full.json',
    string_fr_ca='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/USfr_full.json',
    string_fr_fr='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUfr_full.json',
    string_it_it='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUit_full.json',
    string_ja_jp='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/JPja_full.json',
    string_ko_kr='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/KRko_full.json',
    string_nl_nl='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUnl_full.json',
    string_ru_ru='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/EUru_full.json',
    string_zh_cn='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/CNzh_full.json',
    string_zh_tw='https://raw.githubusercontent.com/Leanny/leanny.github.io/master/splat3/data/language/TWzh_full.json',
)

types_to_store = {
    'CommonMsg/Byname/BynameAdjective': LocalizationString.Type.TITLE_ADJECTIVE,
    'CommonMsg/Byname/BynameSubject': LocalizationString.Type.TITLE_SUBJECT,
    'CommonMsg/Gear/GearName_Head': LocalizationString.Type.HEAD_GEAR,
    'CommonMsg/Gear/GearName_Clothes': LocalizationString.Type.CLOTHING_GEAR,
    'CommonMsg/Gear/GearName_Shoes': LocalizationString.Type.SHOES_GEAR,
    'CommonMsg/Gear/GearPowerName': LocalizationString.Type.ABILITY,
    'CommonMsg/Gear/GearPowerExp': LocalizationString.Type.ABILITY_DESCRIPTION,
    'CommonMsg/Gear/GearBrandName': LocalizationString.Type.BRAND,
    'CommonMsg/VS/VSStageName': LocalizationString.Type.STAGE,
    'CommonMsg/Weapon/WeaponName_Main': LocalizationString.Type.WEAPON_NAME,
    'CommonMsg/Weapon/WeaponName_Sub': LocalizationString.Type.SUB_WEAPON_NAME,
    'CommonMsg/Weapon/WeaponName_Special': LocalizationString.Type.SPECIAL_WEAPON_NAME,
}


class Command(BaseCommand):
    help = 'Scrapes data from https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/language and stores ' \
           'in the database.'

    def handle(self, *args, **options):
        locales = {}

        for locale, url in locale_json_url.items():
            locales[locale] = requests.get(url).json()

        for locale_key, locale_type in types_to_store.items():
            internal_ids: dict = locales['string_en_us'][locale_key]
            for internal_id in internal_ids.keys():
                locale_strings = {}
                for locale, locale_data in locales.items():
                    locale_strings[locale] = locale_data[locale_key][internal_id]

                new_localization_string, created = LocalizationString.objects.update_or_create(
                    internal_id=internal_id, type=locale_type, defaults=locale_strings)
                if created:
                    self.stdout.write(f'Created {new_localization_string.internal_id} ({new_localization_string.type})')

            self.stdout.write(f'Finished {locale_type}')

        self.stdout.write('Finished updating localization strings')
