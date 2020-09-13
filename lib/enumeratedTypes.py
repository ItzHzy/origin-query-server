from enum import Enum, auto


class Status(Enum):
    ATTACKING = auto()
    DEFENDING = auto()


class GameRuleAns(Enum):
    ALLOWED = auto()
    DENIED = auto()
    UNKNOWN = auto()
    CONDITIONAL = auto()


class Placeholder(Enum):
    VARIABLE = auto()
    TARGET = auto()
    YOU = auto()
    OPPONENTS = auto()
    ALL_PLAYERS = auto()


class CostType(Enum):
    NORMAL = auto()
    FLASHBACK = auto()
    OVERLOAD = auto()
    KICKER = auto()
    MULTIKICKER = auto()


class Color(Enum):
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    COLORLESS = auto()


class ManaType(Enum):
    WHITE = auto()
    BLUE = auto()
    BLACK = auto()
    RED = auto()
    GREEN = auto()
    COLORLESS = auto()

    GENERIC = auto()
    VARIBLE = auto()  # Represents X
    SNOW = auto()

    # Hybrid Mana
    WU = auto()
    WB = auto()
    UB = auto()
    UR = auto()
    BR = auto()
    BG = auto()
    RG = auto()
    RW = auto()
    GW = auto()
    GU = auto()

    # Monocolored Hybrid Mana
    W2 = auto()
    U2 = auto()
    B2 = auto()
    R2 = auto()
    G2 = auto()

    # Phrexian Mana
    WP = auto()
    UP = auto()
    BP = auto()
    RP = auto()
    GP = auto()


class Layer:
    BASE = auto()  # (name, power, toughness, abilities, types, colors)
    ONE = auto()  # copy abilities (name, power, toughness, abilities, types, colors)
    TWO = auto()  # (controller)
    THREE = auto()  # Would be implemented for text-changes, but there's only 15 cards that do that and its not worth the overhead
    FOUR = auto()  # (addOrSet, types) Change card types True for add, false else
    FIVE = auto()  # (addOrSet, colors) Change card colors  True for add, false else
    SIX = auto()  # (addOrSet, abilities)   True for add, false else
    SIX_0 = auto()  # Used for the archetypes from BRN (Ability)
    SIX_A = auto()  # (power func, toughness func) CDA abilities
    SIX_B = auto()  # (power, toughness) abilities that set
    SIX_C = auto()  # (power delta, toughness delta) ex Giant Growth
    SIX_D = auto()  # P/T changes from counters
    SIX_E = auto()  # P/T switching


class Turn(Enum):
    EXTRA = auto()
    UNTAP = auto()
    UPKEEP = auto()
    DRAW = auto()
    FIRST_MAIN = auto()
    BEGIN_COMBAT = auto()
    DECLARE_ATTACKS = auto()
    DECLARE_BLOCKS = auto()
    FIRST_COMBAT_DAMAGE = auto()
    SECOND_COMBAT_DAMAGE = auto()
    END_COMBAT = auto()
    SECOND_MAIN = auto()
    BEGIN_END = auto()
    CLEANUP = auto()


class AbilityType(Enum):
    ACTIVATED = auto()
    TRIGGERED = auto()
    STATIC = auto()
    LOYALTY = auto()
    MANA = auto()


class Zone(Enum):
    DECK = auto()
    GRAVE = auto()
    FIELD = auto()
    HAND = auto()
    EXILE = auto()
    STACK = auto()
    COMMAND_ZONE = auto()


class Supertype(Enum):
    LEGENDARY = auto()
    SNOW = auto()
    BASIC = auto()


class Type(Enum):
    CREATURE = auto()
    INSTANT = auto()
    SORCERY = auto()
    ENCHANTMENT = auto()
    ARTIFACT = auto()
    LAND = auto()
    PLANESWALKER = auto()
    TRIBAL = auto()


class COD(Enum):
    HAVING_0_LIFE = auto()
    DREW_FROM_EMPTY_DECK = auto()
    POISON = auto()
    SBA = auto()


class Split(Enum):
    DFC = auto()
    AFTERMATH = auto()
    SPLIT = auto()
    FUSE = auto()
    FLIP = auto()
    ADVENTURE = auto()


class Counter(Enum):
    POISON = auto()
    LOYALTY = auto()
    LORE = auto()
    P1P1 = auto()
    M1M1 = auto()


class Keyword(Enum):
    DECLARE_VAR = auto()  # Not really a keyword ability, but it couldn't be by itself
    HASTE = auto()
    FIRST_STRIKE = auto()
    DOUBLE_STRIKE = auto()
    TRAMPLE = auto()
    PROWESS = auto()


class Subtype(Enum):
    ISLAND = auto()
    PLAINS = auto()
    MOUNTAIN = auto()
    FOREST = auto()
    SWAMP = auto()

    AURA = auto()
    SAGA = auto()
    EQUIPTMENT = auto()

    ARCHER = auto()

    GOBLIN = auto()
    SCOUT = auto()
    DEVIL = auto()
    HORROR = auto()
    KNIGHT = auto()
    HUMAN = auto()
    CONSTRUCT = auto()
