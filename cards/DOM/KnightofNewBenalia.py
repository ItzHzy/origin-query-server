from enumeratedTypes import *
from combatFunctions import *
from gameElements import *
from gameActions import *


class KnightofNewBenalia(Card):
    def __init__(self, game, player, key):
        super(KnightofNewBenalia, self).__init__(game, player, key)

        self.manaCost = {ManaType.WHITE: 1, ManaType.GENERIC: 1}

        self.printed = {
            "name": "Knight of New Benalia",
            "power": 3,
            "toughness": 1,
            "abilities": [],
            "types": {Type.CREATURE, Subtype.HUMAN, Subtype.KNIGHT},
            "colors": {Color.WHITE}
        }

        self.update()
