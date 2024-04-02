from typing import cast

import strawberry
import strawberry_django
from graphql import GraphQLError
from strawberry.types import Info
from strawberry_django.auth.utils import get_current_user
from strawberry_django.permissions import IsAuthenticated
from strawberry_django.relay import ListConnectionWithTotalCount

import splatnet_assets.models
from battles import models
from battles.formats.splashcat_battle import SplashcatBattle
from battles.types import Battle, Player, BattleInput
from battles.utils import get_title_parts_from_string, get_nameplate_badge
from splatnet_assets.fields import Color
from users.models import User


@strawberry.type(name="Query")
class BattlesQuery:
    battle: Battle = strawberry_django.node()
    battles: ListConnectionWithTotalCount[Battle] = strawberry_django.connection()
    player: Player = strawberry_django.node()


@strawberry.type(name="Mutation")
class BattlesMutation:
    @strawberry_django.mutation(extensions=[IsAuthenticated()])
    def create_battle(self, battle_details: BattleInput, info: Info) -> Battle:
        current_user: User = cast(get_current_user(info), User)
        if models.Battle.objects.filter(splatnet_id=battle_details.splatnet_id, uploader=current_user).exists():
            raise GraphQLError("Battle with the same splatnet_id already exists for the current user.")

        battle = models.Battle(data_type="GraphQL", uploader=current_user, raw_data="")
        battle.splatnet_id = battle_details.splatnet_id
        battle.vs_mode = battle_details.vs_mode
        battle.vs_rule = battle_details.vs_rule
        battle.vs_stage = battle_details.vs_stage
        battle.played_time = battle_details.played_time
        battle.duration = battle_details.duration
        battle.judgement = battle_details.judgement
        battle.knockout = battle_details.knockout

        if battle_details.anarchy:
            battle.anarchy_mode = battle_details.anarchy.mode
            battle.anarchy_point_change = battle_details.anarchy.point_change
            battle.anarchy_rank = battle_details.anarchy.rank
            battle.anarchy_s_plus_number = battle_details.anarchy.s_plus_number
            battle.anarchy_points = battle_details.anarchy.points
            battle.power = battle_details.anarchy.power

        if battle_details.x_battle:
            battle.x_battle_rank = battle_details.x_battle.rank
            battle.x_battle_division = current_user.x_battle_division
            battle.power = battle_details.x_battle.power

        if battle_details.splatfest:
            battle.splatfest_mode = battle_details.splatfest.mode
            battle.splatfest_clout_multiplier = battle_details.splatfest.clout_multiplier
            battle.power = battle_details.splatfest.power

        if battle_details.challenge:
            try:
                challenge = splatnet_assets.models.Challenge.objects.get(internal_id=battle_details.challenge.id)
            except splatnet_assets.models.Challenge.DoesNotExist:
                challenge = None
            battle.challenge = challenge
            battle.power = battle_details.challenge.power

        battle.save()

        for i, team in enumerate(battle_details.teams):
            team_object = battle.teams.create(
                is_my_team=team.is_my_team,
                color=Color.from_floating_point_dict(team.color.to_dict()),
                fest_streak_win_count=team.fest_streak_win_count,
                fest_team_name=team.fest_team_name,
                fest_uniform_bonus_rate=team.fest_uniform_bonus_rate,
                fest_uniform_name=team.fest_uniform_name,
                judgement=team.judgement,
                order=team.order,
                noroshi=team.noroshi,
                paint_ratio=team.paint_ratio,
                score=team.score,
                tricolor_role=team.tricolor_role,
            )

            for pi, player in enumerate(team.players):
                title_adjective, title_subject = get_title_parts_from_string(player.byname)

                team_object.players.create(
                    is_self=player.is_self,
                    species=player.species,
                    npln_id=player.npln_id,
                    name=player.name,
                    name_id=player.name_id,
                    title_adjective=title_adjective,
                    title_subject=title_subject,
                    nameplate_background=splatnet_assets.models.NameplateBackground.objects.get(
                        splatnet_id=player.splashtag_background_id),
                    nameplate_badge_1=splatnet_assets.models.NameplateBadge.objects.get(
                        player.splashtag_badge_ids[0]) if player.splashtag_badge_ids[0] else None,
                    nameplate_badge_2=splatnet_assets.models.NameplateBadge.objects.get(
                        player.splashtag_badge_ids[1]) if player.splashtag_badge_ids[1] else None,
                    nameplate_badge_3=splatnet_assets.models.NameplateBadge.objects.get(
                        player.splashtag_badge_ids[2]) if player.splashtag_badge_ids[2] else None,
                    weapon=splatnet_assets.models.Weapon.objects.get(splatnet_id=player.weapon_id),
                    head_gear=get_player_gear_graphql(player.head_gear),
                    clothing_gear=get_player_gear_graphql(player.clothing_gear),
                    shoes_gear=get_player_gear_graphql(player.shoes_gear),
                    disconnect=player.disconnect,
                    kills=player.kills,
                    assists=player.assists,
                    deaths=player.deaths,
                    specials=player.specials,
                    paint=player.paint,
                    noroshi_try=player.noroshi_try,
                    order=pi,
                )
        for i, award in enumerate(battle_details.award_names):
            battle.awards.add(
                splatnet_assets.models.Award.objects.filter(name__string_en_us=award).first(),
                through_defaults={'order': i}
            )
        return battle
