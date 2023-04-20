from django.core.management import BaseCommand

from splatnet_assets.models import LocalizationString, Award

gold = [
    "Battle",
    "GachiareaPaint",
    "GachiareaFrontHold",
    "GachiyaguraInvasion",
    "GachiyaguraBest",
    "GachihokoInvasion",
    "GachihokoBest",
    "GachiasariInvasion",
    "GachiasariHold",
    "Paint",
    "Standout",
    "NawabariPaintMyTeamArea",
    "NawabariPaintOpTeamArea",
    "SuperJumpTarget",
    "Kill",
    "KillAssist",
]
silver = [
    "GachiareaStay",
    "GachiyaguraCheckPointPass",
    "GachiyaguraStop",
    "GachihokoCheckPointPass",
    "GachihokoHold",
    "GachihokoStop",
    "GachiasariStop",
    "NawabariDefenseMyTeamArea",
    "MoveDistance",
    "DamageRecovery",
    "InkConsumption",
    "FirstSplat",
    "UltraShot",
    "GreatBarrier",
    "MicroLaser",
    "MultiMissile",
    "InkStorm",
    "NiceBall",
    "UltraStamp",
    "Jetpack",
    "SuperHook",
    "ShockSonar",
    "Blower",
    "Chariot",
    "Skewer",
    "TripleTornado",
    "EnergyStand",
    "Battle2",
    "GachiareaPaint2",
    "GachiareaFrontHold2",
    "GachiyaguraInvasion2",
    "GachihokoInvasion2",
    "GachiasariInvasion2",
    "GachiasariHold2",
    "Paint2",
    "Standout2",
    "NawabariPaintMyTeamArea2",
    "NawabariPaintOpTeamArea2",
    "SuperJumpTarget2",
    "Kill2",
    "KillAssist2",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for award in gold:
            Award.objects.update_or_create(
                internal_id=award,
                defaults={
                    'name': LocalizationString.objects.get_or_create(
                        internal_id=award, type=LocalizationString.Type.AWARD)[0],
                    'gold': True,
                }
            )
        for award in silver:
            Award.objects.update_or_create(
                internal_id=award,
                defaults={
                    'name': LocalizationString.objects.get_or_create(
                        internal_id=award, type=LocalizationString.Type.AWARD)[0],
                    'gold': False,
                }
            )
