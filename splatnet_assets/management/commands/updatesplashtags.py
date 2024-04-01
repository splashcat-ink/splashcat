from typing import List

import requests
from django.core.management import BaseCommand

from splatnet_assets.fields import Color
from splatnet_assets.management.commands._private import download_image_from_path, get_latest_version
from splatnet_assets.models import LocalizationString, NameplateBackground, NameplateBadge
from splatnet_assets.badge_descriptions import level_regex, bad_badge_prefixes, salmon_run_badge_prefixes, has_prefix

badge_prefixes = bad_badge_prefixes + salmon_run_badge_prefixes


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
                    localization_id: str = item['Name']
                    if has_prefix(localization_id, badge_prefixes):
                        badge_prefix = None
                        for prefix in badge_prefixes:
                            if prefix in item['Name']:
                                badge_prefix = prefix
                                break
                        level: str = level_regex.search(item['Name']).group()
                        localization_id = f'{badge_prefix}{level.lstrip("_")}'

                    NameplateBadge.objects.update_or_create(
                        internal_id=item['Name'],
                        defaults={
                            'splatnet_id': item['Id'],
                            'description': LocalizationString.objects.get_or_create(
                                internal_id=localization_id, type=LocalizationString.Type.BADGE_DESCRIPTION)[0],
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
