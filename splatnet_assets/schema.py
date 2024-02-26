import graphene
from graphene import relay
from query_optimizer import DjangoObjectType, DjangoConnectionField

from splatnet_assets.models import NameplateBadge, Image, Weapon, LocalizationString


class LocalizationStringType(DjangoObjectType):
    string = graphene.String()

    class Meta:
        model = LocalizationString
        fields = '__all__'

    @staticmethod
    def resolve_string(parent, info):
        return parent.string


class ImageType(DjangoObjectType):
    class Meta:
        model = Image
        fields = '__all__'


class NameplateBadgeType(DjangoObjectType):
    class Meta:
        model = NameplateBadge
        fields = ('image', 'internal_id', 'splatnet_id')


class WeaponType(DjangoObjectType):
    class Meta:
        model = Weapon
        fields = '__all__'
