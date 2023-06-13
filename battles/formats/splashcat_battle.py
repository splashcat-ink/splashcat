from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Any, List, TypeVar, Type, Callable, cast

import dateutil.parser

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


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


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


class AnarchyMode(Enum):
    OPEN = "OPEN"
    SERIES = "SERIES"


@dataclass
class Anarchy:
    mode: Optional[AnarchyMode] = None
    point_change: Optional[int] = None
    power: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Anarchy':
        assert isinstance(obj, dict)
        mode = from_union([AnarchyMode, from_none], obj.get("mode"))
        point_change = from_union([from_int, from_none], obj.get("pointChange"))
        power = from_union([from_int, from_none], obj.get("power"))
        return Anarchy(mode, point_change, power)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.mode is not None:
            result["mode"] = from_union([lambda x: to_enum(AnarchyMode, x), from_none], self.mode)
        if self.point_change is not None:
            result["pointChange"] = from_union([from_int, from_none], self.point_change)
        if self.power is not None:
            result["power"] = from_union([from_int, from_none], self.power)
        return result


@dataclass
class Challenge:
    id: Optional[str] = None
    power: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Challenge':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        power = from_union([from_int, from_none], obj.get("power"))
        return Challenge(id, power)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.power is not None:
            result["power"] = from_union([from_int, from_none], self.power)
        return result


class SplashcatBattleJudgement(Enum):
    DEEMED_LOSE = "DEEMED_LOSE"
    DRAW = "DRAW"
    EXEMPTED_LOSE = "EXEMPTED_LOSE"
    LOSE = "LOSE"
    WIN = "WIN"


class Knockout(Enum):
    LOSE = "LOSE"
    NEITHER = "NEITHER"
    WIN = "WIN"


class CloutMultiplier(Enum):
    DECUPLE = "DECUPLE"
    DOUBLE_DRAGON = "DOUBLE_DRAGON"
    DRAGON = "DRAGON"
    NONE = "NONE"


class SplatfestMode(Enum):
    OPEN = "OPEN"
    PRO = "PRO"


@dataclass
class Splatfest:
    clout_multiplier: Optional[CloutMultiplier] = None
    mode: Optional[SplatfestMode] = None
    power: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Splatfest':
        assert isinstance(obj, dict)
        clout_multiplier = from_union([CloutMultiplier, from_none], obj.get("cloutMultiplier"))
        mode = from_union([SplatfestMode, from_none], obj.get("mode"))
        power = from_union([from_int, from_none], obj.get("power"))
        return Splatfest(clout_multiplier, mode, power)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.clout_multiplier is not None:
            result["cloutMultiplier"] = from_union([lambda x: to_enum(CloutMultiplier, x), from_none],
                                                   self.clout_multiplier)
        if self.mode is not None:
            result["mode"] = from_union([lambda x: to_enum(SplatfestMode, x), from_none], self.mode)
        if self.power is not None:
            result["power"] = from_union([from_int, from_none], self.power)
        return result


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


class TeamJudgement(Enum):
    DRAW = "DRAW"
    LOSE = "LOSE"
    WIN = "WIN"


@dataclass
class Gear:
    """A piece of gear. Use en-US locale for name and all abilities."""
    name: Optional[str] = None
    primary_ability: Optional[str] = None
    secondary_abilities: Optional[List[str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Gear':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        primary_ability = from_union([from_str, from_none], obj.get("primaryAbility"))
        secondary_abilities = from_union([lambda x: from_list(from_str, x), from_none], obj.get("secondaryAbilities"))
        return Gear(name, primary_ability, secondary_abilities)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.primary_ability is not None:
            result["primaryAbility"] = from_union([from_str, from_none], self.primary_ability)
        if self.secondary_abilities is not None:
            result["secondaryAbilities"] = from_union([lambda x: from_list(from_str, x), from_none],
                                                      self.secondary_abilities)
        return result


class Species(Enum):
    INKLING = "INKLING"
    OCTOLING = "OCTOLING"


@dataclass
class Player:
    """Array of badge IDs. Use JSON `null` for empty slots."""
    badges: List[Optional[int]]
    clothing_gear: Gear
    disconnected: bool
    head_gear: Gear
    is_me: bool
    name: str
    name_id: str
    npln_id: str
    paint: int
    shoes_gear: Gear
    species: Species
    splashtag_background_id: int
    title: str
    weapon_id: int
    assists: Optional[int] = None
    deaths: Optional[int] = None
    """Should report the same way that SplatNet 3 does (kills + assists)"""
    kills: Optional[int] = None
    noroshi_try: Optional[int] = None
    specials: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        assert isinstance(obj, dict)
        badges = from_list(lambda x: from_union([from_int, from_none], x), obj.get("badges"))
        clothing_gear = Gear.from_dict(obj.get("clothingGear"))
        disconnected = from_bool(obj.get("disconnected"))
        head_gear = Gear.from_dict(obj.get("headGear"))
        is_me = from_bool(obj.get("isMe"))
        name = from_str(obj.get("name"))
        name_id = from_str(obj.get("nameId"))
        npln_id = from_str(obj.get("nplnId"))
        paint = from_int(obj.get("paint"))
        shoes_gear = Gear.from_dict(obj.get("shoesGear"))
        species = Species(obj.get("species"))
        splashtag_background_id = from_int(obj.get("splashtagBackgroundId"))
        title = from_str(obj.get("title"))
        weapon_id = from_int(obj.get("weaponId"))
        assists = from_union([from_int, from_none], obj.get("assists"))
        deaths = from_union([from_int, from_none], obj.get("deaths"))
        kills = from_union([from_int, from_none], obj.get("kills"))
        noroshi_try = from_union([from_int, from_none], obj.get("noroshiTry"))
        specials = from_union([from_int, from_none], obj.get("specials"))
        return Player(badges, clothing_gear, disconnected, head_gear, is_me, name, name_id, npln_id, paint, shoes_gear,
                      species, splashtag_background_id, title, weapon_id, assists, deaths, kills, noroshi_try, specials)

    def to_dict(self) -> dict:
        result: dict = {}
        result["badges"] = from_list(lambda x: from_union([from_int, from_none], x), self.badges)
        result["clothingGear"] = to_class(Gear, self.clothing_gear)
        result["disconnected"] = from_bool(self.disconnected)
        result["headGear"] = to_class(Gear, self.head_gear)
        result["isMe"] = from_bool(self.is_me)
        result["name"] = from_str(self.name)
        result["nameId"] = from_str(self.name_id)
        result["nplnId"] = from_str(self.npln_id)
        result["paint"] = from_int(self.paint)
        result["shoesGear"] = to_class(Gear, self.shoes_gear)
        result["species"] = to_enum(Species, self.species)
        result["splashtagBackgroundId"] = from_int(self.splashtag_background_id)
        result["title"] = from_str(self.title)
        result["weaponId"] = from_int(self.weapon_id)
        if self.assists is not None:
            result["assists"] = from_union([from_int, from_none], self.assists)
        if self.deaths is not None:
            result["deaths"] = from_union([from_int, from_none], self.deaths)
        if self.kills is not None:
            result["kills"] = from_union([from_int, from_none], self.kills)
        if self.noroshi_try is not None:
            result["noroshiTry"] = from_union([from_int, from_none], self.noroshi_try)
        if self.specials is not None:
            result["specials"] = from_union([from_int, from_none], self.specials)
        return result


class TricolorRole(Enum):
    ATTACK1 = "ATTACK1"
    ATTACK2 = "ATTACK2"
    DEFENSE = "DEFENSE"


@dataclass
class Team:
    color: Color
    is_my_team: bool
    order: int
    fest_streak_win_count: Optional[int] = None
    fest_team_name: Optional[str] = None
    fest_uniform_bonus_rate: Optional[float] = None
    fest_uniform_name: Optional[str] = None
    judgement: Optional[TeamJudgement] = None
    noroshi: Optional[int] = None
    paint_ratio: Optional[float] = None
    players: Optional[List[Player]] = None
    score: Optional[int] = None
    tricolor_role: Optional[TricolorRole] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Team':
        assert isinstance(obj, dict)
        color = Color.from_dict(obj.get("color"))
        is_my_team = from_bool(obj.get("isMyTeam"))
        order = from_int(obj.get("order"))
        fest_streak_win_count = from_union([from_int, from_none], obj.get("festStreakWinCount"))
        fest_team_name = from_union([from_str, from_none], obj.get("festTeamName"))
        fest_uniform_bonus_rate = from_union([from_float, from_none], obj.get("festUniformBonusRate"))
        fest_uniform_name = from_union([from_str, from_none], obj.get("festUniformName"))
        judgement = from_union([TeamJudgement, from_none], obj.get("judgement"))
        noroshi = from_union([from_int, from_none], obj.get("noroshi"))
        paint_ratio = from_union([from_float, from_none], obj.get("paintRatio"))
        players = from_union([lambda x: from_list(Player.from_dict, x), from_none], obj.get("players"))
        score = from_union([from_int, from_none], obj.get("score"))
        tricolor_role = from_union([TricolorRole, from_none], obj.get("tricolorRole"))
        return Team(color, is_my_team, order, fest_streak_win_count, fest_team_name, fest_uniform_bonus_rate,
                    fest_uniform_name, judgement, noroshi, paint_ratio, players, score, tricolor_role)

    def to_dict(self) -> dict:
        result: dict = {}
        result["color"] = to_class(Color, self.color)
        result["isMyTeam"] = from_bool(self.is_my_team)
        result["order"] = from_int(self.order)
        if self.fest_streak_win_count is not None:
            result["festStreakWinCount"] = from_union([from_int, from_none], self.fest_streak_win_count)
        if self.fest_team_name is not None:
            result["festTeamName"] = from_union([from_str, from_none], self.fest_team_name)
        if self.fest_uniform_bonus_rate is not None:
            result["festUniformBonusRate"] = from_union([to_float, from_none], self.fest_uniform_bonus_rate)
        if self.fest_uniform_name is not None:
            result["festUniformName"] = from_union([from_str, from_none], self.fest_uniform_name)
        if self.judgement is not None:
            result["judgement"] = from_union([lambda x: to_enum(TeamJudgement, x), from_none], self.judgement)
        if self.noroshi is not None:
            result["noroshi"] = from_union([from_int, from_none], self.noroshi)
        if self.paint_ratio is not None:
            result["paintRatio"] = from_union([to_float, from_none], self.paint_ratio)
        if self.players is not None:
            result["players"] = from_union([lambda x: from_list(lambda x: to_class(Player, x), x), from_none],
                                           self.players)
        if self.score is not None:
            result["score"] = from_union([from_int, from_none], self.score)
        if self.tricolor_role is not None:
            result["tricolorRole"] = from_union([lambda x: to_enum(TricolorRole, x), from_none], self.tricolor_role)
        return result


class VsMode(Enum):
    BANKARA = "BANKARA"
    CHALLENGE = "CHALLENGE"
    FEST = "FEST"
    PRIVATE = "PRIVATE"
    REGULAR = "REGULAR"
    X_MATCH = "X_MATCH"


class VsRule(Enum):
    AREA = "AREA"
    CLAM = "CLAM"
    GOAL = "GOAL"
    LOFT = "LOFT"
    TRI_COLOR = "TRI_COLOR"
    TURF_WAR = "TURF_WAR"


@dataclass
class XBattle:
    x_power: Optional[float] = None
    x_rank: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'XBattle':
        assert isinstance(obj, dict)
        x_power = from_union([from_float, from_none], obj.get("xPower"))
        x_rank = from_union([from_int, from_none], obj.get("xRank"))
        return XBattle(x_power, x_rank)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.x_power is not None:
            result["xPower"] = from_union([to_float, from_none], self.x_power)
        if self.x_rank is not None:
            result["xRank"] = from_union([from_int, from_none], self.x_rank)
        return result


@dataclass
class SplashcatBattle:
    """A battle to be uploaded to Splashcat. Any SplatNet 3 strings should use en-US locale.
    Splashcat will translate strings into the user's language.
    """
    """The en-US string for the award. Splashcat will translate this into the user's language
    and manage the award's rank.
    """
    awards: List[str]
    duration: int
    judgement: SplashcatBattleJudgement
    played_time: datetime
    """base64 decoded and split by `:` to get the last section"""
    splatnet_id: str
    teams: List[Team]
    vs_mode: VsMode
    vs_rule: VsRule
    vs_stage_id: int
    anarchy: Optional[Anarchy] = None
    challenge: Optional[Challenge] = None
    knockout: Optional[Knockout] = None
    splatfest: Optional[Splatfest] = None
    x_battle: Optional[XBattle] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SplashcatBattle':
        assert isinstance(obj, dict)
        awards = from_list(from_str, obj.get("awards"))
        duration = from_int(obj.get("duration"))
        judgement = SplashcatBattleJudgement(obj.get("judgement"))
        played_time = from_datetime(obj.get("playedTime"))
        splatnet_id = from_str(obj.get("splatnetId"))
        teams = from_list(Team.from_dict, obj.get("teams"))
        vs_mode = VsMode(obj.get("vsMode"))
        vs_rule = VsRule(obj.get("vsRule"))
        vs_stage_id = from_int(obj.get("vsStageId"))
        anarchy = from_union([Anarchy.from_dict, from_none], obj.get("anarchy"))
        challenge = from_union([Challenge.from_dict, from_none], obj.get("challenge"))
        knockout = from_union([Knockout, from_none], obj.get("knockout"))
        splatfest = from_union([Splatfest.from_dict, from_none], obj.get("splatfest"))
        x_battle = from_union([XBattle.from_dict, from_none], obj.get("xBattle"))
        return SplashcatBattle(awards, duration, judgement, played_time, splatnet_id, teams, vs_mode, vs_rule,
                               vs_stage_id, anarchy, challenge, knockout, splatfest, x_battle)

    def to_dict(self) -> dict:
        result: dict = {}
        result["awards"] = from_list(from_str, self.awards)
        result["duration"] = from_int(self.duration)
        result["judgement"] = to_enum(SplashcatBattleJudgement, self.judgement)
        result["playedTime"] = self.played_time.isoformat()
        result["splatnetId"] = from_str(self.splatnet_id)
        result["teams"] = from_list(lambda x: to_class(Team, x), self.teams)
        result["vsMode"] = to_enum(VsMode, self.vs_mode)
        result["vsRule"] = to_enum(VsRule, self.vs_rule)
        result["vsStageId"] = from_int(self.vs_stage_id)
        if self.anarchy is not None:
            result["anarchy"] = from_union([lambda x: to_class(Anarchy, x), from_none], self.anarchy)
        if self.challenge is not None:
            result["challenge"] = from_union([lambda x: to_class(Challenge, x), from_none], self.challenge)
        if self.knockout is not None:
            result["knockout"] = from_union([lambda x: to_enum(Knockout, x), from_none], self.knockout)
        if self.splatfest is not None:
            result["splatfest"] = from_union([lambda x: to_class(Splatfest, x), from_none], self.splatfest)
        if self.x_battle is not None:
            result["xBattle"] = from_union([lambda x: to_class(XBattle, x), from_none], self.x_battle)
        return result


def splashcat_battle_from_dict(s: Any) -> SplashcatBattle:
    return SplashcatBattle.from_dict(s)


def splashcat_battle_to_dict(x: SplashcatBattle) -> Any:
    return to_class(SplashcatBattle, x)
