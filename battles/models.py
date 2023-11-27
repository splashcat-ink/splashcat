from datetime import timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from splatnet_assets.common_model_choices import XBattleDivisions
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

    def with_prefetch(self, include_player_gear=False):
        player_prefetch_queryset = Player.objects \
            .select_related('title_adjective__string', 'title_subject__string', 'nameplate_background__image',
                            'nameplate_badge_1__image', 'nameplate_badge_2__image', 'nameplate_badge_3__image',
                            'nameplate_badge_1__description', 'nameplate_badge_2__description',
                            'nameplate_badge_3__description', 'weapon__name',
                            'weapon__flat_image', 'weapon__image_3d', 'weapon__sub__name',
                            'weapon__sub__overlay_image', 'weapon__sub__mask_image', 'weapon__special__name',
                            'weapon__special__overlay_image', 'weapon__special__mask_image')

        if include_player_gear:
            player_prefetch_queryset = player_prefetch_queryset \
                .prefetch_related('head_gear__gear__name', 'head_gear__gear__image', 'head_gear__gear__brand',
                                  'head_gear__primary_ability__name',
                                  'head_gear__primary_ability__image',
                                  'head_gear__secondary_ability_1__name',
                                  'head_gear__secondary_ability_1__image',
                                  'head_gear__secondary_ability_2__name',
                                  'head_gear__secondary_ability_2__image',
                                  'head_gear__secondary_ability_3__name',
                                  'head_gear__secondary_ability_3__image',

                                  'clothing_gear__gear__name', 'clothing_gear__gear__image',
                                  'clothing_gear__gear__brand',
                                  'clothing_gear__primary_ability__name',
                                  'clothing_gear__primary_ability__image',
                                  'clothing_gear__secondary_ability_1__name',
                                  'clothing_gear__secondary_ability_1__image',
                                  'clothing_gear__secondary_ability_2__name',
                                  'clothing_gear__secondary_ability_2__image',
                                  'clothing_gear__secondary_ability_3__name',
                                  'clothing_gear__secondary_ability_3__image',

                                  'shoes_gear__gear__name', 'shoes_gear__gear__image', 'shoes_gear__gear__brand',
                                  'shoes_gear__primary_ability__name',
                                  'shoes_gear__primary_ability__image',
                                  'shoes_gear__secondary_ability_1__name',
                                  'shoes_gear__secondary_ability_1__image',
                                  'shoes_gear__secondary_ability_2__name',
                                  'shoes_gear__secondary_ability_2__image',
                                  'shoes_gear__secondary_ability_3__name',
                                  'shoes_gear__secondary_ability_3__image',
                                  )

        player_prefetch = Prefetch(
            'teams__players',
            queryset=player_prefetch_queryset,
        )

        return self.select_related('uploader__github_link', 'vs_stage__name', 'vs_stage__image') \
            .prefetch_related('awards__name', 'battlevideo').prefetch_related(player_prefetch)


class Battle(models.Model):
    class VsMode(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular Battle')
        CHALLENGE = 'CHALLENGE', _('Challenge')
        FEST = 'FEST', _('Splatfest Battle')
        BANKARA = 'BANKARA', _('Anarchy Battle')
        X_MATCH = 'X_MATCH', _('X Battle')
        PRIVATE = 'PRIVATE', _('Private Battle')

    class AnarchyMode(models.TextChoices):
        SERIES = 'SERIES', _('Anarchy Battle (Series)')
        OPEN = 'OPEN', _('Anarchy Battle (Open)')

    class SplatfestBattleType(models.TextChoices):
        OPEN = 'OPEN', _('Splatfest Battle (Open)')
        PRO = 'PRO', _('Splatfest Battle (Pro)')

    class SplatfestBattleCloutMultiplier(models.TextChoices):
        NONE = 'NONE', _('1x')
        DECUPLE = 'DECUPLE', _('10x')
        DRAGON = 'DRAGON', _('100x')
        DOUBLE_DRAGON = 'DOUBLE_DRAGON', _('333x')

    class VsRule(models.TextChoices):
        TURF_WAR = 'TURF_WAR', _('Turf War')
        TRI_COLOR = 'TRI_COLOR', _('Tricolor Turf War')
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
            models.Index(fields=["uploader", "-uploaded_at"]),
            models.Index(fields=["uploader", "judgement"]),
            models.Index(fields=["-uploaded_at"]),
            models.Index(fields=["-played_time"]),
            models.Index(fields=["splatnet_id", "id"]),
        ]

    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='battles')
    uploader_agent_name = models.CharField(max_length=32, blank=True, null=True)
    uploader_agent_version = models.CharField(max_length=50, blank=True, null=True)
    uploader_agent_extra = models.CharField(max_length=100, blank=True, null=True)
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
    anarchy_mode = models.CharField(max_length=32, choices=AnarchyMode.choices, blank=True, null=True)
    anarchy_point_change = models.IntegerField(blank=True, null=True)
    anarchy_rank = models.CharField(max_length=2, blank=True, null=True)
    anarchy_s_plus_number = models.IntegerField(blank=True, null=True,
                                                validators=[MinValueValidator(0), MaxValueValidator(50)])
    anarchy_points = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    x_battle_rank = models.IntegerField(blank=True, null=True)
    x_battle_division = models.CharField(max_length=32, blank=True, null=True, choices=XBattleDivisions.choices)
    splatfest_mode = models.CharField(max_length=32, choices=SplatfestBattleType.choices, blank=True, null=True)
    splatfest_clout_multiplier = models.CharField(max_length=32, choices=SplatfestBattleCloutMultiplier.choices,
                                                  blank=True, null=True)
    splatfest_clout_contribution = models.FloatField(blank=True, null=True)
    splatfest_festival_shells = models.IntegerField(blank=True, null=True)
    power = models.FloatField(blank=True, null=True)

    challenge = models.ForeignKey('splatnet_assets.Challenge', on_delete=models.PROTECT, blank=True, null=True)

    gpt_description = models.TextField(blank=True)
    gpt_description_generated = models.BooleanField(default=False)
    gpt_description_generated_at = models.DateTimeField(blank=True, null=True)

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
        for team in self.teams.all():
            for player in team.players.all():
                if player.is_self:
                    return player

    def to_dict(self):
        data = {
            'battle_id': self.id,
            'uploader_id': self.uploader_id,
            'data_type': self.data_type,
            'raw_data': self.raw_data,
            'vs_mode': self.vs_mode,
            'vs_rule': self.vs_rule,
            'stage_id': self.vs_stage_id,
            'uploaded_at': self.uploaded_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'played_time': self.played_time.isoformat(),
            'duration': self.duration.total_seconds(),
            'judgement': self.judgement,
            'knockout': self.knockout,
            'awards': [],
            'teams': [],
        }

        for award in self.awards.all():
            data['awards'].append({
                'id': award.id,
                'name': award.name.string,
            })

        for team in self.teams.all():
            data['teams'].append(team.to_dict())

        return data

    def to_gpt_dict(self):
        data = {
            'battle_id': self.id,
            'uploader_id': self.uploader_id,
            'vs_mode': self.vs_mode,
            'vs_rule': self.vs_rule,
            'stage_name': self.vs_stage.name.string,
            'uploaded_at': self.uploaded_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'played_time': self.played_time.isoformat(),
            'duration': self.duration.total_seconds(),
            'judgement': self.judgement,
            'knockout': self.knockout,
            'awards': [],
            'teams': [],
        }

        for award in self.awards.all():
            data['awards'].append({
                'name': award.name.string,
            })

        for team in self.teams.all():
            data['teams'].append(team.to_gpt_dict())

        return data

    def get_vs_rule_image_name(self):
        vs_rule_to_image_name = {
            self.VsRule.TURF_WAR: 'regular',
            self.VsRule.TRI_COLOR: 'regular',
            self.VsRule.AREA: 'area',
            self.VsRule.LOFT: 'yagura',
            self.VsRule.GOAL: 'hoko',
            self.VsRule.CLAM: 'asari',
        }

        return vs_rule_to_image_name[self.vs_rule]

    def get_short_judgement_display(self):
        if self.judgement == self.BattleJudgement.WIN:
            return _('Victory')
        elif self.judgement == self.BattleJudgement.DRAW:
            return _('Draw')
        else:
            return _('Defeat')

    def get_related_battles(self):
        return Battle.objects.filter(splatnet_id=self.splatnet_id).exclude(id=self.id)

    def get_player_next_battle(self):
        try:
            return self.get_next_by_played_time(uploader_id=self.uploader_id)
        except Battle.DoesNotExist:
            return None

    def get_player_previous_battle(self):
        try:
            return self.get_previous_by_played_time(uploader_id=self.uploader_id)
        except Battle.DoesNotExist:
            return None

    def find_related_battle_video(self):
        return self.uploader.battlevideo_set.filter(
            battle_start_time__gte=self.played_time - timedelta(minutes=1),
            battle_start_time__lte=self.played_time + timedelta(minutes=1),
            battle__isnull=True,
        ).first()


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
    fest_uniform_name = models.CharField(max_length=100, blank=True, null=True)
    judgement = models.CharField(max_length=32, choices=Judgement.choices, blank=True, null=True)
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

    def to_dict(self):
        data = {
            'is_my_team': self.is_my_team,
            'color': self.color.to_hex(),
            'fest_streak_win_count': self.fest_streak_win_count,
            'fest_team_name': self.fest_team_name,
            'fest_uniform_bonus_rate': self.fest_uniform_bonus_rate,
            'fest_uniform_name': self.fest_uniform_name,
            'tricolor_role': self.tricolor_role,
            'judgement': self.judgement,
            'score': self.score,
            'paint_ratio': self.paint_ratio,
            'noroshi': self.noroshi,
            'order': self.order,
            'players': [],
        }

        for player in self.players.all():
            data['players'].append(player.to_dict())

        return data

    def to_gpt_dict(self):
        data = {
            'is_my_team': self.is_my_team,
            'color': self.color.to_hex(),
            'fest_streak_win_count': self.fest_streak_win_count,
            'fest_team_name': self.fest_team_name,
            'fest_uniform_bonus_rate': self.fest_uniform_bonus_rate,
            'fest_uniform_name': self.fest_uniform_name,
            'tricolor_role': self.tricolor_role,
            'judgement': self.judgement,
            'score': self.score,
            'paint_ratio': self.paint_ratio,
            'ultra_signals': self.noroshi,
            'order': self.order,
            'players': [],
        }

        for player in self.players.all():
            data['players'].append(player.to_gpt_dict())

        return data


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
    name_id = models.CharField(max_length=10, blank=True, null=True)
    species = models.CharField(max_length=32, choices=Species.choices)
    title_adjective = models.ForeignKey('splatnet_assets.TitleAdjective', on_delete=models.PROTECT, null=True)
    title_subject = models.ForeignKey('splatnet_assets.TitleSubject', on_delete=models.PROTECT, null=True)
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
        if self.title_adjective is None or self.title_subject is None:
            return ''
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

    def to_dict(self):
        data = {
            'is_self': self.is_self,
            'species': self.species,
            'npln_id': self.npln_id,
            'name': self.name,
            'name_id': self.name_id,
            'title': self.byname,
            'title_adjective_id': self.title_adjective.internal_id if self.title_adjective else None,
            'title_subject_id': self.title_subject.internal_id if self.title_subject else None,
            'nameplate_background_id': self.nameplate_background.internal_id,
            'nameplate_badge_ids': [
                self.nameplate_badge_1.internal_id if self.nameplate_badge_1 else None,
                self.nameplate_badge_2.internal_id if self.nameplate_badge_2 else None,
                self.nameplate_badge_3.internal_id if self.nameplate_badge_3 else None,
            ],
            'weapon_id': self.weapon.internal_id,
            'head_gear': self.head_gear.to_dict(),
            'clothing_gear': self.clothing_gear.to_dict(),
            'shoes_gear': self.shoes_gear.to_dict(),
            'disconnect': self.disconnect,
            'kills': self.kills,
            'assists': self.assists,
            'deaths': self.deaths,
            'specials': self.specials,
            'paint': self.paint,
            'noroshi_try': self.noroshi_try,
            'order': self.order,
        }

        return data

    def to_gpt_dict(self):
        data = {
            'is_self': self.is_self,
            'species': self.species,
            'npln_id': self.npln_id,
            'name': self.name,
            'name_id': self.name_id,
            'title': self.byname,
            'nameplate_background_id': self.nameplate_background.internal_id,
            'nameplate_badge_ids': [
                self.nameplate_badge_1.internal_id if self.nameplate_badge_1 else None,
                self.nameplate_badge_2.internal_id if self.nameplate_badge_2 else None,
                self.nameplate_badge_3.internal_id if self.nameplate_badge_3 else None,
            ],
            'nameplate_badge_descriptions': [
                self.nameplate_badge_1.description.string if self.nameplate_badge_1 else None,
                self.nameplate_badge_2.description.string if self.nameplate_badge_2 else None,
                self.nameplate_badge_3.description.string if self.nameplate_badge_3 else None,
            ],
            'weapon_name': self.weapon.name.string,
            'sub_weapon_name': self.weapon.sub.name.string,
            'special_weapon_name': self.weapon.special.name.string,
            'head_gear': self.head_gear.to_gpt_dict(),
            'clothing_gear': self.clothing_gear.to_gpt_dict(),
            'shoes_gear': self.shoes_gear.to_gpt_dict(),
            'disconnect': self.disconnect,
            'kills': self.kills,
            'assists': self.assists,
            'deaths': self.deaths,
            'specials': self.specials,
            'paint': self.paint,
            'ultra_signal_attempts': self.noroshi_try,
            'order': self.order,
        }

        return data


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

    def to_dict(self):
        return {
            'gear_id': self.gear.internal_id,
            'primary_ability_id': self.primary_ability.internal_id,
            'secondary_ability_ids': [
                self.secondary_abilities[0].internal_id if self.secondary_abilities[0] else None,
                self.secondary_abilities[1].internal_id if self.secondary_abilities[1] else None,
                self.secondary_abilities[2].internal_id if self.secondary_abilities[2] else None,
            ],
        }

    def to_gpt_dict(self):
        return {
            'gear_name': self.gear.name.string,
            'primary_ability_name': self.primary_ability.name.string,
            'secondary_ability_names': [
                self.secondary_abilities[0].name.string if self.secondary_abilities[0] else None,
                self.secondary_abilities[1].name.string if self.secondary_abilities[1] else None,
                self.secondary_abilities[2].name.string if self.secondary_abilities[2] else None,
            ],
        }


class BattleGroup(models.Model):
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    battles = models.ManyToManyField(Battle)

    def __str__(self):
        return f'Battle Group {self.id} - @{self.creator.username}'

    def get_absolute_url(self):
        return reverse('battles:view_battle_group', args=[str(self.id)])
