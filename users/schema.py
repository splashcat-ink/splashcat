import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from users.models import User


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'preferred_pronouns', 'profile_picture', 'sponsor_tiers', 'battles')
        filter_fields = ['username']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    users = DjangoFilterConnectionField(UserNode)
    user = relay.Node.Field(UserNode)
