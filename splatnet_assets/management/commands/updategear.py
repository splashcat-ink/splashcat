import requests
from django.core.management import BaseCommand

from splatnet_assets.models import *
from ._private import get_latest_version, download_image_from_path


def get_gear_urls(version: str):
    prefix = f'https://leanny.github.io/splat3/data/mush/{version}'
    return {
        Gear.GearType.HEAD: f'{prefix}/GearInfoHead.json',
        Gear.GearType.CLOTHING: f'{prefix}/GearInfoClothes.json',
        Gear.GearType.SHOES: f'{prefix}/GearInfoShoes.json',
    }


def get_localization_type_from_gear_type(gear_type: Gear.GearType):
    if gear_type == Gear.GearType.HEAD:
        return LocalizationString.Type.HEAD_GEAR
    elif gear_type == Gear.GearType.CLOTHING:
        return LocalizationString.Type.CLOTHING_GEAR
    elif gear_type == Gear.GearType.SHOES:
        return LocalizationString.Type.SHOES_GEAR
    else:
        raise ValueError(f'Unknown gear type {gear_type}')


class Command(BaseCommand):
    help = 'Scrapes gear data from https://github.com/Leanny/leanny.github.io/tree/master/splat3/data/mush and stores ' \
           'it in the database.'

    def handle(self, *args, **options):
        latest_version = get_latest_version()

        print(f'Latest version: {latest_version}')
        print('Doing skills...')

        skills_url = f'https://leanny.github.io/splat3/data/parameter/' \
                     f'{latest_version}/misc/spl__GearSkillTraitsParam.spl__GearSkillTraitsParam.json'

        skills_data = requests.get(skills_url).json()

        for skill, _data in skills_data['Traits'].items():
            Ability.objects.update_or_create(
                internal_id=skill,
                defaults={
                    'name': LocalizationString.objects.get_or_create(
                        internal_id=skill, type=LocalizationString.Type.ABILITY)[0],
                    'description': LocalizationString.objects.get_or_create(
                        internal_id=skill, type=LocalizationString.Type.ABILITY_DESCRIPTION)[0],
                    'image': download_image_from_path(
                        'ability', skill, f'skill/{"Unknown" if skill == "None" else skill}.png'),
                }
            )

        print('Doing brands...')

        brand_url = f'https://leanny.github.io/splat3/data/parameter/' \
                    f'{latest_version}/misc/spl__BrandTraitsParam.spl__BrandTraitsParam.json'

        brand_data = requests.get(brand_url).json()

        for brand, data in brand_data['Traits'].items():
            Brand.objects.update_or_create(
                internal_id=brand,
                defaults={
                    'name': LocalizationString.objects.get_or_create(
                        internal_id=brand, type=LocalizationString.Type.BRAND)[0],
                    'favored_ability': Ability.objects.get(internal_id=data['UsualGearSkill']),
                    'unfavored_ability': Ability.objects.get(internal_id=data['UnusualGearSkill']),
                    'image': download_image_from_path('brand', brand, f'brand/{brand}.png'),
                }
            )

        print('Doing gear...')

        gear_urls = get_gear_urls(latest_version)

        for gear_type, url in gear_urls.items():
            data = requests.get(url).json()
            for gear in data:
                translation_string_id = gear['__RowId'][4:]
                localization_string = LocalizationString.objects.get(
                    internal_id=translation_string_id, type=get_localization_type_from_gear_type(gear_type))

                brand = Brand.objects.get(internal_id=gear['Brand'])

                Gear.objects.update_or_create(
                    internal_id=gear['Id'],
                    type=gear_type,
                    defaults={
                        'brand': brand,
                        'name': localization_string,
                        'rarity': gear['Rarity'],
                        'main_ability': Ability.objects.get(internal_id=gear['Skill']),
                        'image': download_image_from_path('gear', gear['Id'], f'gear/{gear["__RowId"]}.png'),
                    }
                )

        self.stdout.write('Finished updating gear')
