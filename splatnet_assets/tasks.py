from celery import shared_task
from django.core import management

from splatnet_assets.management.commands.updatechallenges import Command as UpdateChallengesCommand


@shared_task
def update_challenges():
    management.call_command(UpdateChallengesCommand())
