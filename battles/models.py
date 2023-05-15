from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from splatnet_assets.fields import ColorField


# Create your models here.


class Judgement(models.TextChoices):
    WIN = 'WIN', _('Victory')
    LOSE = 'LOSE', _('Defeat')
    DRAW = 'DRAW', _('Draw')


class KnockoutJudgement(models.TextChoices):
    NEITHER = 'NEITHER', _('Neither')
    WIN = 'WIN', _('Victory')
    LOSE = 'LOSE', _('Defeat')


class BattleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().defer("raw_data")

    def with_prefetch(self):
        return self.select_related('uploader', 'vs_stage__name',
                                   'vs_stage__image', ) \
            .prefetch_related(
            'awards',
            'teams__players__head_gear__gear__name', 'teams__players__head_gear__gear__brand',
            'teams__players__head_gear__gear__image',
            'teams__players__clothing_gear__gear__name', 'teams__players__clothing_gear__gear__brand',
            'teams__players__clothing_gear__gear__image',
            'teams__players__shoes_gear__gear__name', 'teams__players__shoes_gear__gear__brand',
            'teams__players__shoes_gear__gear__image',
            'teams__players__weapon__name', 'teams__players__weapon__flat_image',
            'teams__players__weapon__sub__name', 'teams__players__weapon__sub__image',
            'teams__players__weapon__special__name',
            'teams__players__weapon__special__mask_image',
            'teams__players__weapon__special__overlay_image',
            'teams__players__nameplate_background',
            'teams__players__title_adjective__string', 'teams__players__title_subject__string',
        )


class Battle(models.Model):
    class VsMode(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular Battle')
        LEAGUE = 'LEAGUE', _('League Battle')
        FEST = 'FEST', _('Splatfest Battle')
        BANKARA = 'BANKARA', _('Anarchy Battle')
        X_MATCH = 'X_MATCH', _('X Battle')
        PRIVATE = 'PRIVATE', _('Private Battle')

    class VsRule(models.TextChoices):
        TURF_WAR = 'TURF_WAR', _('Turf War')
        AREA = 'AREA', _('Splat Zones')
        LOFT = 'LOFT', _('Tower Control')
        CLAM = 'CLAM', _('Clam Blitz')
        GOAL = 'GOAL', _('Rainmaker')

    class BattleJudgement(models.TextChoices):
        WIN = 'WIN', _('Victory')
        LOSE = 'LOSE', _('Defeat')
        DRAW = 'DRAW', _('Draw')
        EXEMPTED_LOSE = 'EXEMPTED_LOSE', _('Defeat (Exempted)')
        DEEMED_LOSE = 'DEEMED_LOSE', _('Deemed Lose')

    objects = BattleManager()

    class Meta:
        indexes = [
            models.Index(fields=["uploader", "-played_time"]),
            models.Index(fields=["uploader", "judgement"]),
        ]

    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='battles')
    splatnet_id = models.CharField(max_length=100)
    raw_data = models.JSONField()
    data_type = models.CharField(max_length=32)  # e.g. "splatnet3"
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vs_mode = models.CharField(max_length=32, choices=VsMode.choices)
    vs_rule = models.CharField(max_length=32, choices=VsRule.choices)
    vs_stage = models.ForeignKey('splatnet_assets.Stage', on_delete=models.PROTECT, null=True)
    played_time = models.DateTimeField()
    duration = models.DurationField()
    judgement = models.CharField(max_length=32, choices=BattleJudgement.choices, db_index=True)
    knockout = models.CharField(max_length=32, choices=KnockoutJudgement.choices, blank=True, null=True)

    # teams comes from related_name='teams' on Team.battle

    awards = models.ManyToManyField('splatnet_assets.Award', related_name='battles', through='BattleAward')

    def __str__(self):
        return f'Battle {self.id} ({self.splatnet_id}) - @{self.uploader.username}'

    def get_absolute_url(self):
        return reverse('battles:view_battle', args=[str(self.id)])

    @property
    def splashtag(self):
        player = self.player
        return {
            'name': player.name,
            'name_id': player.name_id,
            'title_adjective': player.title_adjective,
            'title_subject': player.title_subject,
            'badges': [player.nameplate_badge_1, player.nameplate_badge_2, player.nameplate_badge_3],
            'background': player.nameplate_background,
        }

    @property
    def player(self):
        return self.teams.get(is_my_team=True).players \
            .select_related('title_adjective__string') \
            .select_related('title_subject__string') \
            .select_related('nameplate_background__image') \
            .select_related('nameplate_badge_1__image') \
            .select_related('nameplate_badge_2__image') \
            .select_related('nameplate_badge_3__image') \
            .select_related('weapon__name') \
            .select_related('weapon__flat_image') \
            .select_related('weapon__sub__name') \
            .select_related('weapon__sub__image') \
            .select_related('weapon__special__name') \
            .select_related('weapon__special__image') \
            .get(is_self=True)


class BattleAward(models.Model):
    battle = models.ForeignKey('Battle', on_delete=models.CASCADE)
    award = models.ForeignKey('splatnet_assets.Award', on_delete=models.PROTECT)
    order = models.IntegerField()


class TeamManager(models.Manager):
    def with_prefetch(self):
        return self.prefetch_related(Prefetch('players', queryset=Player.objects.with_prefetch()))


class Team(models.Model):
    objects = TeamManager()

    battle = models.ForeignKey('Battle', on_delete=models.CASCADE, related_name='teams')
    is_my_team = models.BooleanField()
    color = ColorField()
    fest_streak_win_count = models.IntegerField(blank=True, null=True)
    fest_team_name = models.CharField(max_length=50, blank=True, null=True)
    fest_uniform_bonus_rate = models.FloatField(blank=True, null=True)
    fest_uniform_name = models.CharField(max_length=50, blank=True, null=True)
    judgement = models.CharField(max_length=32, choices=Judgement.choices)
    order = models.IntegerField()
    # players comes from a many-to-one relationship from the Player class
    noroshi = models.IntegerField(blank=True, null=True)
    paint_ratio = models.FloatField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    class TricolorRole(models.TextChoices):
        ATTACK1 = 'ATTACK1', _('Attack 1')
        ATTACK2 = 'ATTACK2', _('Attack 2')
        DEFENSE = 'DEFENSE', _('Defense')

    tricolor_role = models.CharField(max_length=32, choices=TricolorRole.choices, blank=True, null=True)

    @property
    def next_team(self):
        # get the next team, looping back to the beginning if necessary. used by the template to display colors
        return self.battle.teams.get(order=(self.order % self.battle.teams.count()) + 1)


class PlayerManager(models.Manager):
    def with_prefetch(self):
        return self.prefetch_related(
            'title_adjective__string', 'title_subject__string',
            'nameplate_background__image',
            'nameplate_badge_1__image', 'nameplate_badge_2__image', 'nameplate_badge_3__image',
            'weapon__name', 'weapon__flat_image', 'weapon__sub__name', 'weapon__sub__image',
            'weapon__special__name',
            'weapon__special__mask_image', 'weapon__special__overlay_image',
            'head_gear__gear__name', 'head_gear__gear__image',
            'clothing_gear__gear__name', 'clothing_gear__gear__image',
            'shoes_gear__gear__name', 'shoes_gear__gear__image',
        )


class Player(models.Model):
    class Species(models.TextChoices):
        INKLING = 'INKLING', _('Inkling')
        OCTOLING = 'OCTOLING', _('Octoling')

    objects = PlayerManager()

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='players')
    is_self = models.BooleanField()
    npln_id = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    name_id = models.CharField(max_length=10)
    species = models.CharField(max_length=32, choices=Species.choices)
    title_adjective = models.ForeignKey('splatnet_assets.TitleAdjective', on_delete=models.PROTECT)
    title_subject = models.ForeignKey('splatnet_assets.TitleSubject', on_delete=models.PROTECT)
    nameplate_background = models.ForeignKey('splatnet_assets.NameplateBackground', on_delete=models.PROTECT)
    nameplate_badge_1 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                          related_name='+')
    nameplate_badge_2 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                          related_name='+')
    nameplate_badge_3 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                          related_name='+')
    weapon = models.ForeignKey('splatnet_assets.Weapon', on_delete=models.PROTECT, related_name='+')
    head_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    clothing_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    shoes_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    disconnect = models.BooleanField()
    kills = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    deaths = models.IntegerField(blank=True, null=True)
    specials = models.IntegerField(blank=True, null=True)
    paint = models.IntegerField(blank=True, null=True)
    noroshi_try = models.IntegerField(blank=True, null=True)
    order = models.IntegerField()

    @property
    def byname(self):
        return self.title_adjective.string.string + ' ' + self.title_subject.string.string

    @property
    def splashtag(self):
        return {
            'name': self.name,
            'name_id': self.name_id,
            'title_adjective': self.title_adjective,
            'title_subject': self.title_subject,
            'badges': [self.nameplate_badge_1, self.nameplate_badge_2, self.nameplate_badge_3],
            'background': self.nameplate_background,
        }


class PlayerGear(models.Model):
    gear = models.ForeignKey('splatnet_assets.Gear', on_delete=models.PROTECT)
    primary_ability = models.ForeignKey('splatnet_assets.Ability', on_delete=models.PROTECT, related_name='+')
    secondary_ability_1 = models.ForeignKey('splatnet_assets.Ability', on_delete=models.PROTECT, related_name='+',
                                            null=True)
    secondary_ability_2 = models.ForeignKey('splatnet_assets.Ability', on_delete=models.PROTECT, related_name='+',
                                            null=True)
    secondary_ability_3 = models.ForeignKey('splatnet_assets.Ability', on_delete=models.PROTECT, related_name='+',
                                            null=True)

    @property
    def secondary_abilities(self):
        return [self.secondary_ability_1, self.secondary_ability_2, self.secondary_ability_3]
