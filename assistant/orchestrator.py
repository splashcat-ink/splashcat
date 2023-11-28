import requests
from django.conf import settings

from assistant.models import Thread

fly_api_hostname = settings.FLY_API_HOSTNAME
fly_api_token = settings.FLY_API_TOKEN
fly_primary_region = settings.FLY_PRIMARY_REGION


def schedule_machine(thread: Thread):
    thread_id = thread.id
    response = requests.post(
        f'{fly_api_hostname}/v1/apps/splashcat/machines',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {fly_api_token}',
        },
        json={
            'region': fly_primary_region,
            'config': {
                # 'auto_destroy': True,
                'guest': {
                    'cpu_kind': 'performance',
                    'cpus': 1,
                    'memory_mb': 1024 * 2,
                },
                'init': {
                    'cmd': ['python assistant/runner.py'],
                    'swap_size_mb': 1024 * 4,
                },
                'image': 'splashcat:latest',
            }
        }
    )
    response.raise_for_status()
