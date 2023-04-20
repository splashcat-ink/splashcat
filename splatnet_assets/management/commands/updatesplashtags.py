from typing import List

import requests
from django.core.management import BaseCommand

from splatnet_assets.fields import Color
from splatnet_assets.management.commands._private import download_image_from_path, get_latest_version
from splatnet_assets.models import LocalizationString, NameplateBackground, NameplateBadge


def get_urls(version: str):
    prefix = f'https://leanny.github.io/splat3/data/mush/{version}'
    return {
        'badges': f'{prefix}/BadgeInfo.json',
        'backgrounds': f'{prefix}/NamePlateBgInfo.json',
    }


class Command(BaseCommand):
    def handle(self, *args, **options):
        latest_version = get_latest_version()

        urls = get_urls(latest_version)

        for url in urls.values():
            data: List = requests.get(url).json()

            for item in data:
                if url == urls['badges']:
                    NameplateBadge.objects.update_or_create(
                        internal_id=item['Name'],
                        defaults={
                            'splatnet_id': item['Id'],
                            'description': LocalizationString.objects.get_or_create(
                                internal_id=item['__RowId'], type=LocalizationString.Type.BADGE_DESCRIPTION)[0],
                            'image': download_image_from_path('badge', item['Id'], f'badge/Badge_{item["Name"]}.png'),
                        }
                    )
                elif url == urls['backgrounds']:
                    NameplateBackground.objects.update_or_create(
                        internal_id=item['__RowId'],
                        defaults={
                            'splatnet_id': item['Id'],
                            'text_color': Color.from_floating_point_dict(item['TextColor']),
                            'image': download_image_from_path('nameplate_background', item['Id'],
                                                              f'npl/{item["__RowId"]}.png'),
                        }
                    )
