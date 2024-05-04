from django.db import models
from django.dispatch import receiver

from battles.models import Battle, BattleGroup
from groups.models import Group
from indexnow.api import send_indexnow_request
from users.models import User


@receiver(models.signals.post_save, dispatch_uid='indexnow_model_save')
def send_indexnow_on_model_save(sender, instance, **kwargs):
    if sender in [User, Battle, BattleGroup, Group]:
        path = instance.get_absolute_url()
        send_indexnow_request(path)


@receiver(models.signals.post_delete, dispatch_uid='indexnow_model_save')
def send_indexnow_on_model_delete(sender, instance, **kwargs):
    if sender in [User, Battle, BattleGroup, Group]:
        path = instance.get_absolute_url()
        send_indexnow_request(path)
