import requests
from django.core.management import BaseCommand

from splatnet_assets.management.commands._private import download_image_from_path
from splatnet_assets.models import Stage, LocalizationString


class Command(BaseCommand):
    def handle(self, *args, **options):
        stage_data = requests.get('https://leanny.github.io/splat3/data/mush/310/VersusSceneInfo.json').json()
        for stage in stage_data:
            if stage['__RowId'][:3] == 'Vss':
                # remove any numbers from the rowid
                image_id = ''.join([c for c in stage['__RowId'] if not c.isdigit()])

                Stage.objects.update_or_create(
                    internal_id=stage['__RowId'],
                    defaults={
                        'splatnet_id': stage['Id'],
                        'name': LocalizationString.objects.get_or_create(
                            type=LocalizationString.Type.STAGE,
                            internal_id=''.join([c for c in stage['__RowId'][4:] if not c.isdigit()]),
                        )[0],
                        'image': download_image_from_path(
                            'stage',
                            image_id,
                            f'stageL/{image_id}.png',
                        ),
                        'image_banner': download_image_from_path(
                            'stage_banner',
                            image_id,
                            f'stageBanner/{image_id}.png',
                        ),
                    }
                )
