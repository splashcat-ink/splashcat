import graphene
from graphene import relay
from query_optimizer import DjangoObjectType, DjangoConnectionField, required_fields
from query_optimizer.filter import DjangoFilterConnectionField

from battles.models import Battle, Team, Player
from splatnet_assets.schema import WeaponType


class BattleNode(DjangoObjectType):
    class Meta:
        model = Battle
        fields = ('uploader', 'uploader_agent_name', 'uploader_agent_variables', 'uploader_agent_extra', 'splatnet_id',
                  'data_type', 'uploaded_at', 'updated_at', 'vs_mode', 'vs_rule', 'vs_stage', 'played_time', 'duration',
                  'judgement', 'knockout', 'anarchy_mode', 'anarchy_point_change', 'anarchy_rank',
                  'anarchy_s_plus_number', 'anarchy_points', 'x_battle_rank', 'x_battle_division', 'splatfest_mode',
                  'splatfest_clout_multiplier', 'splatfest_clout_contribution', 'splatfest_festival_shells', 'power',
                  'challenge', 'gpt_description', 'gpt_description_generated', 'gpt_description_generated_at', 'awards', 'teams')
        filter_fields = ('uploader', 'splatnet_id', 'id')
        interfaces = (relay.Node,)


class TeamType(DjangoObjectType):
    class Meta:
        model = Team
        fields = '__all__'


class SplashtagType(graphene.ObjectType):
    name = graphene.String()
    name_id = graphene.String()
    nameplate_badges = graphene.List(graphene.String)


class PlayerType(DjangoObjectType):
    splashtag = graphene.Field(SplashtagType)
    byname = graphene.String()
    weapon = graphene.Field(WeaponType)

    class Meta:
        model = Player
        fields = (
            'name', 'is_self', 'name_id', 'species', 'disconnect', 'kills', 'assists', 'deaths', 'specials', 'paint',
            'noroshi_try', 'order', 'splashtag', 'weapon')

    @staticmethod
    @required_fields('title_adjective__string', 'title_subject__string')
    def resolve_splashtag(parent, info):
        return parent.splashtag

    @staticmethod
    @required_fields('title_adjective__string__string_en_us', 'title_subject__string__string_en_us')
    def resolve_byname(parent, info):
        return parent.byname

    @staticmethod
    @required_fields('name', 'flat_image', 'image_3d', 'sub__name', 'sub__mask_image', 'sub__overlay_image',
                     'special__name', 'special__mask_image', 'special__overlay_image')
    def resolve_weapon(parent, info):
        return parent.weapon


class Query(graphene.ObjectType):
    battle = relay.Node.Field(BattleNode)
    battles = DjangoConnectionField(BattleNode)
