import base64
import datetime

import requests
from django.core.management import BaseCommand

from splatnet_assets.fields import Color
from splatnet_assets.models import Splatfest


class Command(BaseCommand):
    help = 'Updates Splatfests from splatoon3.ink'

    def handle(self, *args, **options):
        data = requests.get('https://splatoon3.ink/data/festivals.json').json()
        for splatfest in data['US']['data']['festRecords']['nodes']:
            splatfest_id = splatfest['__splatoon3ink_id']

            Splatfest.objects.update_or_create(internal_id=splatfest_id, defaults={
                'start_date': datetime.datetime.fromisoformat(splatfest['startTime']),
                'end_date': datetime.datetime.fromisoformat(splatfest['endTime']),
                'team_1_color': Color.from_floating_point_dict(splatfest['teams'][0]['color']),
                'team_2_color': Color.from_floating_point_dict(splatfest['teams'][1]['color']),
                'team_3_color': Color.from_floating_point_dict(splatfest['teams'][2]['color']),
            })
