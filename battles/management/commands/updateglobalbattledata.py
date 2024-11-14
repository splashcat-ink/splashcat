from django.core.management import BaseCommand

from battles.tasks import update_global_battle_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_global_battle_data()
