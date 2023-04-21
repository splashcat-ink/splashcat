from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Any, List, TypeVar, Type, cast, Callable

import dateutil.parser

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


class Rank(Enum):
    GOLD = "GOLD"
    SILVER = "SILVER"


@dataclass
class Award:
    name: Optional[str] = None
    rank: Optional[Rank] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Award':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        rank = from_union([Rank, from_none], obj.get("rank"))
        return Award(name, rank)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.rank is not None:
            result["rank"] = from_union([lambda x: to_enum(Rank, x), from_none], self.rank)
        return result


class VsHistoryDetailJudgement(Enum):
    DEEMED_LOSE = "DEEMED_LOSE"
    DRAW = "DRAW"
    EXEMPTED_LOSE = "EXEMPTED_LOSE"
    LOSE = "LOSE"
    WIN = "WIN"


class Knockout(Enum):
    LOSE = "LOSE"
    NEITHER = "NEITHER"
    WIN = "WIN"


@dataclass
class Color:
    a: float
    b: float
    g: float
    r: float

    @staticmethod
    def from_dict(obj: Any) -> 'Color':
        assert isinstance(obj, dict)
        a = from_float(obj.get("a"))
        b = from_float(obj.get("b"))
        g = from_float(obj.get("g"))
        r = from_float(obj.get("r"))
        return Color(a, b, g, r)

    def to_dict(self) -> dict:
        result: dict = {}
        result["a"] = to_float(self.a)
        result["b"] = to_float(self.b)
        result["g"] = to_float(self.g)
        result["r"] = to_float(self.r)
        return result


class MyTeamJudgement(Enum):
    DRAW = "DRAW"
    LOSE = "LOSE"
    WIN = "WIN"


@dataclass
class SimpleImage:
    """Like `Image` but with only a `url` property. The `url` is optional. See `Image` and
    WIKILINK for more details.
    """
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SimpleImage':
        assert isinstance(obj, dict)
        url = from_union([from_str, from_none], obj.get("url"))
        return SimpleImage(url)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.url is not None:
            result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class GearPower:
    image: SimpleImage
    name: str
    desc: Optional[str] = None
    gear_power_id: Optional[int] = None
    is_empty_slot: Optional[bool] = None
    power: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GearPower':
        assert isinstance(obj, dict)
        image = SimpleImage.from_dict(obj.get("image"))
        name = from_str(obj.get("name"))
        desc = from_union([from_str, from_none], obj.get("desc"))
        gear_power_id = from_union([from_int, from_none], obj.get("gearPowerId"))
        is_empty_slot = from_union([from_bool, from_none], obj.get("isEmptySlot"))
        power = from_union([from_int, from_none], obj.get("power"))
        return GearPower(image, name, desc, gear_power_id, is_empty_slot, power)

    def to_dict(self) -> dict:
        result: dict = {}
        result["image"] = to_class(SimpleImage, self.image)
        result["name"] = from_str(self.name)
        if self.desc is not None:
            result["desc"] = from_union([from_str, from_none], self.desc)
        if self.gear_power_id is not None:
            result["gearPowerId"] = from_union([from_int, from_none], self.gear_power_id)
        if self.is_empty_slot is not None:
            result["isEmptySlot"] = from_union([from_bool, from_none], self.is_empty_slot)
        if self.power is not None:
            result["power"] = from_union([from_int, from_none], self.power)
        return result


@dataclass
class Brand:
    id: str
    image: SimpleImage
    name: str
    usual_gear_power: GearPower

    @staticmethod
    def from_dict(obj: Any) -> 'Brand':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        image = SimpleImage.from_dict(obj.get("image"))
        name = from_str(obj.get("name"))
        usual_gear_power = GearPower.from_dict(obj.get("usualGearPower"))
        return Brand(id, image, name, usual_gear_power)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["image"] = to_class(SimpleImage, self.image)
        result["name"] = from_str(self.name)
        result["usualGearPower"] = to_class(GearPower, self.usual_gear_power)
        return result


@dataclass
class BaseGear:
    additional_gear_powers: List[GearPower]
    brand: Brand
    name: str
    original_image: SimpleImage
    primary_gear_power: GearPower
    image: Optional[SimpleImage] = None
    thumbnail_image: Optional[SimpleImage] = None

    @staticmethod
    def from_dict(obj: Any) -> 'BaseGear':
        assert isinstance(obj, dict)
        additional_gear_powers = from_list(GearPower.from_dict, obj.get("additionalGearPowers"))
        brand = Brand.from_dict(obj.get("brand"))
        name = from_str(obj.get("name"))
        original_image = SimpleImage.from_dict(obj.get("originalImage"))
        primary_gear_power = GearPower.from_dict(obj.get("primaryGearPower"))
        image = from_union([SimpleImage.from_dict, from_none], obj.get("image"))
        thumbnail_image = from_union([SimpleImage.from_dict, from_none], obj.get("thumbnailImage"))
        return BaseGear(additional_gear_powers, brand, name, original_image, primary_gear_power, image, thumbnail_image)

    def to_dict(self) -> dict:
        result: dict = {}
        result["additionalGearPowers"] = from_list(lambda x: to_class(GearPower, x), self.additional_gear_powers)
        result["brand"] = to_class(Brand, self.brand)
        result["name"] = from_str(self.name)
        result["originalImage"] = to_class(SimpleImage, self.original_image)
        result["primaryGearPower"] = to_class(GearPower, self.primary_gear_power)
        if self.image is not None:
            result["image"] = from_union([lambda x: to_class(SimpleImage, x), from_none], self.image)
        if self.thumbnail_image is not None:
            result["thumbnailImage"] = from_union([lambda x: to_class(SimpleImage, x), from_none], self.thumbnail_image)
        return result


class FestDragonCERT(Enum):
    DOUBLE_DRAGON = "DOUBLE_DRAGON"
    DRAGON = "DRAGON"
    NONE = "NONE"


@dataclass
class Background:
    id: str
    text_color: Color
    image: Optional[SimpleImage] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Background':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        text_color = Color.from_dict(obj.get("textColor"))
        image = from_union([SimpleImage.from_dict, from_none], obj.get("image"))
        return Background(id, text_color, image)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["textColor"] = to_class(Color, self.text_color)
        if self.image is not None:
            result["image"] = from_union([lambda x: to_class(SimpleImage, x), from_none], self.image)
        return result


@dataclass
class Badge:
    typename: Any
    id: str
    image: SimpleImage
    description: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Badge':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        id = from_str(obj.get("id"))
        image = SimpleImage.from_dict(obj.get("image"))
        description = from_union([from_str, from_none], obj.get("description"))
        return Badge(typename, id, image, description)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        result["id"] = from_str(self.id)
        result["image"] = to_class(SimpleImage, self.image)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        return result


@dataclass
class Nameplate:
    background: Background
    badges: List[Optional[Badge]]

    @staticmethod
    def from_dict(obj: Any) -> 'Nameplate':
        assert isinstance(obj, dict)
        background = Background.from_dict(obj.get("background"))
        badges = from_list(lambda x: from_union([from_none, Badge.from_dict], x), obj.get("badges"))
        return Nameplate(background, badges)

    def to_dict(self) -> dict:
        result: dict = {}
        result["background"] = to_class(Background, self.background)
        result["badges"] = from_list(lambda x: from_union([from_none, lambda x: to_class(Badge, x)], x), self.badges)
        return result


@dataclass
class PlayerResult:
    assist: int
    death: int
    kill: int
    special: int
    noroshi_try: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'PlayerResult':
        assert isinstance(obj, dict)
        assist = from_int(obj.get("assist"))
        death = from_int(obj.get("death"))
        kill = from_int(obj.get("kill"))
        special = from_int(obj.get("special"))
        noroshi_try = from_union([from_int, from_none], obj.get("noroshiTry"))
        return PlayerResult(assist, death, kill, special, noroshi_try)

    def to_dict(self) -> dict:
        result: dict = {}
        result["assist"] = from_int(self.assist)
        result["death"] = from_int(self.death)
        result["kill"] = from_int(self.kill)
        result["special"] = from_int(self.special)
        result["noroshiTry"] = from_union([from_int, from_none], self.noroshi_try)
        return result


class Species(Enum):
    INKLING = "INKLING"
    OCTOLING = "OCTOLING"


@dataclass
class MaskingImage:
    """Like in `Image`, `maskImageUrl` and `overlayImageUrl` are optional."""
    height: int
    width: int
    mask_image_url: Optional[str] = None
    overlay_image_url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MaskingImage':
        assert isinstance(obj, dict)
        height = from_int(obj.get("height"))
        width = from_int(obj.get("width"))
        mask_image_url = from_union([from_str, from_none], obj.get("maskImageUrl"))
        overlay_image_url = from_union([from_str, from_none], obj.get("overlayImageUrl"))
        return MaskingImage(height, width, mask_image_url, overlay_image_url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["height"] = from_int(self.height)
        result["width"] = from_int(self.width)
        if self.mask_image_url is not None:
            result["maskImageUrl"] = from_union([from_str, from_none], self.mask_image_url)
        if self.overlay_image_url is not None:
            result["overlayImageUrl"] = from_union([from_str, from_none], self.overlay_image_url)
        return result


@dataclass
class SpecialWeapon:
    id: str
    image: SimpleImage
    """Like in `Image`, `maskImageUrl` and `overlayImageUrl` are optional."""
    masking_image: MaskingImage
    name: str
    special_weapon_id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SpecialWeapon':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        image = SimpleImage.from_dict(obj.get("image"))
        masking_image = MaskingImage.from_dict(obj.get("maskingImage"))
        name = from_str(obj.get("name"))
        special_weapon_id = from_union([from_int, from_none], obj.get("specialWeaponId"))
        return SpecialWeapon(id, image, masking_image, name, special_weapon_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["image"] = to_class(SimpleImage, self.image)
        result["maskingImage"] = to_class(MaskingImage, self.masking_image)
        result["name"] = from_str(self.name)
        if self.special_weapon_id is not None:
            result["specialWeaponId"] = from_union([from_int, from_none], self.special_weapon_id)
        return result


@dataclass
class SubWeapon:
    id: str
    image: SimpleImage
    name: str
    sub_weapon_id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SubWeapon':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        image = SimpleImage.from_dict(obj.get("image"))
        name = from_str(obj.get("name"))
        sub_weapon_id = from_union([from_int, from_none], obj.get("subWeaponId"))
        return SubWeapon(id, image, name, sub_weapon_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["image"] = to_class(SimpleImage, self.image)
        result["name"] = from_str(self.name)
        if self.sub_weapon_id is not None:
            result["subWeaponId"] = from_union([from_int, from_none], self.sub_weapon_id)
        return result


@dataclass
class Image:
    """The `url` is optional. See <wiki link> for details. TODO: write wiki page"""
    typename: Any
    height: int
    width: int
    url: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Image':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        height = from_int(obj.get("height"))
        width = from_int(obj.get("width"))
        url = from_union([from_str, from_none], obj.get("url"))
        return Image(typename, height, width, url)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        result["height"] = from_int(self.height)
        result["width"] = from_int(self.width)
        if self.url is not None:
            result["url"] = from_union([from_str, from_none], self.url)
        return result


@dataclass
class WeaponCategory:
    typename: Any
    category: str
    id: str
    image: Image
    name: str
    weapon_category_id: int

    @staticmethod
    def from_dict(obj: Any) -> 'WeaponCategory':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        category = from_str(obj.get("category"))
        id = from_str(obj.get("id"))
        image = Image.from_dict(obj.get("image"))
        name = from_str(obj.get("name"))
        weapon_category_id = from_int(obj.get("weaponCategoryId"))
        return WeaponCategory(typename, category, id, image, name, weapon_category_id)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        result["category"] = from_str(self.category)
        result["id"] = from_str(self.id)
        result["image"] = to_class(Image, self.image)
        result["name"] = from_str(self.name)
        result["weaponCategoryId"] = from_int(self.weapon_category_id)
        return result


@dataclass
class Weapon:
    typename: Any
    id: str
    image: SimpleImage
    name: str
    special_weapon: SpecialWeapon
    sub_weapon: SubWeapon
    weapon_category: Optional[WeaponCategory] = None
    weapon_id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Weapon':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        id = from_str(obj.get("id"))
        image = SimpleImage.from_dict(obj.get("image"))
        name = from_str(obj.get("name"))
        special_weapon = SpecialWeapon.from_dict(obj.get("specialWeapon"))
        sub_weapon = SubWeapon.from_dict(obj.get("subWeapon"))
        weapon_category = from_union([WeaponCategory.from_dict, from_none], obj.get("weaponCategory"))
        weapon_id = from_union([from_int, from_none], obj.get("weaponId"))
        return Weapon(typename, id, image, name, special_weapon, sub_weapon, weapon_category, weapon_id)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        result["id"] = from_str(self.id)
        result["image"] = to_class(SimpleImage, self.image)
        result["name"] = from_str(self.name)
        result["specialWeapon"] = to_class(SpecialWeapon, self.special_weapon)
        result["subWeapon"] = to_class(SubWeapon, self.sub_weapon)
        if self.weapon_category is not None:
            result["weaponCategory"] = from_union([lambda x: to_class(WeaponCategory, x), from_none],
                                                  self.weapon_category)
        if self.weapon_id is not None:
            result["weaponId"] = from_union([from_int, from_none], self.weapon_id)
        return result


@dataclass
class VsHistoryDetai:
    """The player object in VsHistoryDetail.player and the elements in team.players extend this"""
    is_player: Any
    crown: bool
    fest_dragon_cert: FestDragonCERT
    is_myself: bool
    species: Species
    weapon: Weapon
    byname: Optional[str] = None
    clothing_gear: Optional[BaseGear] = None
    head_gear: Optional[BaseGear] = None
    id: Optional[str] = None
    name: Optional[str] = None
    name_id: Optional[str] = None
    nameplate: Optional[Nameplate] = None
    paint: Optional[int] = None
    shoes_gear: Optional[BaseGear] = None
    fest_grade: Optional[str] = None
    result: Optional[PlayerResult] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VsHistoryDetai':
        assert isinstance(obj, dict)
        is_player = obj.get("__isPlayer")
        crown = from_bool(obj.get("crown"))
        fest_dragon_cert = FestDragonCERT(obj.get("festDragonCert"))
        is_myself = from_bool(obj.get("isMyself"))
        species = Species(obj.get("species"))
        weapon = Weapon.from_dict(obj.get("weapon"))
        byname = from_union([from_str, from_none], obj.get("byname"))
        clothing_gear = from_union([BaseGear.from_dict, from_none], obj.get("clothingGear"))
        head_gear = from_union([BaseGear.from_dict, from_none], obj.get("headGear"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        name_id = from_union([from_str, from_none], obj.get("nameId"))
        nameplate = from_union([Nameplate.from_dict, from_none], obj.get("nameplate"))
        paint = from_union([from_int, from_none], obj.get("paint"))
        shoes_gear = from_union([BaseGear.from_dict, from_none], obj.get("shoesGear"))
        fest_grade = from_union([from_none, from_str], obj.get("festGrade"))
        result = from_union([PlayerResult.from_dict, from_none], obj.get("result"))
        return VsHistoryDetai(is_player, crown, fest_dragon_cert, is_myself, species, weapon, byname, clothing_gear,
                              head_gear, id, name, name_id, nameplate, paint, shoes_gear, fest_grade, result)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.is_player is not None:
            result["__isPlayer"] = self.is_player
        result["crown"] = from_bool(self.crown)
        result["festDragonCert"] = to_enum(FestDragonCERT, self.fest_dragon_cert)
        result["isMyself"] = from_bool(self.is_myself)
        result["species"] = to_enum(Species, self.species)
        result["weapon"] = to_class(Weapon, self.weapon)
        if self.byname is not None:
            result["byname"] = from_union([from_str, from_none], self.byname)
        if self.clothing_gear is not None:
            result["clothingGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.clothing_gear)
        if self.head_gear is not None:
            result["headGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.head_gear)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.name_id is not None:
            result["nameId"] = from_union([from_str, from_none], self.name_id)
        if self.nameplate is not None:
            result["nameplate"] = from_union([lambda x: to_class(Nameplate, x), from_none], self.nameplate)
        if self.paint is not None:
            result["paint"] = from_union([from_int, from_none], self.paint)
        if self.shoes_gear is not None:
            result["shoesGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.shoes_gear)
        if self.fest_grade is not None:
            result["festGrade"] = from_union([from_none, from_str], self.fest_grade)
        result["result"] = from_union([lambda x: to_class(PlayerResult, x), from_none], self.result)
        return result


@dataclass
class MyTeamResult:
    noroshi: Optional[int] = None
    paint_ratio: Optional[float] = None
    score: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'MyTeamResult':
        assert isinstance(obj, dict)
        noroshi = from_union([from_int, from_none], obj.get("noroshi"))
        paint_ratio = from_union([from_float, from_none], obj.get("paintRatio"))
        score = from_union([from_int, from_none], obj.get("score"))
        return MyTeamResult(noroshi, paint_ratio, score)

    def to_dict(self) -> dict:
        result: dict = {}
        result["noroshi"] = from_union([from_int, from_none], self.noroshi)
        result["paintRatio"] = from_union([to_float, from_none], self.paint_ratio)
        result["score"] = from_union([from_int, from_none], self.score)
        return result


class TricolorRole(Enum):
    ATTACK1 = "ATTACK1"
    ATTACK2 = "ATTACK2"
    DEFENSE = "DEFENSE"


@dataclass
class Team:
    color: Color
    judgement: MyTeamJudgement
    order: int
    players: List[VsHistoryDetai]
    result: MyTeamResult
    fest_streak_win_count: Optional[int] = None
    fest_team_name: Optional[str] = None
    fest_uniform_bonus_rate: Optional[float] = None
    fest_uniform_name: Optional[str] = None
    tricolor_role: Optional[TricolorRole] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Team':
        assert isinstance(obj, dict)
        color = Color.from_dict(obj.get("color"))
        judgement = MyTeamJudgement(obj.get("judgement"))
        order = from_int(obj.get("order"))
        players = from_list(VsHistoryDetai.from_dict, obj.get("players"))
        result = MyTeamResult.from_dict(obj.get("result"))
        fest_streak_win_count = from_union([from_int, from_none], obj.get("festStreakWinCount"))
        fest_team_name = from_union([from_none, from_str], obj.get("festTeamName"))
        fest_uniform_bonus_rate = from_union([from_float, from_none], obj.get("festUniformBonusRate"))
        fest_uniform_name = from_union([from_none, from_str], obj.get("festUniformName"))
        tricolor_role = from_union([from_none, TricolorRole], obj.get("tricolorRole"))
        return Team(color, judgement, order, players, result, fest_streak_win_count, fest_team_name,
                    fest_uniform_bonus_rate, fest_uniform_name, tricolor_role)

    def to_dict(self) -> dict:
        result: dict = {}
        result["color"] = to_class(Color, self.color)
        result["judgement"] = to_enum(MyTeamJudgement, self.judgement)
        result["order"] = from_int(self.order)
        result["players"] = from_list(lambda x: to_class(VsHistoryDetai, x), self.players)
        result["result"] = to_class(MyTeamResult, self.result)
        if self.fest_streak_win_count is not None:
            result["festStreakWinCount"] = from_union([from_int, from_none], self.fest_streak_win_count)
        if self.fest_team_name is not None:
            result["festTeamName"] = from_union([from_none, from_str], self.fest_team_name)
        if self.fest_uniform_bonus_rate is not None:
            result["festUniformBonusRate"] = from_union([to_float, from_none], self.fest_uniform_bonus_rate)
        if self.fest_uniform_name is not None:
            result["festUniformName"] = from_union([from_none, from_str], self.fest_uniform_name)
        result["tricolorRole"] = from_union([from_none, lambda x: to_enum(TricolorRole, x)], self.tricolor_role)
        return result


@dataclass
class BasePlayer:
    """The player object in VsHistoryDetail.player and the elements in team.players extend this"""
    is_player: Any
    byname: Optional[str] = None
    clothing_gear: Optional[BaseGear] = None
    head_gear: Optional[BaseGear] = None
    id: Optional[str] = None
    name: Optional[str] = None
    name_id: Optional[str] = None
    nameplate: Optional[Nameplate] = None
    paint: Optional[int] = None
    shoes_gear: Optional[BaseGear] = None

    @staticmethod
    def from_dict(obj: Any) -> 'BasePlayer':
        assert isinstance(obj, dict)
        is_player = obj.get("__isPlayer")
        byname = from_union([from_str, from_none], obj.get("byname"))
        clothing_gear = from_union([BaseGear.from_dict, from_none], obj.get("clothingGear"))
        head_gear = from_union([BaseGear.from_dict, from_none], obj.get("headGear"))
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        name_id = from_union([from_str, from_none], obj.get("nameId"))
        nameplate = from_union([Nameplate.from_dict, from_none], obj.get("nameplate"))
        paint = from_union([from_int, from_none], obj.get("paint"))
        shoes_gear = from_union([BaseGear.from_dict, from_none], obj.get("shoesGear"))
        return BasePlayer(is_player, byname, clothing_gear, head_gear, id, name, name_id, nameplate, paint, shoes_gear)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.is_player is not None:
            result["__isPlayer"] = self.is_player
        if self.byname is not None:
            result["byname"] = from_union([from_str, from_none], self.byname)
        if self.clothing_gear is not None:
            result["clothingGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.clothing_gear)
        if self.head_gear is not None:
            result["headGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.head_gear)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.name_id is not None:
            result["nameId"] = from_union([from_str, from_none], self.name_id)
        if self.nameplate is not None:
            result["nameplate"] = from_union([lambda x: to_class(Nameplate, x), from_none], self.nameplate)
        if self.paint is not None:
            result["paint"] = from_union([from_int, from_none], self.paint)
        if self.shoes_gear is not None:
            result["shoesGear"] = from_union([lambda x: to_class(BaseGear, x), from_none], self.shoes_gear)
        return result


class Mode(Enum):
    BANKARA = "BANKARA"
    FEST = "FEST"
    REGULAR = "REGULAR"
    X_MATCH = "X_MATCH"


@dataclass
class VsMode:
    typename: Any
    id: Optional[str] = None
    mode: Optional[Mode] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VsMode':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        id = from_union([from_str, from_none], obj.get("id"))
        mode = from_union([Mode, from_none], obj.get("mode"))
        name = from_union([from_str, from_none], obj.get("name"))
        return VsMode(typename, id, mode, name)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.mode is not None:
            result["mode"] = from_union([lambda x: to_enum(Mode, x), from_none], self.mode)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


class Rule(Enum):
    AREA = "AREA"
    CLAM = "CLAM"
    GOAL = "GOAL"
    LOFT = "LOFT"
    TURF_WAR = "TURF_WAR"


@dataclass
class VsRule:
    typename: Any
    id: Optional[str] = None
    name: Optional[str] = None
    rule: Optional[Rule] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VsRule':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        rule = from_union([Rule, from_none], obj.get("rule"))
        return VsRule(typename, id, name, rule)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.rule is not None:
            result["rule"] = from_union([lambda x: to_enum(Rule, x), from_none], self.rule)
        return result


@dataclass
class VsStage:
    typename: Any
    id: Optional[str] = None
    image: Optional[SimpleImage] = None
    name: Optional[str] = None
    vs_stage_id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VsStage':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        id = from_union([from_str, from_none], obj.get("id"))
        image = from_union([SimpleImage.from_dict, from_none], obj.get("image"))
        name = from_union([from_str, from_none], obj.get("name"))
        vs_stage_id = from_union([from_int, from_none], obj.get("vsStageId"))
        return VsStage(typename, id, image, name, vs_stage_id)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.image is not None:
            result["image"] = from_union([lambda x: to_class(SimpleImage, x), from_none], self.image)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.vs_stage_id is not None:
            result["vsStageId"] = from_union([from_int, from_none], self.vs_stage_id)
        return result


@dataclass
class VsHistoryDetail:
    """A VsHistoryDetail from SplatNet 3"""
    typename: Any
    awards: List[Award]
    duration: int
    id: str
    judgement: VsHistoryDetailJudgement
    my_team: Team
    other_teams: List[Team]
    played_time: datetime
    """The player object in VsHistoryDetail.player and the elements in team.players extend this"""
    player: BasePlayer
    vs_mode: VsMode
    vs_rule: VsRule
    vs_stage: VsStage
    knockout: Optional[Knockout] = None

    @staticmethod
    def from_dict(obj: Any) -> 'VsHistoryDetail':
        assert isinstance(obj, dict)
        typename = obj.get("__typename")
        awards = from_list(Award.from_dict, obj.get("awards"))
        duration = from_int(obj.get("duration"))
        id = from_str(obj.get("id"))
        judgement = VsHistoryDetailJudgement(obj.get("judgement"))
        my_team = Team.from_dict(obj.get("myTeam"))
        other_teams = from_list(Team.from_dict, obj.get("otherTeams"))
        played_time = from_datetime(obj.get("playedTime"))
        player = BasePlayer.from_dict(obj.get("player"))
        vs_mode = VsMode.from_dict(obj.get("vsMode"))
        vs_rule = VsRule.from_dict(obj.get("vsRule"))
        vs_stage = VsStage.from_dict(obj.get("vsStage"))
        knockout = from_union([from_none, Knockout], obj.get("knockout"))
        return VsHistoryDetail(typename, awards, duration, id, judgement, my_team, other_teams, played_time, player,
                               vs_mode, vs_rule, vs_stage, knockout)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.typename is not None:
            result["__typename"] = self.typename
        result["awards"] = from_list(lambda x: to_class(Award, x), self.awards)
        result["duration"] = from_int(self.duration)
        result["id"] = from_str(self.id)
        result["judgement"] = to_enum(VsHistoryDetailJudgement, self.judgement)
        result["myTeam"] = to_class(Team, self.my_team)
        result["otherTeams"] = from_list(lambda x: to_class(Team, x), self.other_teams)
        result["playedTime"] = self.played_time.isoformat()
        result["player"] = to_class(BasePlayer, self.player)
        result["vsMode"] = to_class(VsMode, self.vs_mode)
        result["vsRule"] = to_class(VsRule, self.vs_rule)
        result["vsStage"] = to_class(VsStage, self.vs_stage)
        result["knockout"] = from_union([from_none, lambda x: to_enum(Knockout, x)], self.knockout)
        return result


def vs_history_detail_from_dict(s: Any) -> VsHistoryDetail:
    return VsHistoryDetail.from_dict(s)


def vs_history_detail_to_dict(x: VsHistoryDetail) -> Any:
    return to_class(VsHistoryDetail, x)
