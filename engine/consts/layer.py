from enum import Enum, auto

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
