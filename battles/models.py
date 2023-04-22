from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from splatnet_assets.fields import ColorField


# Create your models here.


class Judgement(models.TextChoices):
    WIN = 'WIN', _('Win')
    LOSE = 'LOSE', _('Lose')
    DRAW = 'DRAW', _('Draw')


class KnockoutJudgement(models.TextChoices):
    NEITHER = 'NEITHER', _('Neither')
    WIN = 'WIN', _('Win')
    LOSE = 'LOSE', _('Lose')


class Battle(models.Model):
    class VsMode(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular Battle')
        LEAGUE = 'LEAGUE', _('League Battle')
        FEST = 'FEST', _('Splatfest Battle')
        BANKARA = 'BANKARA', _('Anarchy Battle')
        X_MATCH = 'X_MATCH', _('X Battle')

    class VsRule(models.TextChoices):
        TURF_WAR = 'TURF_WAR', _('Turf War')
        AREA = 'AREA', _('Splat Zones')
        LOFT = 'LOFT', _('Tower Control')
        CLAM = 'CLAM', _('Clam Blitz')
        GOAL = 'GOAL', _('Rainmaker')

    class BattleJudgement(models.TextChoices):
        WIN = 'WIN', _('Win')
        LOSE = 'LOSE', _('Lose')
        DRAW = 'DRAW', _('Draw')
        EXEMPTED_LOSE = 'EXEMPTED_LOSE', _('Lose (Exempted)')
        DEEMED_LOSE = 'DEEMED_LOSE', _('Deemed Lose')

    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='battles')
    splatnet_id = models.CharField(max_length=32)
    raw_data = models.JSONField()
    data_type = models.CharField(max_length=32)  # e.g. "splatnet3"
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vs_mode = models.CharField(max_length=32, choices=VsMode.choices)
    vs_rule = models.CharField(max_length=32, choices=VsRule.choices)
    vs_stage = models.ForeignKey('splatnet_assets.Stage', on_delete=models.PROTECT, null=True)
    played_time = models.DateTimeField()
    duration = models.IntegerField()
    judgement = models.CharField(max_length=32, choices=BattleJudgement.choices)

    player_title_adjective = models.ForeignKey('splatnet_assets.TitleAdjective', on_delete=models.PROTECT)
    player_title_subject = models.ForeignKey('splatnet_assets.TitleSubject', on_delete=models.PROTECT)
    player_head_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    player_clothing_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    player_shoes_gear = models.OneToOneField('PlayerGear', on_delete=models.PROTECT, related_name='+')
    player_npln_id = models.CharField(max_length=50)
    player_name = models.CharField(max_length=50)
    player_name_id = models.CharField(max_length=10)
    player_nameplate_background = models.ForeignKey('splatnet_assets.NameplateBackground', on_delete=models.PROTECT)
    player_nameplate_badge_1 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                                 related_name='+')
    player_nameplate_badge_2 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                                 related_name='+')
    player_nameplate_badge_3 = models.ForeignKey('splatnet_assets.NameplateBadge', on_delete=models.PROTECT, null=True,
                                                 related_name='+')
    player_paint = models.IntegerField(validators=[MinValueValidator(0)], null=True)
    knockout = models.CharField(max_length=32, choices=KnockoutJudgement.choices, blank=True, null=True)

    # teams comes from related_name='teams' on Team.battle

    awards = models.ManyToManyField('splatnet_assets.Award', related_name='battles', through='BattleAward')

    def __str__(self):
        return f'Battle {self.id} ({self.splatnet_id}) - @{self.uploader.username}'

    def get_absolute_url(self):
        return reverse('battle_detail', args=[str(self.id)])

    @property
    def splashtag(self):
        return {
            'name': self.player_name,
            'name_id': self.player_name_id,
            'title_adjective': self.player_title_adjective,
            'title_subject': self.player_title_subject,
            'badges': [self.player_nameplate_badge_1, self.player_nameplate_badge_2, self.player_nameplate_badge_3],
            'background': self.player_nameplate_background,
        }


class BattleAward(models.Model):
    battle = models.ForeignKey('Battle', on_delete=models.CASCADE)
    award = models.ForeignKey('splatnet_assets.Award', on_delete=models.PROTECT)
    order = models.IntegerField()


class Team(models.Model):
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


class Player(models.Model):
    class Species(models.TextChoices):
        INKLING = 'INKLING', _('Inkling')
        OCTOLING = 'OCTOLING', _('Octoling')

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
