from typing import List

import requests
from django.core.management import BaseCommand

from splatnet_assets.management.commands._private import get_latest_version, download_image_from_path, download_image
from splatnet_assets.models import LocalizationString, Weapon, SubWeapon, SpecialWeapon


def get_urls(version: str):
    prefix = f'https://leanny.github.io/splat3/data/mush/{version}'
    return {
        'sub': f'{prefix}/WeaponInfoSub.json',
        'special': f'{prefix}/WeaponInfoSpecial.json',
        'main': f'{prefix}/WeaponInfoMain.json',
    }


class Command(BaseCommand):
    def handle(self, *args, **options):
        latest_version = get_latest_version()

        weapon_urls = get_urls(latest_version)

        for weapon_type, url in weapon_urls.items():
            weapon_data: List = requests.get(url).json()

            for weapon in weapon_data:
                if weapon['Type'] != 'Versus':
                    continue

                if weapon_type == 'main':
                    Weapon.objects.update_or_create(
                        internal_id=weapon['__RowId'],
                        defaults={
                            'splatnet_id': weapon['Id'],
                            'name': LocalizationString.objects.get_or_create(
                                internal_id=weapon['__RowId'], type=LocalizationString.Type.WEAPON_NAME)[0],
                            'flat_image': download_image_from_path('weapon', weapon['Id'],
                                                                   f'weapon_flat/Path_Wst_{weapon["__RowId"]}.png'),
                            'image_3d': download_image_from_path('weapon_3d', weapon['Id'],
                                                                 f'weapon/Wst_{weapon["__RowId"]}.png'),
                            'sub': SubWeapon.objects.get(internal_id=weapon['SubWeapon'].split('.')[0][10:]),
                            'special': SpecialWeapon.objects.get(
                                internal_id=weapon['SpecialWeapon'].split('.')[0][10:]),
                        }
                    )
                elif weapon_type == 'sub':
                    SubWeapon.objects.update_or_create(
                        internal_id=weapon['__RowId'],
                        defaults={
                            'splatnet_id': weapon['Id'],
                            'name': LocalizationString.objects.get_or_create(
                                internal_id=weapon['__RowId'], type=LocalizationString.Type.SUB_WEAPON_NAME)[0],
                            'image': download_image_from_path('sub', weapon['Id'], f'subspe/Wsb_{weapon["__RowId"]}00'
                                                                                   f'.png'),
                        }
                    )
                elif weapon_type == 'special':
                    SpecialWeapon.objects.update_or_create(
                        internal_id=weapon['__RowId'],
                        defaults={
                            'splatnet_id': weapon['Id'],
                            'name': LocalizationString.objects.get_or_create(
                                internal_id=weapon['__RowId'], type=LocalizationString.Type.SPECIAL_WEAPON_NAME)[0],
                            'image': download_image_from_path('special', weapon['Id'], f'subspe/Wsp_{weapon["__RowId"]}'
                                                                                       f'00.png'),
                            'mask_image': download_image('special_mask', weapon['Id'], f'https://uploads.catgirlin'
                                                                                       f'.space/specialsmasks/Wsp_'
                                                                                       f'{weapon["__RowId"]}00.png'),
                            'overlay_image': download_image('special_mask', weapon['Id'], f'https://uploads.catgirlin'
                                                                                          f'.space/specialsmasks/Wsp_'
                                                                                          f'{weapon["__RowId"]}01.png'),
                        }
                    )

        print('Done!')
