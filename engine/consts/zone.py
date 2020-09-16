from enum import Enum, auto

class Zone(Enum):
    DECK = auto()
    GRAVE = auto()
    FIELD = auto()
    HAND = auto()
    EXILE = auto()
    STACK = auto()
    COMMAND_ZONE = auto()
