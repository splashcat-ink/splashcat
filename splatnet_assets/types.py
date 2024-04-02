import re
from typing import List

import strawberry_django
from strawberry import auto, relay
import strawberry

from . import models
from .badge_descriptions import get_proper_badge_localization


@strawberry_django.type(models.Image)
class Image(relay.Node):
    image: auto
    type: auto
    asset_name: auto
    original_file_name: auto
    width: auto
    height: auto

    @strawberry_django.field(only=["image"])
    def url(self, root: models.Image) -> str:
        return root.image.url


@strawberry_django.type(models.LocalizationString)
class LocalizationString(relay.Node):
    internal_id: auto
    type: auto
    string_de_de: auto
    string_en_gb: auto
    string_en_us: auto
    string_es_es: auto
    string_es_mx: auto
    string_fr_ca: auto
    string_fr_fr: auto
    string_it_it: auto
    string_ja_jp: auto
    string_ko_kr: auto
    string_nl_nl: auto
    string_ru_ru: auto
    string_zh_cn: auto
    string_zh_tw: auto

    @strawberry_django.field(only=[
        "string_de_de",
        "string_en_gb",
        "string_en_us",
        "string_es_es",
        "string_es_mx",
        "string_fr_ca",
        "string_fr_fr",
        "string_it_it",
        "string_ja_jp",
        "string_ko_kr",
        "string_nl_nl",
        "string_ru_ru",
        "string_zh_cn",
        "string_zh_tw",
    ])
    def string(self, root) -> str:
        return root.string


@strawberry_django.type(models.Gear)
class Gear(relay.Node):
    internal_id: auto
    name: LocalizationString
    type: auto
    brand: 'Brand'
    rarity: auto
    main_ability: 'Ability'
    image: Image


@strawberry_django.type(models.Ability)
class Ability(relay.Node):
    internal_id: auto
    name: LocalizationString
    image: Image
    description: LocalizationString


@strawberry_django.type(models.Brand)
class Brand(relay.Node):
    internal_id: auto
    name: LocalizationString
    favored_ability: Ability
    unfavored_ability: Ability


@strawberry_django.type(models.NameplateBackground)
class NameplateBackground(relay.Node):
    internal_id: auto
    splatnet_id: auto
    image: Image
    text_color: auto


@strawberry_django.type(models.NameplateBadge)
class NameplateBadge(relay.Node):
    internal_id: auto
    splatnet_id: auto
    image: Image

    # description: LocalizationString
    @strawberry_django.field()
    def description(self, root) -> str:
        return get_proper_badge_localization(root)


@strawberry_django.type(models.Stage)
class Stage(relay.Node):
    internal_id: auto
    splatnet_id: auto
    name: LocalizationString
    image: Image
    image_banner: Image


@strawberry_django.type(models.Award)
class Award(relay.Node):
    internal_id: auto
    name: LocalizationString
    gold: auto


@strawberry_django.type(models.TitleAdjective)
class TitleAdjective(relay.Node):
    internal_id: auto
    string: LocalizationString


@strawberry_django.type(models.TitleSubject)
class TitleSubject(relay.Node):
    internal_id: auto
    string: LocalizationString


@strawberry_django.type(models.Weapon)
class Weapon(relay.Node):
    internal_id: auto
    splatnet_id: auto
    name: LocalizationString
    sub: 'SubWeapon'
    special: 'SpecialWeapon'
    flat_image: Image
    image_3d: Image


@strawberry_django.type(models.SubWeapon)
class SubWeapon(relay.Node):
    internal_id: auto
    splatnet_id: auto
    name: LocalizationString
    image: Image
    mask_image: Image
    overlay_image: Image


@strawberry_django.type(models.SpecialWeapon)
class SpecialWeapon(relay.Node):
    internal_id: auto
    splatnet_id: auto
    name: LocalizationString
    image: Image
    mask_image: Image
    overlay_image: Image


@strawberry_django.type(models.Challenge)
class Challenge(relay.Node):
    internal_id: auto
    name: LocalizationString
    description: LocalizationString
    long_description: LocalizationString


@strawberry_django.type(models.Splatfest)
class Splatfest(relay.Node):
    internal_id: auto
    start_date: auto
    end_date: auto
    team_1_color: auto
    team_2_color: auto
    team_3_color: auto
