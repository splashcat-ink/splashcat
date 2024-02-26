import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from battles.models import Battle, Team, Player


class BattleNode(DjangoObjectType):
    class Meta:
        model = Battle
        exclude = ('raw_data', )
        filter_fields = ('uploader', 'splatnet_id', 'id')
        interfaces = (relay.Node, )


class TeamNode(DjangoObjectType):
    class Meta:
        model = Team
        fields = '__all__'
        interfaces = (relay.Node, )


class PlayerNode(DjangoObjectType):
    class Meta:
        model = Player
        fields = ('name', 'is_self', 'name_id', 'species', 'disconnect', 'kills', 'assists', 'deaths', 'specials', 'paint', 'noroshi_try', 'order', 'byname', 'splashtag')
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    battle = relay.Node.Field(BattleNode)
    battles = DjangoFilterConnectionField(BattleNode)
