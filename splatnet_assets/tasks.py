from celery import shared_task
from django.core import management

from splatnet_assets.management.commands.updatesplatfests import Command as UpdateSplatfestsCommand
from splatnet_assets.management.commands.updatechallenges import Command as UpdateChallengesCommand


@shared_task
def update_challenges():
    management.call_command(UpdateChallengesCommand())


@shared_task
def update_splatfests():
    management.call_command(UpdateSplatfestsCommand())
