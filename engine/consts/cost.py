from enum import Enum, auto

class CostType(Enum):
    NORMAL = auto()
    FLASHBACK = auto()
    OVERLOAD = auto()
    KICKER = auto()
    MULTIKICKER = auto()
