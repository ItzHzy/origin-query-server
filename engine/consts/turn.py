from enum import Enum, auto

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
