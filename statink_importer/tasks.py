import gzip
import json
import re
from datetime import datetime, timedelta

from celery import shared_task
from django.db import transaction

from battles.models import Battle, Team, PlayerGear
from battles.utils import get_title_parts_from_string, get_ability, find_existing_battle
from splatnet_assets.fields import Color
from splatnet_assets.models import *
from statink_importer.models import StatInkImport

lobby_to_vs_mode = {
    'regular': "REGULAR",
    'bankara_challenge': "BANKARA",
    'bankara_open': "BANKARA",
    'xmatch': "X_MATCH",
    'splatfest_challenge': "FEST",
    'splatfest_open': "FEST",
    'event': "CHALLENGE",
    'private': "PRIVATE",
}

rule_to_vs_rule = {
    'nawabari': 'TURF_WAR',
    'area': 'AREA',
    'yagura': 'LOFT',
    'hoko': 'GOAL',
    'asari': 'CLAM',
    'tricolor': 'TRI_COLOR',
}

result_to_judgement = {
    'draw': 'DRAW',
    'exempted_lose': 'EXEMPTED_LOSE',
    'lose': 'LOSE',
    'win': 'WIN',
}


@shared_task(autoretry_for=(Exception,), retry_backoff=True)
def import_statink(import_id):
    statink_import = StatInkImport.objects.get(pk=import_id)
    uploader = statink_import.user

    file_data = statink_import.file
    if statink_import.file.read(1) == b'{':
        statink_import.file.seek(0)
    else:
        file_data = gzip.decompress(file_data)

    for json_line in file_data:
        data = json.loads(json_line)

        played_time = datetime.fromisoformat(get_or(data, "start_at", data.get('created_at')).get("iso8601"))

        if not (data.get('lobby') and data.get('rule') and data.get('stage') and data.get(
                'result') and not find_existing_battle(uploader, played_time)):
            # battle is likely a weird broken one or already exists, skip
            print(f'skipping battle {data.get("id")}')
            continue

        with transaction.atomic():
            battle = Battle(data_type="stat.ink", raw_data=data, uploader_id=statink_import.user_id)
            battle.statink_id = data.get('id')
            battle.statink_username = find_username(data.get('url', ''))
            battle.played_time = played_time
            battle.vs_mode = lobby_to_vs_mode.get(data.get('lobby').get('key'))
            battle.vs_rule = rule_to_vs_rule.get(data.get('rule').get('key'))
            battle.vs_stage = \
                Stage.objects.filter(name__string_en_us=data.get('stage').get('name').get('en_US')).order_by(
                    '-id')[0]
            battle.duration = datetime.fromisoformat(data.get("end_at").get("iso8601")) - datetime.fromisoformat(
                data.get("start_at").get("iso8601"))
            battle.judgement = result_to_judgement.get(data.get('result'))

            lobby = data.get('lobby').get('key')
            if 'bankara' in lobby:
                battle.anarchy_mode = 'OPEN' if lobby == 'bankara_open' else 'SERIES'
                battle.anarchy_point_change = data.get('rank_exp_change')
                battle.power = data.get('bankara_power_after')
                battle.anarchy_rank = get_or(data, 'rank_after', {}).get('name', {}).get('en_US')
                battle.anarchy_s_plus_number = data.get('rank_after_s_plus')
                battle.anarchy_points = data.get('rank_after_exp')

            if lobby == 'xmatch':
                battle.power = data.get('x_power_before')

            if 'splatfest' in lobby:
                battle.splatfest_mode = 'OPEN' if lobby == 'splatfest_open' else 'PRO'
                battle.splatfest_clout_multiplier = None
                battle.splatfest_clout_contribution = data.get('clout_after')
                battle.power = data.get('fest_power')

            if lobby == 'event':
                try:
                    challenge = Challenge.objects.get(
                        name__string_en_us=get_or(data, 'event', {}).get('name', {}).get('en_US'))
                except Challenge.DoesNotExist:
                    challenge = None
                battle.challenge = challenge
                battle.power = data.get('event_power')

            battle.save()

            for i, team in enumerate(['our_team', 'their_team', 'third_team']):
                if data.get(f"{team}_members"):
                    # team exists
                    tricolor_role = None
                    role = get_or(data, f'{team}_role', {}).get('key')
                    if role == 'attacker':
                        if team == 'third_team':
                            tricolor_role = "ATTACK2"
                        else:
                            tricolor_role = "ATTACK1"
                    elif role == 'defender':
                        tricolor_role = "DEFENSE"

                    color = data.get(f"{team}_color")
                    if not color:
                        if team == 'our_team':
                            color = 'd0be08'
                        elif team == 'their_team':
                            color = '3a0ccd'
                        elif team == 'third_team':
                            color = 'b62ea7'

                    team_object = battle.teams.create(
                        is_my_team=team == 'our_team',
                        color=Color.from_hex(color),
                        fest_team_name=data.get(f"{team}_theme"),
                        judgement='DRAW' if battle.judgement == 'DRAW' else (
                            'WIN' if (team == 'our_team' and battle.judgement == 'WIN') else (
                                'WIN' if (team == 'their_team' and battle.judgement != 'WIN') else "LOSE")),
                        order=3 if team == 'third_team' else (
                            1 if (team == 'our_team' and battle.judgement == 'WIN') else 2),
                        noroshi=None,
                        paint_ratio=float(data.get(f'{team}_percent')) / 100 if data.get(f'{team}_percent') else None,
                        score=data.get(f'{team}_count'),
                        tricolor_role=tricolor_role,
                    )
                    team_object.save()

                    for pi, player in enumerate(data.get(f'{team}_members')):
                        title_adjective, title_subject = get_title_parts_from_string(player.get('splashtag_title'))

                        weapon = Weapon.objects.get(
                            name__string_en_us=get_or(player, 'weapon', {}).get('name', {}).get('en_US'))

                        if not weapon:
                            print("OH NO THAT'S BAD")

                        team_object.players.create(
                            is_self=player.get('me'),
                            species=get_or(player, 'species', {}).get('key', 'inkling').upper(),
                            npln_id='',
                            name=player.get('name'),
                            name_id=player.get('number'),
                            title_adjective=title_adjective,
                            title_subject=title_subject,
                            nameplate_background=NameplateBackground.objects.get(splatnet_id=1),
                            nameplate_badge_1=None,
                            nameplate_badge_2=None,
                            nameplate_badge_3=None,
                            weapon=weapon,
                            head_gear=get_player_gear(get_or(player, 'gears', {}).get('headgear')),
                            clothing_gear=get_player_gear(get_or(player, 'gears', {}).get('clothing')),
                            shoes_gear=get_player_gear(get_or(player, 'gears', {}).get('shoes')),
                            disconnect=player.get('disconnected'),
                            kills=player.get('kill_or_assist'),
                            assists=player.get('assist'),
                            deaths=player.get('death'),
                            specials=player.get('special'),
                            paint=player.get('inked'),
                            noroshi_try=player.get('signal'),
                            order=player.get('rank_in_team'),
                        ).save()
            battle.x_battle_division = 'UNSPECIFIED'
            battle.save()
            print(f"saved battle {battle.id}")


def get_player_gear(gear):
    if not gear:
        gear = {}
    secondary_abilities = gear.get('secondary_abilities', [{}])
    gear = PlayerGear(
        gear=Gear.objects.get(internal_id=0),
        primary_ability=get_ability_from_statink(get_or(gear, 'primary_ability', None)),
        secondary_ability_1=get_ability_from_statink(secondary_abilities[0]),
        secondary_ability_2=get_ability_from_statink(secondary_abilities[1])
        if len(secondary_abilities) > 1 else None,
        secondary_ability_3=get_ability_from_statink(secondary_abilities[2])
        if len(secondary_abilities) > 2 else None,
    )
    gear.save()
    return gear


def get_ability_from_statink(ability):
    if ability:
        return get_ability(ability.get('name', {}).get('en_US'))
    else:
        return Ability.objects.get(internal_id='None')


def get_or(obj, index, default):
    ret = obj.get(index)
    if not ret:
        return default
    return ret


def find_username(text):
    match = re.search(r'/@(\w+)/', text)
    return match.group(1) if match else None
