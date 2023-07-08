import json
from datetime import timedelta
from typing import Optional

from jsonschema.validators import validate

from battles.formats.splashcat_battle import SplashcatBattle, Gear as SplashcatJsonGear
from battles.models import Battle, PlayerGear
from battles.utils import BattleAlreadyExistsError, get_title_parts_from_string, get_ability
from splatnet_assets.fields import Color
from splatnet_assets.models import Gear, Stage, NameplateBackground, NameplateBadge, Weapon, Award, Challenge


def parse_splashcat(data, request):
    with open('./battles/format_schemas/splashcat.schema.json') as f:
        schema = json.load(f)
    validate(data['battle'], schema)

    splashcat_battle = SplashcatBattle.from_dict(data['battle'])

    if Battle.objects.filter(splatnet_id=splashcat_battle.splatnet_id, uploader=request.user).exists():
        raise BattleAlreadyExistsError()

    battle = Battle(data_type="splashcat", raw_data=data['battle'], uploader=request.user)
    battle.splatnet_id = splashcat_battle.splatnet_id
    battle.vs_mode = splashcat_battle.vs_mode.value
    battle.vs_rule = splashcat_battle.vs_rule.value
    battle.vs_stage = Stage.objects.get(splatnet_id=splashcat_battle.vs_stage_id)
    battle.played_time = splashcat_battle.played_time
    battle.duration = timedelta(seconds=splashcat_battle.duration)
    battle.judgement = splashcat_battle.judgement.value
    battle.knockout = splashcat_battle.knockout.value if splashcat_battle.knockout else None

    if splashcat_battle.anarchy:
        battle.anarchy_mode = splashcat_battle.anarchy.mode.value if splashcat_battle.anarchy else None
        battle.anarchy_point_change = splashcat_battle.anarchy.point_change if splashcat_battle.anarchy else None
        battle.power = splashcat_battle.anarchy.power if splashcat_battle.anarchy else None

    if splashcat_battle.x_battle:
        battle.power = splashcat_battle.x_battle.x_power
        battle.x_battle_rank = splashcat_battle.x_battle.x_rank

    if splashcat_battle.splatfest:
        battle.splatfest_mode = splashcat_battle.splatfest.mode.value if \
            splashcat_battle.splatfest.mode else None
        battle.splatfest_clout_multiplier = splashcat_battle.splatfest.clout_multiplier.value if \
            splashcat_battle.splatfest.clout_multiplier else None
        battle.power = splashcat_battle.splatfest.power

    if splashcat_battle.challenge:
        try:
            challenge = Challenge.objects.get(interal_id=splashcat_battle.challenge.id)
        except Challenge.DoesNotExist:
            challenge = None
        battle.challenge = challenge
        battle.power = splashcat_battle.challenge.power

    battle.save()
    for i, team in enumerate(splashcat_battle.teams):
        team_object = battle.teams.create(
            is_my_team=team.is_my_team,
            color=Color.from_floating_point_dict(team.color.to_dict()),
            fest_streak_win_count=team.fest_streak_win_count,
            fest_team_name=team.fest_team_name,
            fest_uniform_bonus_rate=team.fest_uniform_bonus_rate,
            fest_uniform_name=team.fest_uniform_name,
            judgement=team.judgement.value if team.judgement else None,
            order=team.order,
            noroshi=team.noroshi,
            paint_ratio=team.paint_ratio,
            score=team.score,
            tricolor_role=team.tricolor_role.value if team.tricolor_role else None,
        )
        for pi, player in enumerate(team.players):
            title_adjective, title_subject = get_title_parts_from_string(player.title)

            team_object.players.create(
                is_self=player.is_me,
                species=player.species.value,
                npln_id=player.npln_id,
                name=player.name,
                name_id=player.name_id,
                title_adjective=title_adjective,
                title_subject=title_subject,
                nameplate_background=NameplateBackground.objects.get(splatnet_id=player.splashtag_background_id),
                nameplate_badge_1=get_nameplate_badge(player.badges[0]),
                nameplate_badge_2=get_nameplate_badge(player.badges[1]),
                nameplate_badge_3=get_nameplate_badge(player.badges[2]),
                weapon=Weapon.objects.get(splatnet_id=player.weapon_id),
                head_gear=get_player_gear(player.head_gear),
                clothing_gear=get_player_gear(player.clothing_gear),
                shoes_gear=get_player_gear(player.shoes_gear),
                disconnect=player.disconnected,
                kills=player.kills,
                assists=player.assists,
                deaths=player.deaths,
                specials=player.specials,
                paint=player.paint,
                noroshi_try=player.noroshi_try,
                order=pi,
            )
    for i, award in enumerate(splashcat_battle.awards):
        battle.awards.add(
            Award.objects.filter(name__string_en_us=award).first(),
            through_defaults={'order': i}
        )
    return battle


def get_nameplate_badge(badge: Optional[int]):
    if badge is None:
        return None
    return NameplateBadge.objects.get(splatnet_id=badge)


def get_player_gear(gear: SplashcatJsonGear):
    gear = PlayerGear(
        gear=Gear.objects.get(name__string_en_us=gear.name),
        primary_ability=get_ability(gear.primary_ability),
        secondary_ability_1=get_ability(gear.secondary_abilities[0]),
        secondary_ability_2=get_ability(gear.secondary_abilities[1])
        if len(gear.secondary_abilities) > 1 else None,
        secondary_ability_3=get_ability(gear.secondary_abilities[2])
        if len(gear.secondary_abilities) > 2 else None,
    )
    gear.save()
    return gear
