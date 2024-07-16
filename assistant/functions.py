from django.db import transaction

from battles.models import Battle, BattleGroup
from users.models import User


def create_battle_group(user: User, params: dict) -> int:
    battles = params.get('battles', [])
    with transaction.atomic():
        battles = Battle.objects.filter(pk__in=battles, uploader=user)
        group = BattleGroup(creator=user)
        group.save()

        group.battles.add(*battles)

        group.save()

        return group.id
