from typing import List, Optional, TYPE_CHECKING, Annotated

import strawberry_django
from strawberry import auto, relay
import strawberry

from splatnet_assets.types import TitleAdjective, TitleSubject, NameplateBackground, NameplateBadge, Weapon, Gear, \
    Stage, Challenge, Ability
from . import models

if TYPE_CHECKING:
    from users.types import User


@strawberry_django.order(models.Battle)
class BattleOrder:
    played_time: auto
    uploaded_at: auto


@strawberry_django.filter(models.Battle)
class BattleFilter:
    id: auto
    uploader: auto
    data_type: auto
    uploaded_at: auto
    played_time: auto
    vs_mode: auto
    vs_rule: auto
    vs_stage: auto
    judgement: auto


@strawberry_django.type(models.Battle, filters=BattleFilter, order=BattleOrder)
class Battle(relay.Node):
    uploader: Annotated["User", strawberry.lazy("users.types")]
    uploader_agent_name: auto
    uploader_agent_version: auto
    uploader_agent_extra: auto
    splatnet_id: auto
    data_type: auto
    uploaded_at: auto
    updated_at: auto
    vs_mode: auto
    vs_rule: auto
    vs_stage: Stage
    played_time: auto
    # duration: auto
    judgement: auto
    knockout: auto
    anarchy_mode: auto
    anarchy_point_change: auto
    anarchy_rank: auto
    anarchy_s_plus_number: auto
    anarchy_points: auto
    x_battle_rank: auto
    x_battle_division: auto
    splatfest_mode: auto
    splatfest_clout_multiplier: auto
    splatfest_clout_contribution: auto
    splatfest_festival_shells: auto
    power: auto
    challenge: Challenge
    gpt_description: auto
    gpt_description_generated: auto
    gpt_description_generated_at: auto
    teams: List["Team"]

    @strawberry_django.field(
        prefetch_related=["teams__players__weapon__name", "teams__players__weapon__flat_image",
                          "teams__players__weapon__image_3d",
                          "teams__players__weapon__sub__name", "teams__players__weapon__sub__mask_image",
                          "teams__players__weapon__sub__overlay_image",
                          "teams__players__weapon__special__name", "teams__players__weapon__special__mask_image",
                          "teams__players__weapon__special__overlay_image", ])
    def weapon(self, root) -> Weapon:
        return root.player.weapon


@strawberry_django.type(models.Team)
class Team(relay.Node):
    battle: Battle
    is_my_team: auto
    color: auto
    fest_streak_win_count: auto
    fest_team_name: auto
    fest_uniform_bonus_rate: auto
    fest_uniform_name: auto
    judgement: auto
    order: auto
    noroshi: auto
    paint_ratio: auto
    score: auto
    tricolor_role: auto
    players: List["Player"]


@strawberry_django.type(models.Player)
class Player(relay.Node):
    team: Team
    is_self: auto
    npln_id: auto
    name: auto
    name_id: auto
    species: auto
    title_adjective: Optional[TitleAdjective]
    title_subject: Optional[TitleSubject]
    nameplate_background: NameplateBackground
    nameplate_badge_1: Optional[NameplateBadge]
    nameplate_badge_2: Optional[NameplateBadge]
    nameplate_badge_3: Optional[NameplateBadge]
    weapon: Weapon
    head_gear: 'PlayerGear'
    clothing_gear: 'PlayerGear'
    shoes_gear: 'PlayerGear'
    disconnect: auto
    kills: auto
    assists: auto
    deaths: auto
    specials: auto
    paint: auto
    noroshi_try: auto
    order: auto

    @strawberry_django.field(select_related=["title_adjective__string", "title_subject__string"])
    def byname(self, root) -> str:
        return root.byname

    @strawberry_django.field(
        select_related=["title_adjective__string", "title_subject__string", "nameplate_background__image",
                        "nameplate_badge_1__image", "nameplate_badge_2__image", "nameplate_badge_3__image",
                        "nameplate_badge_1__description", "nameplate_badge_2__description",
                        "nameplate_badge_3__description"], only=["name", "name_id"])
    def splashtag(self, root) -> 'Splashtag':
        splashtag_data = root.splashtag
        return Splashtag(name=splashtag_data.get('name'), name_id=splashtag_data.get('name_id'),
                         title_adjective=splashtag_data.get('title_adjective'),
                         title_subject=splashtag_data.get('title_subject'),
                         badges=splashtag_data.get('badges'), background=splashtag_data.get('background'))


@strawberry.type
class Splashtag:
    name: str
    name_id: Optional[str]
    title_adjective: Optional[TitleAdjective]
    title_subject: Optional[TitleSubject]
    badges: List[NameplateBadge | None]
    background: NameplateBackground


@strawberry_django.type(models.PlayerGear)
class PlayerGear(relay.Node):
    gear: Gear
    primary_ability: Ability
    secondary_ability_1: Ability
    secondary_ability_2: Ability
    secondary_ability_3: Ability

    @strawberry_django.field
    def secondary_abilities(self, root: models.PlayerGear) -> List[Ability | None]:
        return root.secondary_abilities


@strawberry.input()
class ColorInput:
    a: float
    r: float
    g: float
    b: float

    def to_dict(self):
        return {
            "a": self.a,
            "r": self.r,
            "g": self.g,
            "b": self.b,
        }


@strawberry.input()
class AnarchyInput:
    mode: Optional[strawberry.enum(models.Battle.AnarchyMode)]
    point_change: Optional[int]
    rank: Optional[str]
    s_plus_number: Optional[int]
    points: Optional[int]
    power: Optional[float]


@strawberry.input()
class XBattleInput:
    power: Optional[int]
    rank: Optional[float]


@strawberry.input()
class SplatfestInput:
    mode: strawberry.enum(models.Battle.SplatfestBattleType)
    clout_multiplier: strawberry.enum(models.Battle.SplatfestBattleCloutMultiplier)
    power: Optional[float]


@strawberry.input()
class ChallengeInput:
    id: Optional[str]
    power: Optional[float]


@strawberry_django.input(models.Battle)
class BattleInput:
    uploader_agent_name: auto
    uploader_agent_version: auto
    uploader_agent_extra: auto
    splatnet_id: auto
    # raw_data: auto
    vs_mode: auto
    vs_rule: auto
    vs_stage: str
    played_time: str
    duration: int
    judgement: auto
    knockout: auto
    anarchy: Optional[AnarchyInput]
    x_battle: Optional[XBattleInput]
    splatfest: Optional[SplatfestInput]
    challenge: Optional[ChallengeInput]
    award_names: list[str]
    teams: list['TeamInput']


@strawberry_django.input(models.Team)
class TeamInput:
    is_my_team: auto
    color: ColorInput
    fest_streak_win_count: auto
    fest_team_name: auto
    fest_uniform_bonus_rate: auto
    fest_uniform_name: auto
    judgement: auto
    order: auto
    noroshi: auto
    paint_ratio: auto
    score: auto
    tricolor_role: auto
    players: list['PlayerInput']


@strawberry_django.input(models.Player)
class PlayerInput:
    is_self: auto
    species: auto
    npln_id: auto
    name: auto
    name_id: auto
    byname: str
    splashtag_background_id: int
    splashtag_badge_ids: list[int]
    weapon_id: int
    head_gear: "PlayerGearInput"
    clothing_gear: "PlayerGearInput"
    shoes_gear: "PlayerGearInput"
    disconnect: auto
    kills: auto
    assists: auto
    deaths: auto
    specials: auto
    paint: auto
    noroshi_try: auto
    order: auto


@strawberry_django.input(models.PlayerGear)
class PlayerGearInput:
    name: str
    primary_ability_name: str
    secondary_ability_names: list[str]
