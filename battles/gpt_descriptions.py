from battles.models import Battle


def battle_to_gpt_dict(battle: Battle):
    data = {
        'uploader_preferred_pronouns': battle.uploader.preferred_pronouns or "they/them",
        'vs_mode': battle.get_vs_mode_display(),
        'vs_rule': battle.get_vs_rule_display(),
        'stage_name': battle.vs_stage.name.string,
        'played_time': battle.played_time.isoformat(),
        'duration': battle.duration.total_seconds(),
        'judgement': battle.get_judgement_display(),
        'knockout': battle.get_knockout_display(),
        'splatfest_clout_multiplier': battle.get_splatfest_clout_multiplier_display(),
        'awards': [],
        'teams': [],
    }

    for award in battle.awards.all():
        data['awards'].append(award.name.string)

    for team in battle.teams.all():
        data['teams'].append(team_to_gpt_dict(team))

    return data


def team_to_gpt_dict(team):
    data = {
        'is_my_team': team.is_my_team,
        'fest_streak_win_count': team.fest_streak_win_count,
        'fest_team_name': f'Team {team.fest_team_name}' if team.fest_team_name else None,
        'judgement': team.get_judgement_display(),
        'score': team.score,
        'paint_ratio': team.paint_ratio,
        'order': team.order,
        'players': [],
    }

    for player in team.players.all():
        data['players'].append(player_to_gpt_dict(player))

    return data


def player_to_gpt_dict(player):
    data = {
        'is_self': player.is_self,
        'name': player.name,
        'weapon_name': player.weapon.name.string,
        'disconnect': player.disconnect,
        'kills': player.kills,
        'deaths': player.deaths,
        'specials': player.specials,
        'paint': player.paint,
        'order': player.order,
    }

    if player.is_self and player.team.battle.uploader.preferred_pronouns is not None:
        data['pronouns'] = player.team.battle.uploader.preferred_pronouns

    return data
