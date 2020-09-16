from enum import Enum, auto

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
