from enum import Enum, auto

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
