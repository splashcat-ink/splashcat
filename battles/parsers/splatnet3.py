import base64
import json

from jsonschema import validate

from battles.formats.vs_history_detail import VsHistoryDetail, PlayerResult
from battles.models import Battle
from battles.utils import get_splatnet_int_id, get_title_parts_from_string, get_player_gear, get_npln_id, \
    get_nameplate_badge, BattleAlreadyExistsError
from splatnet_assets.fields import Color
from splatnet_assets.models import Stage, NameplateBackground, Weapon, Award


def parse_splatnet3(data, request):
    # haven't finished schema validation yet...
    # raise NotImplementedError()

    with open('./battles/format_schemas/SplatNet3/battle.schema.json') as f:
        schema = json.load(f)
    validate(data['battle'], schema)

    vs_history_detail = VsHistoryDetail.from_dict(data['battle'])
    splatnet_id = vs_history_detail.id
    splatnet_id = base64.b64decode(splatnet_id).decode('utf-8')
    splatnet_id = splatnet_id.split(':')[-1]

    if Battle.objects.filter(splatnet_id=splatnet_id).exists():
        raise BattleAlreadyExistsError()

    battle = Battle(data_type="splatnet3", raw_data=data['battle'], uploader=request.user)
    battle.splatnet_id = splatnet_id
    battle.vs_mode = vs_history_detail.vs_mode.mode.value
    battle.vs_rule = vs_history_detail.vs_rule.rule.value
    battle.vs_stage = Stage.objects.get(splatnet_id=get_splatnet_int_id(vs_history_detail.vs_stage.id))
    battle.played_time = vs_history_detail.played_time
    battle.duration = vs_history_detail.duration
    battle.judgement = vs_history_detail.judgement.value
    battle.knockout = vs_history_detail.knockout.value
    teams = [vs_history_detail.my_team] + vs_history_detail.other_teams
    battle.save()
    for i, team in enumerate(teams):
        team_object = battle.teams.create(
            is_my_team=i == 0,
            color=Color.from_floating_point_dict(team.color.to_dict()),
            fest_streak_win_count=team.fest_streak_win_count,
            fest_team_name=team.fest_team_name,
            fest_uniform_bonus_rate=team.fest_uniform_bonus_rate,
            fest_uniform_name=team.fest_uniform_name,
            judgement=team.judgement.value,
            order=team.order,
            noroshi=team.result.noroshi,
            paint_ratio=team.result.paint_ratio,
            score=team.result.score,
            tricolor_role=team.tricolor_role.value if team.tricolor_role else None,
        )
        for player in team.players:
            title_adjective, title_subject = get_title_parts_from_string(player.byname)

            team_object.players.create(
                is_self=player.is_myself,
                species=player.species.value,
                npln_id=get_npln_id(player.id),
                name=player.name,
                name_id=player.name_id,
                title_adjective=title_adjective,
                title_subject=title_subject,
                nameplate_background=NameplateBackground.objects.get(
                    splatnet_id=get_splatnet_int_id(player.nameplate.background.id)),
                nameplate_badge_1=get_nameplate_badge(player.nameplate.badges[0]),
                nameplate_badge_2=get_nameplate_badge(player.nameplate.badges[1]),
                nameplate_badge_3=get_nameplate_badge(player.nameplate.badges[2]),
                weapon=Weapon.objects.get(splatnet_id=get_splatnet_int_id(player.weapon.id)),
                head_gear=get_player_gear(player.head_gear),
                clothing_gear=get_player_gear(player.clothing_gear),
                shoes_gear=get_player_gear(player.shoes_gear),
                disconnect=not isinstance(player.result, PlayerResult),
                kills=player.result.kill if isinstance(player.result, PlayerResult) else None,
                assists=player.result.assist if isinstance(player.result, PlayerResult) else None,
                deaths=player.result.death if isinstance(player.result, PlayerResult) else None,
                specials=player.result.special if isinstance(player.result, PlayerResult) else None,
                paint=player.paint,
                noroshi_try=player.result.noroshi_try if isinstance(player.result, PlayerResult) else None,
            )
    battle.save()
    for i, award in enumerate(vs_history_detail.awards):
        battle.awards.add(
            Award.objects.filter(name__string_en_us=award.name).first(),
            through_defaults={
                'order': i,
            },
        )
    battle.save()
    return battle
