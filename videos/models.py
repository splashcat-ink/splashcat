import datetime

from django.db import models

from battles.models import Battle
from videos.bunny import set_video_thumbnail


# Create your models here.

class Video(models.Model):
    bunny_video_id = models.CharField(max_length=255)
    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class BattleVideo(Video):
    battle = models.OneToOneField('battles.Battle', on_delete=models.CASCADE, blank=True, null=True)
    battle_start_time = models.DateTimeField()

    def find_related_battle(self):
        # find a battle with a played time within 1 minute of the video's start time uploaded by the same user
        # if there are multiple, pick the one with the closest played time
        # if there are none, return None
        return self.uploader.battles.filter(played_time__gte=self.battle_start_time - datetime.timedelta(minutes=1),
                                            played_time__lte=self.battle_start_time + datetime.timedelta(minutes=1),
                                            battlevideo__isnull=True).order_by('played_time').first()

    def update_video_thumbnail(self):
        if not self.battle:
            return
        thumbnail_url = f"https://cdn.splashcat.ink/image-render/battle/{self.battle_id}/render"
        set_video_thumbnail(self.bunny_video_id, thumbnail_url)
