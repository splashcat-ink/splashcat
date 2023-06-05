import requests
from django.core.management import BaseCommand

from splatnet_assets.management.commands._private import download_image_from_path, download_image, get_latest_version
from splatnet_assets.models import Stage, LocalizationString


class Command(BaseCommand):
    def handle(self, *args, **options):
        version = get_latest_version()
        stage_data = requests.get(f'https://leanny.github.io/splat3/data/mush/{version}/VersusSceneInfo.json').json()
        splatoon_3_ink_data = requests.get('https://splatoon3.ink/data/stages.json').json()
        splatoon_3_ink_data = splatoon_3_ink_data['data']['stageRecords']['nodes']
        splatoon_3_ink_data = {stage['stageId']: stage for stage in splatoon_3_ink_data}

        for stage in stage_data:
            if stage['__RowId'][:3] == 'Vss':
                data = splatoon_3_ink_data[stage['Id']]
                image_id = ''.join([c for c in stage['__RowId'] if not c.isdigit()])

                Stage.objects.update_or_create(
                    internal_id=stage['__RowId'],
                    defaults={
                        'splatnet_id': stage['Id'],
                        'name': LocalizationString.objects.get_or_create(
                            type=LocalizationString.Type.STAGE,
                            internal_id=''.join([c for c in stage['__RowId'][4:] if not c.isdigit()]),
                        )[0],
                        'image': download_image(
                            'stage',
                            image_id,
                            data['originalImage']['url'],
                        ),
                        'image_banner': download_image_from_path(
                            'stage_banner',
                            image_id,
                            f'stageBanner/{image_id}.png',
                        ),
                    }
                )
