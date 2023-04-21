import base64
import json

import jsonschema
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from jsonschema import validate

from battles.formats.vs_history_detail import VsHistoryDetail, PlayerResult
from battles.models import *
from battles.utils import get_splatnet_int_id, get_title_parts_from_string, get_player_gear, get_npln_id, \
    get_nameplate_badge
from splashcat.decorators import api_auth_required
from splatnet_assets.fields import Color
from splatnet_assets.models import *


# Create your views here.

@csrf_exempt
@require_http_methods(['POST'])
@api_auth_required
def upload_battle(request):
    data = request.body
    if request.content_type == 'application/json':
        data = json.loads(data)
    elif request.content_type == 'application/x-messagepack':
        import msgpack
        data = msgpack.unpackb(data)

    # deny request if data is over 512KB
    if len(data) > 512 * 1024:
        return HttpResponseBadRequest(
            json.dumps({
                'error': 'request too large',
            })
        )

    try:
        validate(data, {
            'type': 'object',
            'properties': {
                'battle': {
                    'type': 'object',
                },
                'data_type': {
                    'enum': ['splatnet3']
                }
            },
            'required': ['battle', 'data_type'],
        })
    except jsonschema.ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps(e)
        )

    # passed input validation, validate the battle data

    with open('./battles/format_schemas/SplatNet3/battle.schema.json') as f:
        schema = json.load(f)

    try:
        validate(data['battle'], schema)
    except jsonschema.ValidationError as e:
        return HttpResponseBadRequest(
            e
        )

    # passed input validation, save the battle data

    print("yay we passed that")

    battle = Battle(data_type="splatnet3", raw_data=data['battle'], uploader=request.user)

    vs_history_detail = VsHistoryDetail.from_dict(data['battle'])

    splatnet_id = vs_history_detail.id
    splatnet_id = base64.b64decode(splatnet_id).decode('utf-8')
    battle.splatnet_id = splatnet_id.split(':')[-1]

    battle.vs_mode = vs_history_detail.vs_mode.mode.value
    battle.vs_rule = vs_history_detail.vs_rule.rule.value
    battle.vs_stage = Stage.objects.get(splatnet_id=get_splatnet_int_id(vs_history_detail.vs_stage.id))
    battle.played_time = vs_history_detail.played_time
    battle.duration = vs_history_detail.duration
    battle.judgement = vs_history_detail.judgement.value

    title_adjective, title_subject = get_title_parts_from_string(vs_history_detail.player.byname)
    battle.player_title_adjective = title_adjective
    battle.player_title_subject = title_subject
    battle.player_head_gear = get_player_gear(vs_history_detail.player.head_gear)
    battle.player_clothing_gear = get_player_gear(vs_history_detail.player.clothing_gear)
    battle.player_shoes_gear = get_player_gear(vs_history_detail.player.shoes_gear)
    battle.player_npln_id = get_npln_id(vs_history_detail.player.id)
    battle.player_name = vs_history_detail.player.name
    battle.player_name_id = vs_history_detail.player.name_id
    battle.player_nameplate_background = NameplateBackground.objects.get(
        splatnet_id=get_splatnet_int_id(vs_history_detail.player.nameplate.background.id))
    battle.player_nameplate_badge_1 = get_nameplate_badge(vs_history_detail.player.nameplate.badges[0])
    battle.player_nameplate_badge_2 = get_nameplate_badge(vs_history_detail.player.nameplate.badges[1])
    battle.player_nameplate_badge_3 = get_nameplate_badge(vs_history_detail.player.nameplate.badges[2])
    battle.player_paint = vs_history_detail.player.paint

    battle.knockout = vs_history_detail.knockout.value

    battle.save()

    for i, award in enumerate(vs_history_detail.awards):
        battle.awards.add(
            Award.objects.filter(name__string_en_us=award.name).first(),
            through_defaults={
                'order': i,
            },
        )

    teams = [vs_history_detail.my_team] + vs_history_detail.other_teams

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

    return JsonResponse({
        'status': 'ok',
        'battle_id': battle.id,
    })
